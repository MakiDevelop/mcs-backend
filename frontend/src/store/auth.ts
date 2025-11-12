import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import api, { setAuthToken } from '../services/api'

interface LoginPayload {
  email: string
  password: string
  device_id: string
  device_info?: string
}

interface AuthUser {
  id: string
  name: string
  email: string
  role: string
}

const getDeviceId = () => {
  const key = 'mcs_device_id'
  let value = localStorage.getItem(key)
  if (!value) {
    value = crypto.randomUUID()
    localStorage.setItem(key, value)
  }
  return value
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('mcs_token'))
  const user = ref<AuthUser | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  if (token.value) {
    setAuthToken(token.value)
  }

  const isAuthenticated = computed(() => Boolean(token.value))

  const login = async (payload: Omit<LoginPayload, 'device_id'>) => {
    loading.value = true
    error.value = null
    try {
      const deviceId = getDeviceId()
      const { data } = await api.post('/api/auth/login', {
        ...payload,
        device_id: deviceId,
        device_info: navigator.userAgent
      })
      token.value = data.access_token
      localStorage.setItem('mcs_token', token.value)
      setAuthToken(token.value)
      await fetchProfile()
    } catch (err: any) {
      error.value = err?.response?.data?.detail || '登入失敗'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProfile = async () => {
    if (!token.value) return
    const { data } = await api.get('/api/auth/me')
    user.value = data
  }

  const logout = async () => {
    try {
      await api.post('/api/auth/logout')
    } catch (err) {
      console.warn('logout failed', err)
    }
    token.value = null
    user.value = null
    localStorage.removeItem('mcs_token')
    setAuthToken(null)
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    fetchProfile
  }
})
