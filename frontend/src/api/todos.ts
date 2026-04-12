import api from './index'

export interface Todo {
  id: number
  title: string
  description: string | null
  category: string
  priority: number
  status: string
  estimated_hours: number | null
  actual_hours: number | null
  progress: number
  due_date: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface TodoCreate {
  title: string
  description?: string
  category?: string
  priority?: number
  estimated_hours?: number
  due_date?: string
}

export interface TodoUpdate {
  title?: string
  description?: string
  category?: string
  priority?: number
  status?: string
  estimated_hours?: number
  actual_hours?: number
  progress?: number
  due_date?: string
}

export interface TodoFilters {
  status?: string
  category?: string
  priority?: number
  due_date?: string
}

export const todoApi = {
  getAll: (filters?: TodoFilters) => {
    return api.get<Todo[]>('/todos', { params: filters })
  },

  getToday: () => {
    return api.get<Todo[]>('/todos/today')
  },

  getById: (id: number) => {
    return api.get<Todo>(`/todos/${id}`)
  },

  create: (data: TodoCreate) => {
    return api.post<Todo>('/todos', data)
  },

  update: (id: number, data: TodoUpdate) => {
    return api.put<Todo>(`/todos/${id}`, data)
  },

  delete: (id: number) => {
    return api.delete(`/todos/${id}`)
  }
}
