import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reportApi, type Report, type ReportGenerate, type ReportPreview } from '@/api/reports'
import { templateApi, type ReportTemplate } from '@/api/templates'

export const useReportStore = defineStore('report', () => {
  const reports = ref<Report[]>([])
  const templates = ref<ReportTemplate[]>([])
  const currentPreview = ref<ReportPreview | null>(null)
  const loading = ref(false)

  async function fetchReports(type?: string) {
    loading.value = true
    try {
      const response = await reportApi.getAll({ type })
      reports.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchTemplates(type?: string) {
    const response = await templateApi.getAll(type)
    templates.value = response.data
  }

  async function initDefaultTemplates() {
    await templateApi.initDefaults()
  }

  async function generateReport(data: ReportGenerate) {
    loading.value = true
    try {
      const response = await reportApi.generate(data)
      reports.value.unshift(response.data)
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function previewReport(data: ReportGenerate) {
    loading.value = true
    try {
      const response = await reportApi.preview(data)
      currentPreview.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function deleteReport(id: number) {
    await reportApi.delete(id)
    reports.value = reports.value.filter(r => r.id !== id)
  }

  return {
    reports,
    templates,
    currentPreview,
    loading,
    fetchReports,
    fetchTemplates,
    initDefaultTemplates,
    generateReport,
    previewReport,
    deleteReport
  }
})
