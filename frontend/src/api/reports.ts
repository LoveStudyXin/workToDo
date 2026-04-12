import api from './index'

export interface Report {
  id: number
  type: string
  start_date: string
  end_date: string
  raw_content: string
  ai_enhanced_content: string | null
  created_at: string
}

export interface ReportGenerate {
  type: string
  start_date: string
  end_date: string
  template_id?: number
  use_ai?: boolean
}

export interface ReportPreview {
  raw_content: string
  ai_enhanced_content: string | null
}

export interface ReportFilters {
  type?: string
  start_date?: string
  end_date?: string
}

export interface PresentationGenerate {
  type: string
  start_date: string
  end_date: string
  style?: string
  title?: string
}

export interface PresentationStyles {
  [key: string]: string
}

export const reportApi = {
  generate: (data: ReportGenerate) => {
    return api.post<Report>('/reports/generate', data)
  },

  preview: (data: ReportGenerate) => {
    return api.post<ReportPreview>('/reports/preview', data)
  },

  getAll: (filters?: ReportFilters) => {
    return api.get<Report[]>('/reports', { params: filters })
  },

  getById: (id: number) => {
    return api.get<Report>(`/reports/${id}`)
  },

  exportMarkdown: (id: number, useAi: boolean = false) => {
    return api.get(`/reports/${id}/export/markdown`, {
      params: { use_ai: useAi },
      responseType: 'blob'
    })
  },

  delete: (id: number) => {
    return api.delete(`/reports/${id}`)
  },

  // 演示文稿相关
  getPresentationStyles: () => {
    return api.get<PresentationStyles>('/reports/presentation/styles')
  },

  generatePresentation: (data: PresentationGenerate) => {
    return api.post('/reports/presentation/generate', data, {
      responseType: 'blob'
    })
  },

  exportPresentation: (id: number, style: string = 'modern-dark') => {
    return api.get(`/reports/${id}/export/presentation`, {
      params: { style },
      responseType: 'blob'
    })
  }
}
