<template>
  <div class="page">
    <div class="page-header">
      <el-button type="primary" @click="openDialog()">新增內容</el-button>
    </div>
    <el-table :data="contents" stripe>
      <el-table-column prop="title" label="標題" />
      <el-table-column prop="slug" label="Slug" />
      <el-table-column prop="status" label="狀態" />
      <el-table-column prop="updated_at" label="更新時間">
        <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column width="200" label="操作">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">編輯</el-button>
          <el-popconfirm title="確認下架?" @confirm="archiveContent(row)">
            <template #reference>
              <el-button size="small" type="danger">下架</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '編輯內容' : '新增內容'" width="780px">
      <el-form :model="form" label-position="top">
        <el-form-item label="標題">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="Slug">
          <el-input
            v-model="form.slug"
            placeholder="URL 友善的識別，例如 premium-guide"
            @input="slugTouched = true"
          />
          <small class="help-text">Slug 會用在前台 URL，例如 /contents/slug-name</small>
        </el-form-item>
        <el-form-item label="分類">
          <el-select v-model="form.category_id" placeholder="選擇分類" style="width: 100%">
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="狀態">
          <el-select v-model="form.status">
            <el-option label="草稿" value="draft" />
            <el-option label="發佈" value="published" />
            <el-option label="下架" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="Hashtags">
          <el-select
            v-model="form.tags"
            multiple
            filterable
            allow-create
            default-first-option
            collapse-tags
            placeholder="輸入 #hashtag 並按 Enter"
            @change="normalizeTags"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="內容">
          <RichTextEditor v-model="form.body" />
        </el-form-item>
        <el-form-item label="SEO 標題 (選填)">
          <el-input v-model="form.meta_title" maxlength="60" show-word-limit />
        </el-form-item>
        <el-form-item label="SEO 描述 (選填)">
          <el-input v-model="form.meta_description" maxlength="160" show-word-limit type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveContent">儲存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { pinyin } from 'pinyin-pro'

import RichTextEditor from '../components/RichTextEditor.vue'
import api from '../services/api'

interface ContentItem {
  id: number
  title: string
  slug: string
  status: string
  category_id: number | null
  body: string
  meta_title?: string | null
  meta_description?: string | null
  cover_image_url?: string | null
  tags?: string | null
  updated_at: string
}

interface Category {
  id: number
  name: string
}

const contents = ref<ContentItem[]>([])
const categories = ref<Category[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref<number | null>(null)
const slugTouched = ref(false)
const form = reactive({
  title: '',
  slug: '',
  category_id: null as number | null,
  body: '',
  status: 'draft',
  tags: [] as string[],
  meta_title: '',
  meta_description: ''
})

const fetchContents = async () => {
  const { data } = await api.get<ContentItem[]>('/api/contents')
  contents.value = data
}

const fetchCategories = async () => {
  const { data } = await api.get<Category[]>('/api/categories')
  categories.value = data
}

const normalizeTags = (values: string[]) => {
  form.tags = values.map((tag) => {
    const trimmed = tag.trim()
    if (!trimmed) return ''
    return trimmed.startsWith('#') ? trimmed : `#${trimmed}`
  }).filter(Boolean)
}

const openDialog = (item?: ContentItem) => {
  dialogVisible.value = true
  if (item) {
    isEdit.value = true
    currentId.value = item.id
    form.title = item.title
    form.slug = item.slug
    form.category_id = item.category_id
    form.body = item.body
    form.status = item.status
    form.cover_image_url = item.cover_image_url || ''
    form.meta_title = item.meta_title || ''
    form.meta_description = item.meta_description || ''
    form.tags = item.tags ? item.tags.split(',').map((tag) => tag.trim()).filter(Boolean) : []
    normalizeTags([...form.tags])
    slugTouched.value = true
  } else {
    isEdit.value = false
    currentId.value = null
    form.title = ''
    form.slug = ''
    form.category_id = null
    form.body = ''
    form.status = 'draft'
    form.tags = []
    form.meta_title = ''
    form.meta_description = ''
    slugTouched.value = false
  }
}

const saveContent = async () => {
  const payload = {
    title: form.title,
    slug: form.slug,
    category_id: form.category_id,
    body: form.body,
    status: form.status,
    tags: form.tags.length ? form.tags.join(',') : null,
    cover_image_url: getFirstImageUrl(form.body),
    meta_title: form.meta_title || null,
    meta_description: form.meta_description || null
  }

  if (isEdit.value && currentId.value !== null) {
    await api.put(`/api/contents/${currentId.value}`, payload)
  } else {
    await api.post('/api/contents', payload)
  }
  dialogVisible.value = false
  fetchContents()
}

const archiveContent = async (item: ContentItem) => {
  await api.delete(`/api/contents/${item.id}`)
  fetchContents()
}

const formatTime = (value: string) => new Date(value).toLocaleString()

const getFirstImageUrl = (html: string) => {
  if (!html) return null
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const image = doc.querySelector('img')
    return image?.getAttribute('src') || null
  } catch {
    const match = html.match(/<img[^>]+src=["']([^"']+)["']/i)
    return match ? match[1] : null
  }
}

watch(
  () => form.title,
  (value) => {
    if (slugTouched.value || !value) return
    form.slug = slugifyTitle(value)
  },
)

const slugifyTitle = (value: string) => {
  const transliterated = pinyin(value, { toneType: 'none', type: 'array' }).join(' ')
  const base = transliterated || value
  return base
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

onMounted(() => {
  fetchContents()
  fetchCategories()
})
</script>

<style scoped>
.page {
  padding: 16px;
}
.page-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}
.help-text {
  display: block;
  margin-top: 4px;
  color: #94a3b8;
  font-size: 12px;
}
.cover-preview {
  margin-top: 8px;
  border: 1px solid #e2e8f0;
  padding: 8px;
  border-radius: 6px;
  background: #f8fafc;
}
.cover-preview img {
  max-width: 100%;
  border-radius: 4px;
}
</style>
