/**
 * Auth Store 测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from './auth'

// Mock API
vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn()
  }
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn()
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

import { authApi } from '@/api/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  describe('初始状态', () => {
    it('用户初始为空', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
    })

    it('未登录时 isAuthenticated 为 false', () => {
      const store = useAuthStore()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('登录功能', () => {
    it('登录成功后保存 token', async () => {
      const mockToken = 'test-token-123'
      vi.mocked(authApi.login).mockResolvedValue({
        data: { access_token: mockToken, token_type: 'bearer' }
      } as any)
      vi.mocked(authApi.getCurrentUser).mockResolvedValue({
        data: { id: 1, username: 'testuser', email: 'test@example.com' }
      } as any)

      const store = useAuthStore()
      await store.login({ username: 'testuser', password: 'password123' })

      expect(store.token).toBe(mockToken)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', mockToken)
    })

    it('登录成功后获取用户信息', async () => {
      const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' }
      vi.mocked(authApi.login).mockResolvedValue({
        data: { access_token: 'token', token_type: 'bearer' }
      } as any)
      vi.mocked(authApi.getCurrentUser).mockResolvedValue({
        data: mockUser
      } as any)

      const store = useAuthStore()
      await store.login({ username: 'testuser', password: 'password123' })

      expect(store.user).toEqual(mockUser)
      expect(store.isAuthenticated).toBe(true)
    })
  })

  describe('注册功能', () => {
    it('注册调用正确的 API', async () => {
      vi.mocked(authApi.register).mockResolvedValue({ data: {} } as any)

      const store = useAuthStore()
      const registerData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      }
      await store.register(registerData)

      expect(authApi.register).toHaveBeenCalledWith(registerData)
    })
  })

  describe('登出功能', () => {
    it('登出后清除用户信息和 token', async () => {
      // 先模拟登录状态
      vi.mocked(authApi.login).mockResolvedValue({
        data: { access_token: 'token', token_type: 'bearer' }
      } as any)
      vi.mocked(authApi.getCurrentUser).mockResolvedValue({
        data: { id: 1, username: 'testuser', email: 'test@example.com' }
      } as any)

      const store = useAuthStore()
      await store.login({ username: 'testuser', password: 'password123' })

      // 登出
      store.logout()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
    })
  })
})
