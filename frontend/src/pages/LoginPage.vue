<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>後台登入</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" @submit.prevent>
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" placeholder="admin@example.com" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="form.password" show-password type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="authStore.loading" @click="submit">登入</el-button>
        </el-form-item>
        <el-alert v-if="authStore.error" type="error" :closable="false" :title="authStore.error" />
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const form = reactive({
  email: '',
  password: ''
})

const rules: FormRules = {
  email: [{ required: true, message: '請輸入 Email', trigger: 'blur' }],
  password: [{ required: true, message: '請輸入密碼', trigger: 'blur' }]
}

const submit = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    await authStore.login({ email: form.email, password: form.password })
    router.push((route.query.redirect as string) || '/')
  } catch (err) {
    console.error(err)
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(120deg, #1f3b73, #274060);
}
.login-card {
  width: 360px;
}
</style>
