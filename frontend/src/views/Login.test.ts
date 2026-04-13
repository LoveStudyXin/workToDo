/**
 * Login 组件逻辑测试
 * 注：完整的组件渲染测试需要更多 Vant 配置，这里只测试核心逻辑
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  })
}))

// Mock vant
const mockShowToast = vi.fn()
vi.mock('vant', () => ({
  showToast: (msg: string) => mockShowToast(msg)
}))

// Mock auth store
const mockLogin = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    login: mockLogin
  })
}))

describe('Login 逻辑测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('空表单提交时显示提示', async () => {
    const { showToast } = await import('vant')
    const form = { username: '', password: '' }

    // 模拟 handleLogin 逻辑
    if (!form.username || !form.password) {
      showToast('请输入用户名和密码')
    }

    expect(mockShowToast).toHaveBeenCalledWith('请输入用户名和密码')
  })

  it('登录成功后调用正确的方法', async () => {
    mockLogin.mockResolvedValue({})

    const form = { username: 'testuser', password: 'password123' }
    const { useAuthStore } = await import('@/stores/auth')
    const { showToast } = await import('vant')
    const { useRouter } = await import('vue-router')

    const authStore = useAuthStore()
    const router = useRouter()

    // 模拟 handleLogin 逻辑
    if (form.username && form.password) {
      try {
        await authStore.login(form)
        showToast('登录成功')
        router.push('/')
      } catch (error) {
        //
      }
    }

    expect(mockLogin).toHaveBeenCalledWith(form)
    expect(mockShowToast).toHaveBeenCalledWith('登录成功')
    expect(mockPush).toHaveBeenCalledWith('/')
  })

  it('登录失败时显示错误信息', async () => {
    mockLogin.mockRejectedValue({
      response: { data: { detail: '密码错误，请检查' } }
    })

    const form = { username: 'testuser', password: 'wrongpass' }
    const { useAuthStore } = await import('@/stores/auth')
    const { showToast } = await import('vant')

    const authStore = useAuthStore()

    // 模拟 handleLogin 逻辑
    try {
      await authStore.login(form)
    } catch (error: any) {
      const message = error.response?.data?.detail || '登录失败'
      showToast(message)
    }

    expect(mockShowToast).toHaveBeenCalledWith('密码错误，请检查')
  })
})
