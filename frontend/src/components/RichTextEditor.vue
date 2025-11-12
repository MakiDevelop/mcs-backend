<template>
  <div class="editor">
    <div class="toolbar">
      <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
        <el-button size="small" :loading="uploading">插入圖片</el-button>
        <div class="upload-tip">拖拉或點擊上傳 (≦ 500KB)</div>
      </div>
      <el-button size="small" @click="openMediaDialog">媒體庫</el-button>
      <el-switch
        v-model="isMarkdown"
        size="small"
        active-text="Markdown"
        inactive-text="WYSIWYG"
        @change="handleModeChange"
      />
    </div>
    <input ref="fileInput" type="file" accept="image/*" hidden @change="handleFileChange" />
    <div v-if="isMarkdown" class="markdown-mode">
      <el-input v-model="markdownText" type="textarea" :rows="12" placeholder="在此輸入 Markdown..." />
    </div>
    <Ckeditor
      v-else
      v-model="editorHtml"
      :editor="ClassicEditor"
      :config="editorConfig"
      class="ckeditor"
      @ready="handleEditorReady"
    />
    <el-dialog
      v-model="mediaDialogVisible"
      title="媒體庫"
      width="720px"
      append-to-body
      destroy-on-close
      @open="fetchMedia"
      @closed="handleMediaDialogClosed"
    >
      <div class="media-grid" v-loading="mediaLoading">
        <div v-for="item in mediaItems" :key="item.id" class="media-card">
          <img :src="resolveUrl(item.url)" :alt="item.filename" />
          <div class="media-name">{{ item.filename }}</div>
          <div class="media-meta">
            <span>{{ formatSize(item.size) }}</span>
            <el-tag :type="item.usage_count ? 'warning' : 'success'">{{ item.usage_count }} 用途</el-tag>
          </div>
          <el-button size="small" @click="selectExistingMedia(item)">插入</el-button>
        </div>
        <div v-if="!mediaItems.length && !mediaLoading" class="empty">尚無媒體檔案，請先上傳。</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, shallowRef, watch } from 'vue'
import { ElMessage } from 'element-plus'
import CKEditor from '@ckeditor/ckeditor5-vue'
import ClassicEditor from '@ckeditor/ckeditor5-build-classic'
import MarkdownIt from 'markdown-it'
import TurndownService from 'turndown'
import api from '../services/api'

const Ckeditor = CKEditor.component

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const uploading = ref(false)
const mediaDialogVisible = ref(false)
const mediaLoading = ref(false)
const mediaItems = ref<MediaItem[]>([])
const backendBase = (import.meta.env.VITE_API_BASE || window.location.origin).replace(/\/$/, '')

const isMarkdown = ref(false)
const markdownText = ref('')
const lastSyncedHtml = ref(props.modelValue || '<p></p>')
const editorHtml = ref(lastSyncedHtml.value)
const editorInstance = shallowRef<any>(null)

const markdownParser = new MarkdownIt({ html: true, linkify: true })
const turndown = new TurndownService({ headingStyle: 'atx' })
const editorConfig = computed(() => ({
  toolbar: [
    'heading',
    '|',
    'bold',
    'italic',
    'link',
    'bulletedList',
    'numberedList',
    'blockQuote',
    'codeBlock',
    'insertImage',
    '|',
    'undo',
    'redo',
  ],
}))

interface MediaItem {
  id: string
  filename: string
  url: string
  size: number
  usage_count: number
}

const handleEditorReady = (editor: any) => {
  editorInstance.value = editor
}

const syncMarkdownFromHtml = (html: string) => {
  markdownText.value = turndown.turndown(html || '<p></p>')
}

const syncHtmlFromMarkdown = () => {
  const html = markdownParser.render(markdownText.value || '')
  const nextHtml = html || '<p></p>'
  lastSyncedHtml.value = nextHtml
  editorHtml.value = nextHtml
  emit('update:modelValue', nextHtml)
}

