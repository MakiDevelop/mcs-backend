<template>
  <div class="page">
    <div class="page-header">
      <el-button type="primary" @click="openDialog()">新增會員</el-button>
    </div>
    <el-table :data="members" stripe>
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="email" label="Email" />
      <el-table-column prop="role" label="角色" />
      <el-table-column prop="is_active" label="狀態">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'warning'">{{ row.is_active ? '啟用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">編輯</el-button>
          <el-popconfirm title="確認停用?" @confirm="disableMember(row)">
            <template #reference>
              <el-button size="small" type="danger">停用</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '編輯會員' : '新增會員'" width="400px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role">
            <el-option label="Admin" value="admin" />
            <el-option label="Member" value="member" />
          </el-select>
        </el-form-item>
        <el-form-item label="密碼" prop="password">
          <el-input v-model="form.password" :disabled="isEdit" type="password" placeholder="至少 8 碼" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveMember">儲存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

import api from '../services/api'

interface Member {
  id: string
  name: string
  email: string
  role: string
  is_active: boolean
}

const members = ref<Member[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref<string | null>(null)
const formRef = ref<FormInstance>()
const saving = ref(false)
const form = reactive({
  name: '',
  email: '',
  password: '',
  role: 'member'
})

const rules: FormRules = {
  name: [{ required: true, message: '請輸入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '請輸入 Email', trigger: 'blur' },
    { type: 'email', message: 'Email 格式不正確', trigger: 'blur' }
  ],
  role: [{ required: true, message: '請選擇角色', trigger: 'change' }],
  password: [
    {
      validator: (_rule, value, callback) => {
        if (isEdit.value) return callback()
        if (!value) return callback(new Error('請輸入密碼'))
        if (value.length < 8) return callback(new Error('密碼至少 8 碼'))
        return callback()
      },
      trigger: 'blur'
    }
  ]
}

const fetchMembers = async () => {
  const { data } = await api.get<Member[]>('/api/members')
  members.value = data
}

const openDialog = (member?: Member) => {
  dialogVisible.value = true
  formRef.value?.clearValidate()
  if (member) {
    isEdit.value = true
    currentId.value = member.id
    form.name = member.name
    form.email = member.email
    form.role = member.role
    form.password = ''
  } else {
    isEdit.value = false
    currentId.value = null
    form.name = ''
    form.email = ''
    form.role = 'member'
    form.password = ''
  }
}

const saveMember = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value && currentId.value) {
      const payload: Record<string, unknown> = {
        name: form.name,
        role: form.role
      }
      if (form.password) {
        payload.password = form.password
      }
      await api.put(`/api/members/${currentId.value}`, payload)
    } else {
      await api.post('/api/members', {
        name: form.name,
        email: form.email,
        role: form.role,
        password: form.password
      })
    }
    ElMessage.success('儲存成功')
    dialogVisible.value = false
    fetchMembers()
  } catch (err: any) {
    const detail = err?.response?.data?.detail || '儲存失敗'
    ElMessage.error(detail)
  } finally {
    saving.value = false
  }
}

const disableMember = async (member: Member) => {
  await api.delete(`/api/members/${member.id}`)
  fetchMembers()
}

onMounted(() => {
  fetchMembers()
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
</style>
