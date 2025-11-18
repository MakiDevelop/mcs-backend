<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1 class="login-title">會員登入</h1>
          <p class="login-subtitle">登入以查看完整內容</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email">電子郵件</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="請輸入電子郵件"
              required
              :disabled="authStore.loading"
            />
          </div>

          <div class="form-group">
            <label for="password">密碼</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="請輸入密碼"
              required
              :disabled="authStore.loading"
            />
          </div>

          <div v-if="authStore.error" class="error-message">
            {{ authStore.error }}
          </div>

          <button
            type="submit"
            class="btn btn-primary btn-block"
            :disabled="authStore.loading"
          >
            {{ authStore.loading ? '登入中...' : '登入' }}
          </button>
        </form>

        <div class="login-footer">
          <p class="demo-hint">
            測試帳號：<br>
            <code>admin@test.com</code> / <code>admin123</code>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')

const handleLogin = async () => {
  try {
    await authStore.login(email.value, password.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    // 錯誤已在 store 中處理
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 440px;
}

.login-card {
  background: var(--color-bg);
  border-radius: var(--border-radius);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  padding: 48px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 16px;
  color: var(--color-text-secondary);
}

.login-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.form-group input {
  width: 100%;
}

.error-message {
  background: #FEE;
  color: var(--color-danger);
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  text-align: center;
}

.btn-block {
  width: 100%;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid var(--color-border);
}

.demo-hint {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.demo-hint code {
  background: var(--color-bg-secondary);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Courier New', monospace;
  color: var(--color-primary);
}

@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
  }

  .login-title {
    font-size: 24px;
  }
}
</style>
