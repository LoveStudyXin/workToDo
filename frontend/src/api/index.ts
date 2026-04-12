import axios, { AxiosError } from 'axios'
import { showToast } from 'vant'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError<{ detail: string }>) => {
    const message = error.response?.data?.detail || '请求失败'

    // 401 且不在登录页时，跳转到登录页
    if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
      localStorage.removeItem('token')
      showToast(message)
      setTimeout(() => {
        window.location.href = '/login'
      }, 1000)
      return Promise.reject(error)
    }

    showToast(message)
    return Promise.reject(error)
  }
)

export default api
