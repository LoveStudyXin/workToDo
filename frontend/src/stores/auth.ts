import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type User, type LoginForm, type RegisterForm } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(form: LoginForm) {
    const response = await authApi.login(form)
    token.value = response.data.access_token
    localStorage.setItem('token', response.data.access_token)
    await fetchCurrentUser()
  }

  async function register(form: RegisterForm) {
    await authApi.register(form)
  }

  async function fetchCurrentUser() {
    if (!token.value) return
    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    fetchCurrentUser,
    logout
  }
})
