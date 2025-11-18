import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000'
})

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

// 響應攔截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 過期，清除並跳轉登入
      localStorage.removeItem('token')
      setAuthToken(null)
      if (window.location.pathname !== '/login') {
        window.location.href = '/login?redirect=' + window.location.pathname
      }
    }
    return Promise.reject(error)
  }
)

export default api
