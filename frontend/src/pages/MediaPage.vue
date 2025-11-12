<template>
  <div class="page">
    <div class="page-header">
      <el-upload
        class="upload-box"
        :auto-upload="false"
        :show-file-list="false"
        drag
        accept="image/*"
        :before-upload="beforeUpload"
        :on-change="handleUploadChange"
      >
        <div class="el-upload__text">拖拉或點擊上傳圖片（單張 ≤ 500KB）</div>
      </el-upload>
      <el-input v-model="search" placeholder="搜尋檔名" class="search" @keyup.enter.native="fetchMedia" />
      <el-button type="primary" @click="fetchMedia">重新整理</el-button>
    </div>
    <el-table :data="media" v-loading="loading" stripe>
      <el-table-column label="預覽" width="120">
        <template #default="{ row }">
          <img :src="resolveUrl(row.url)" alt="preview" class="thumb" />
        </template>
      </el-table-column>
      <el-table-column prop="filename" label="檔名" />
      <el-table-column label="大小" width="120">
        <template #default="{ row }">{{ formatSize(row.size) }}</template>
      </el-table-column>
      <el-table-column label="引用次數" width="120">
        <template #default="{ row }">
          <el-tag :type="row.usage_count ? 'warning' : 'success'">{{ row.usage_count }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="上傳時間" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="copyUrl(row.url)">複製連結</el-button>
          <el-popconfirm
            v-if="row.usage_count === 0"
            title="確認刪除圖片?"
            @confirm="deleteMedia(row)"
          >
            <template #reference>
              <el-button size="small" type="danger">刪除</el-button>
            </template>
          </el-popconfirm>
          <el-tooltip v-else content="此圖片仍被文章引用，無法刪除">
            <span>
              <el-button size="small" type="danger" disabled>刪除</el-button>
            </span>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'

import api from '../services/api'

interface MediaItem {
  id: string
  filename: string
  original_filename?: string | null
  url: string
  content_type: string
  size: number
  usage_count: number
  created_at: string
}

const media = ref<MediaItem[]>([])
const loading = ref(false)
const search = ref('')
const backendBase = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace(/\/$/, '')

const fetchMedia = async () => {
  loading.value = true
  try {
    const { data } = await api.get<MediaItem[]>('/api/media', {
      params: { search: search.value || undefined }
    })
    media.value = data
  } finally {
    loading.value = false
  }
}

const beforeUpload = (file: File) => {
  if (file.size > 500 * 1024) {
    ElMessage.error('檔案過大，請小於 500KB')
    return false
  }
  return true
}

const handleUploadChange = async (uploadFile: UploadFile) => {
  if (!uploadFile.raw) return
  if (!beforeUpload(uploadFile.raw)) return
  const formData = new FormData()
  formData.append('file', uploadFile.raw)
  try {
    await api.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('圖片已上傳')
    fetchMedia()
  } catch (err: any) {
    const detail = err?.response?.data?.detail || '上傳失敗'
    ElMessage.error(detail)
  }
}

const deleteMedia = async (row: MediaItem) => {
  try {
    await api.delete(`/api/media/${row.id}`)
    ElMessage.success('已刪除')
    fetchMedia()
  } catch (err: any) {
    const detail = err?.response?.data?.detail || '刪除失敗'
    ElMessage.error(detail)
  }
}

const copyUrl = async (url: string) => {
  try {
    await navigator.clipboard.writeText(resolveUrl(url))
    ElMessage.success('已複製 URL')
  } catch {
    ElMessage.error('複製失敗')
  }
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

const formatTime = (value: string) => new Date(value).toLocaleString()

onMounted(fetchMedia)
</script>

<style scoped>
.page {
  padding: 16px;
}
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.upload-box {
  border: 1px dashed #cbd5f5;
}
.search {
  width: 240px;
}
.thumb {
  width: 96px;
  height: 64px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
</style>
