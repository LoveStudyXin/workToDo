/**
 * Todo Store 测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTodoStore } from './todo'

// Mock API
vi.mock('@/api/todos', () => ({
  todoApi: {
    getAll: vi.fn(),
    getToday: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn()
  }
}))

import { todoApi } from '@/api/todos'

// 测试数据
const mockTodos = [
  { id: 1, title: '任务1', status: 'pending', priority: 3, category: '开发', progress: 0 },
  { id: 2, title: '任务2', status: 'in_progress', priority: 4, category: '测试', progress: 50 }
]

describe('Todo Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('任务列表初始为空', () => {
      const store = useTodoStore()
      expect(store.todos).toEqual([])
      expect(store.todayTodos).toEqual([])
    })

    it('loading 初始为 false', () => {
      const store = useTodoStore()
      expect(store.loading).toBe(false)
    })
  })

  describe('获取任务列表', () => {
    it('fetchTodos 获取所有任务', async () => {
      vi.mocked(todoApi.getAll).mockResolvedValue({ data: mockTodos } as any)

      const store = useTodoStore()
      await store.fetchTodos()

      expect(store.todos).toEqual(mockTodos)
      expect(todoApi.getAll).toHaveBeenCalled()
    })

    it('fetchTodos 支持筛选条件', async () => {
      vi.mocked(todoApi.getAll).mockResolvedValue({ data: [mockTodos[0]] } as any)

      const store = useTodoStore()
      await store.fetchTodos({ status: 'pending' })

      expect(todoApi.getAll).toHaveBeenCalledWith({ status: 'pending' })
    })

    it('fetchTodayTodos 获取今日任务', async () => {
      vi.mocked(todoApi.getToday).mockResolvedValue({ data: mockTodos } as any)

      const store = useTodoStore()
      await store.fetchTodayTodos()

      expect(store.todayTodos).toEqual(mockTodos)
    })

    it('加载时 loading 为 true', async () => {
      let resolvePromise: any
      vi.mocked(todoApi.getAll).mockReturnValue(
        new Promise(resolve => { resolvePromise = resolve })
      )

      const store = useTodoStore()
      const promise = store.fetchTodos()

      expect(store.loading).toBe(true)

      resolvePromise({ data: mockTodos })
      await promise

      expect(store.loading).toBe(false)
    })
  })

  describe('创建任务', () => {
    it('createTodo 创建新任务并添加到列表', async () => {
      const newTodo = { id: 3, title: '新任务', status: 'pending', priority: 3, category: '其他', progress: 0 }
      vi.mocked(todoApi.create).mockResolvedValue({ data: newTodo } as any)

      const store = useTodoStore()
      const result = await store.createTodo({ title: '新任务', category: '其他' })

      expect(result).toEqual(newTodo)
      expect(store.todos[0]).toEqual(newTodo) // 新任务在列表开头
    })
  })

  describe('更新任务', () => {
    it('updateTodo 更新任务并同步列表', async () => {
      vi.mocked(todoApi.getAll).mockResolvedValue({ data: mockTodos } as any)
      const updatedTodo = { ...mockTodos[0], title: '更新后的标题', progress: 100 }
      vi.mocked(todoApi.update).mockResolvedValue({ data: updatedTodo } as any)

      const store = useTodoStore()
      await store.fetchTodos()
      await store.updateTodo(1, { title: '更新后的标题', progress: 100 })

      expect(store.todos[0].title).toBe('更新后的标题')
      expect(store.todos[0].progress).toBe(100)
    })
  })

  describe('删除任务', () => {
    it('deleteTodo 删除任务并从列表移除', async () => {
      vi.mocked(todoApi.getAll).mockResolvedValue({ data: mockTodos } as any)
      vi.mocked(todoApi.delete).mockResolvedValue({} as any)

      const store = useTodoStore()
      await store.fetchTodos()
      expect(store.todos.length).toBe(2)

      await store.deleteTodo(1)

      expect(store.todos.length).toBe(1)
      expect(store.todos.find(t => t.id === 1)).toBeUndefined()
    })
  })
})
