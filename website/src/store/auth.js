import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api, { setAuthToken } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  if (token.value) {
    setAuthToken(token.value)
  }

  const isAuthenticated = computed(() => Boolean(token.value))
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isMember = computed(() => user.value?.role === 'member' || isAdmin.value)

  const login = async (email, password) => {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post('/api/auth/login', {
        email,
        password,
        device_id: crypto.randomUUID(),
        device_info: navigator.userAgent
      })
      token.value = data.access_token
      localStorage.setItem('token', token.value)
      setAuthToken(token.value)
      await fetchProfile()
    } catch (err) {
      error.value = err.response?.data?.detail || '登入失敗'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProfile = async () => {
    if (!token.value) return
    try {
      const { data } = await api.get('/api/auth/me')
      user.value = data
    } catch (err) {
      console.error('Failed to fetch profile:', err)
      logout()
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    setAuthToken(null)
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isMember,
    login,
    logout,
    fetchProfile
  }
})