const handleModeChange = (value: boolean | string | number) => {
  const enabled = Boolean(value)
  if (enabled) {
    syncMarkdownFromHtml(lastSyncedHtml.value)
  } else {
    syncHtmlFromMarkdown()
  }
  isMarkdown.value = enabled
}

watch(
  () => props.modelValue,
  (value) => {
    const nextHtml = value || '<p></p>'
    if (nextHtml === lastSyncedHtml.value) return
    lastSyncedHtml.value = nextHtml
    editorHtml.value = nextHtml
    if (isMarkdown.value) {
      syncMarkdownFromHtml(nextHtml)
    }
  },
)

watch(
  editorHtml,
  (value) => {
    if (isMarkdown.value) return
    const nextHtml = value || '<p></p>'
    if (nextHtml === lastSyncedHtml.value) return
    lastSyncedHtml.value = nextHtml
    emit('update:modelValue', nextHtml)
  },
)

watch(
  markdownText,
  () => {
    if (!isMarkdown.value) return
    syncHtmlFromMarkdown()
  },
)

const fileInput = ref<HTMLInputElement | null>(null)
const triggerFileInput = () => fileInput.value?.click()

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  await processFile(file)
  if (target) target.value = ''
}

const handleDrop = async (event: DragEvent) => {
  const file = event.dataTransfer?.files?.[0]
  await processFile(file)
}

const processFile = async (file?: File) => {
  if (!file) return
  if (file.size > 500 * 1024) {
    ElMessage.error('檔案過大，請小於 500KB')
    return
  }
  await uploadImageFile(file)
}

const insertImageToEditor = (url: string) => {
  if (isMarkdown.value) {
    markdownText.value = `${markdownText.value}\n![image](${url})\n`
    return
  }
  const editor = editorInstance.value
  if (!editor) return
  editor.model.change((writer: any) => {
    const imageElement = writer.createElement('imageBlock', { src: url })
    editor.model.insertContent(imageElement, editor.model.document.selection)
  })
}

const uploadImageFile = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  uploading.value = true
  try {
    const { data } = await api.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const url = resolveUrl(data.url)
    insertImageToEditor(url)
    ElMessage.success('圖片已插入')
  } catch (err: any) {
    const detail = err?.response?.data?.detail || '上傳失敗'
    ElMessage.error(detail)
  } finally {
    uploading.value = false
  }
}

const openMediaDialog = () => {
  mediaDialogVisible.value = true
}

const fetchMedia = async () => {
  mediaLoading.value = true
  try {
    const { data } = await api.get<MediaItem[]>('/api/media')
    mediaItems.value = data
  } catch (err: any) {
    const detail = err?.response?.data?.detail || '載入媒體失敗'
    ElMessage.error(detail)
  } finally {
    mediaLoading.value = false
  }
}

const handleMediaDialogClosed = () => {
  mediaItems.value = []
  mediaLoading.value = false
}

const selectExistingMedia = (item: MediaItem) => {
  const url = resolveUrl(item.url)
  insertImageToEditor(url)
  mediaDialogVisible.value = false
  ElMessage.success('已插入媒體')
}

const resolveUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${backendBase}${url}`
}

const formatSize = (size: number) => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<style scoped>
.editor {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.toolbar {
  border-bottom: 1px solid #e5e7eb;
  padding: 12px;
  display: flex;
  justify-content: flex-start;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px dashed #cbd5f5;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.upload-tip {
  font-size: 12px;
  color: #94a3b8;
}
.markdown-mode {
  padding: 12px;
}
.ckeditor {
  width: 90%;
  margin: 0 auto;
}
.ckeditor :deep(.ck-editor__editable) {
  min-height: 240px;
  max-height: 520px;
  overflow-y: auto;
}
.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}
.media-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.media-card img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 6px;
}
.media-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
}
.empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #94a3b8;
}
</style>
