<template>
  <div class="page">
    <div class="page-header">
      <el-button type="primary" @click="openDialog()">新增分類</el-button>
    </div>
    <el-table :data="categories" stripe>
      <el-table-column prop="name" label="名稱" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="order_index" label="排序" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">編輯</el-button>
          <el-popconfirm title="確認刪除?" @confirm="remove(row)">
            <template #reference>
              <el-button size="small" type="danger">刪除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '編輯分類' : '新增分類'" width="400px">
      <el-form :model="form" label-position="top">
        <el-form-item label="名稱">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.order_index" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">儲存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import api from '../services/api'

interface Category {
  id: number
  name: string
  description: string | null
  order_index: number | null
}

const categories = ref<Category[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref<number | null>(null)
const form = reactive({
  name: '',
  description: '',
  order_index: 0
})

const fetchCategories = async () => {
  const { data } = await api.get<Category[]>('/api/categories')
  categories.value = data
}

const openDialog = (category?: Category) => {
  dialogVisible.value = true
  if (category) {
    isEdit.value = true
    currentId.value = category.id
    form.name = category.name
    form.description = category.description || ''
    form.order_index = category.order_index ?? 0
  } else {
    isEdit.value = false
    currentId.value = null
    form.name = ''
    form.description = ''
    form.order_index = 0
  }
}

const save = async () => {
  const payload = {
    name: form.name,
    description: form.description,
    order_index: form.order_index
  }
  if (isEdit.value && currentId.value !== null) {
    await api.put(`/api/categories/${currentId.value}`, payload)
  } else {
    await api.post('/api/categories', payload)
  }
  dialogVisible.value = false
  fetchCategories()
}

const remove = async (category: Category) => {
  await api.delete(`/api/categories/${category.id}`)
  fetchCategories()
}

onMounted(fetchCategories)
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
</style>
