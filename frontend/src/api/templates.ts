import api from './index'

export interface ReportTemplate {
  id: number
  user_id: number | null
  name: string
  type: string
  template_content: string
  is_default: boolean
  created_at: string
}

export interface TemplateCreate {
  name: string
  type: string
  template_content: string
  is_default?: boolean
}

export interface TemplateUpdate {
  name?: string
  template_content?: string
  is_default?: boolean
}

export interface AIGenerateRequest {
  user_input: string
  template_type: string
  mode: 'describe' | 'convert'
}

export const templateApi = {
  initDefaults: () => {
    return api.post('/templates/init-defaults')
  },

  getAll: (type?: string) => {
    return api.get<ReportTemplate[]>('/templates', { params: { type } })
  },

  getById: (id: number) => {
    return api.get<ReportTemplate>(`/templates/${id}`)
  },

  create: (data: TemplateCreate) => {
    return api.post<ReportTemplate>('/templates', data)
  },

  update: (id: number, data: TemplateUpdate) => {
    return api.put<ReportTemplate>(`/templates/${id}`, data)
  },

  delete: (id: number) => {
    return api.delete(`/templates/${id}`)
  },

  generateWithAI: (data: AIGenerateRequest) => {
    return api.post<{ template_content: string }>('/templates/generate-ai', data)
  }
}
