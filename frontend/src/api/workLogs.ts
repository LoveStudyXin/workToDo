import api from './index'

export interface WorkLog {
  id: number
  date: string
  todo_id: number | null
  content: string
  hours_spent: number
  progress_update: number | null
  notes: string | null
  created_at: string
  todo?: {
    id: number
    title: string
  }
}

export interface WorkLogCreate {
  date: string
  todo_id?: number
  content: string
  hours_spent?: number
  progress_update?: number
  notes?: string
}

export interface WorkLogUpdate {
  date?: string
  todo_id?: number
  content?: string
  hours_spent?: number
  progress_update?: number
  notes?: string
}

export interface WorkLogFilters {
  start_date?: string
  end_date?: string
  todo_id?: number
}

export const workLogApi = {
  getAll: (filters?: WorkLogFilters) => {
    return api.get<WorkLog[]>('/work-logs', { params: filters })
  },

  getToday: () => {
    return api.get<WorkLog[]>('/work-logs/today')
  },

  getById: (id: number) => {
    return api.get<WorkLog>(`/work-logs/${id}`)
  },

  create: (data: WorkLogCreate) => {
    return api.post<WorkLog>('/work-logs', data)
  },

  update: (id: number, data: WorkLogUpdate) => {
    return api.put<WorkLog>(`/work-logs/${id}`, data)
  },

  delete: (id: number) => {
    return api.delete(`/work-logs/${id}`)
  }
}
