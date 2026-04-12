<template>
  <div class="reports-page">
    <van-nav-bar title="报告中心" left-arrow fixed placeholder @click-left="$router.back()" />

    <van-tabs v-model:active="activeTab">
      <van-tab title="生成报告">
        <div class="generate-section">
          <van-cell-group inset>
            <van-field
              v-model="reportTypeText"
              is-link
              readonly
              label="报告类型"
              placeholder="选择类型"
              @click="showTypePicker = true"
            />
            <van-field
              v-model="dateRangeText"
              is-link
              readonly
              label="时间范围"
              placeholder="选择时间范围"
              @click="selectDateRange"
            />
            <van-field
              v-model="selectedTemplateName"
              is-link
              readonly
              label="使用模板"
              placeholder="选择模板"
              @click="showTemplatePicker = true"
            />
            <van-cell title="AI 润色">
              <template #right-icon>
                <van-switch v-model="generateForm.use_ai" size="20" />
              </template>
            </van-cell>
          </van-cell-group>

          <div class="generate-actions">
            <van-button
              type="primary"
              block
              @click="previewReport"
              :disabled="previewing"
            >
              {{ previewing ? (generateForm.use_ai ? 'AI润色中...' : '生成中...') : '预览报告' }}
            </van-button>
          </div>
        </div>
      </van-tab>

      <van-tab title="历史报告">
        <van-loading v-if="reportStore.loading" class="loading" />

        <div v-else-if="reportStore.reports.length === 0" class="empty-state">
          <van-empty description="暂无报告" />
        </div>

        <div v-else class="report-list">
          <van-swipe-cell v-for="report in reportStore.reports" :key="report.id">
            <div class="report-item" @click="viewReport(report)">
              <div class="report-type">
                <van-tag :type="getReportTypeColor(report.type)">
                  {{ getReportTypeName(report.type) }}
                </van-tag>
              </div>
              <div class="report-date">
                {{ report.start_date }} ~ {{ report.end_date }}
              </div>
              <div class="report-meta">
                <span>{{ formatTime(report.created_at) }}</span>
                <van-tag v-if="report.ai_enhanced_content" type="success" size="small">
                  AI润色
                </van-tag>
              </div>
            </div>
            <template #right>
              <van-button square type="danger" text="删除" @click="deleteReport(report.id)" />
            </template>
          </van-swipe-cell>
        </div>
      </van-tab>
    </van-tabs>

    <van-tabbar v-model="navTab" route fixed>
      <van-tabbar-item replace to="/" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item replace to="/todos" icon="todo-list-o">任务</van-tabbar-item>
      <van-tabbar-item replace to="/work-logs" icon="notes-o">日志</van-tabbar-item>
      <van-tabbar-item replace to="/reports" icon="chart-trending-o">报告</van-tabbar-item>
    </van-tabbar>

    <!-- Type Picker -->
    <van-popup v-model:show="showTypePicker" position="bottom">
      <van-picker
        :columns="reportTypes"
        @confirm="onTypeConfirm"
        @cancel="showTypePicker = false"
      />
    </van-popup>

    <!-- Date Picker for Daily -->
    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        v-model="selectedDate"
        title="选择日期"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <!-- Date Range Picker -->
    <van-calendar
      v-model:show="showDateRangePicker"
      type="range"
      @confirm="onDateRangeConfirm"
    />

    <!-- Template Picker -->
    <van-popup v-model:show="showTemplatePicker" position="bottom">
      <van-picker
        :columns="templateColumns"
        @confirm="onTemplateConfirm"
        @cancel="showTemplatePicker = false"
      />
    </van-popup>

    <!-- Style Picker for Presentation -->
    <van-popup v-model:show="showStylePicker" position="bottom">
      <van-picker
        title="选择演示风格"
        :columns="styleColumns"
        @confirm="onStyleConfirm"
        @cancel="showStylePicker = false"
      />
    </van-popup>

    <!-- Preview Popup -->
    <van-popup
      v-model:show="showPreview"
      position="bottom"
      round
      style="height: 90%"
      closeable
    >
      <div class="preview-popup">
        <div class="preview-header">
          <h3>报告预览</h3>
          <div v-if="reportStore.currentPreview?.ai_enhanced_content" class="version-tabs">
            <span
              class="version-tab"
              :class="{ active: previewTab === 0 }"
              @click="previewTab = 0"
            >原始版本</span>
            <span
              class="version-tab"
              :class="{ active: previewTab === 1 }"
              @click="previewTab = 1"
            >AI润色版</span>
          </div>
        </div>
        <div class="preview-content">
          <pre>{{ previewContent }}</pre>
        </div>
        <div class="preview-actions">
          <van-button type="primary" block @click="saveReport" :disabled="saving">
            {{ saving ? '保存中...' : '保存报告' }}
          </van-button>
          <van-button
            type="success"
            block
            plain
            @click="generatePresentation"
            :disabled="exportingPresentation"
            style="margin-top: 10px"
          >
            {{ exportingPresentation ? '生成中...' : '生成PPT' }}
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- View Report Popup -->
    <van-popup
      v-model:show="showViewReport"
      position="bottom"
      round
      style="height: 90%"
      closeable
    >
      <div class="preview-popup" v-if="viewingReport">
        <div class="preview-header">
          <h3>{{ getReportTypeName(viewingReport.type) }}</h3>
          <p>{{ viewingReport.start_date }} ~ {{ viewingReport.end_date }}</p>
          <div v-if="viewingReport.ai_enhanced_content" class="version-tabs">
            <span
              class="version-tab"
              :class="{ active: viewTab === 0 }"
              @click="viewTab = 0"
            >原始版本</span>
            <span
              class="version-tab"
              :class="{ active: viewTab === 1 }"
              @click="viewTab = 1"
            >AI润色版</span>
          </div>
        </div>
        <div class="preview-content">
          <pre>{{ viewTab === 0 ? viewingReport.raw_content : viewingReport.ai_enhanced_content }}</pre>
        </div>
        <div class="preview-actions">
          <div class="action-buttons">
            <van-button type="primary" @click="exportReport" :disabled="exporting">
              {{ exporting ? '导出中...' : '导出 Markdown' }}
            </van-button>
            <van-button
              type="success"
              @click="exportReportPresentation"
              :disabled="exportingPresentation"
            >
              {{ exportingPresentation ? '生成中...' : '生成PPT' }}
            </van-button>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import { useReportStore } from '@/stores/report'
import type { Report, ReportGenerate, PresentationStyles } from '@/api/reports'
import { reportApi } from '@/api/reports'

const reportStore = useReportStore()

const activeTab = ref(0)
const navTab = ref(3)
const previewTab = ref(0)
const viewTab = ref(0)
const showTypePicker = ref(false)
const showDatePicker = ref(false)
const showDateRangePicker = ref(false)
const showTemplatePicker = ref(false)
const showPreview = ref(false)
const showViewReport = ref(false)
const showStylePicker = ref(false)
const saving = ref(false)
const exporting = ref(false)
const exportingPresentation = ref(false)
const previewing = ref(false)
const viewingReport = ref<Report | null>(null)
const selectedDate = ref<string[]>([])
const presentationStyles = ref<PresentationStyles>({})
const selectedStyle = ref('modern-dark')

const generateForm = reactive<ReportGenerate>({
  type: 'daily',
  start_date: new Date().toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0],
  template_id: undefined,
  use_ai: false
})

const reportTypes = [
  { text: '日报', value: 'daily' },
  { text: '周报', value: 'weekly' },
  { text: '月报', value: 'monthly' },
  { text: '年度绩效', value: 'yearly' }
]

const reportTypeText = computed(() => {
  const type = reportTypes.find(t => t.value === generateForm.type)
  return type?.text || '日报'
})

const dateRangeText = computed(() => {
  if (generateForm.start_date === generateForm.end_date) {
    return generateForm.start_date
  }
  return `${generateForm.start_date} ~ ${generateForm.end_date}`
})

const selectedTemplateName = computed(() => {
  if (!generateForm.template_id) return '默认模板'
  const template = reportStore.templates.find(t => t.id === generateForm.template_id)
  return template?.name || '默认模板'
})

const templateColumns = computed(() => {
  const templates = reportStore.templates.filter(t => t.type === generateForm.type)
  return [
    { text: '默认模板', value: undefined },
    ...templates.map(t => ({ text: t.name, value: t.id }))
  ]
})

const styleColumns = computed(() => {
  return Object.entries(presentationStyles.value).map(([key, name]) => ({
    text: name,
    value: key
  }))
})

const previewContent = computed(() => {
  const preview = reportStore.currentPreview
  if (!preview) return ''
  if (previewTab.value === 0) return preview.raw_content
  return preview.ai_enhanced_content || preview.raw_content
})

function getReportTypeName(type: string): string {
  const names: Record<string, string> = {
    daily: '日报',
    weekly: '周报',
    monthly: '月报',
    yearly: '年度绩效'
  }
  return names[type] || type
}

function getReportTypeColor(type: string): 'primary' | 'success' | 'warning' | 'danger' {
  const colors: Record<string, 'primary' | 'success' | 'warning' | 'danger'> = {
    daily: 'primary',
    weekly: 'success',
    monthly: 'warning',
    yearly: 'danger'
  }
  return colors[type] || 'primary'
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function selectDateRange() {
  if (generateForm.type === 'daily') {
    showDatePicker.value = true
  } else {
    showDateRangePicker.value = true
  }
}

function onTypeConfirm({ selectedOptions }: { selectedOptions: { text: string; value: string }[] }) {
  generateForm.type = selectedOptions[0].value
  generateForm.template_id = undefined
  // Reset dates based on type
  const today = new Date()
  if (generateForm.type === 'daily') {
    generateForm.start_date = generateForm.end_date = today.toISOString().split('T')[0]
  } else if (generateForm.type === 'weekly') {
    const monday = new Date(today)
    monday.setDate(today.getDate() - today.getDay() + 1)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    generateForm.start_date = monday.toISOString().split('T')[0]
    generateForm.end_date = sunday.toISOString().split('T')[0]
  } else if (generateForm.type === 'monthly') {
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)
    generateForm.start_date = firstDay.toISOString().split('T')[0]
    generateForm.end_date = lastDay.toISOString().split('T')[0]
  } else if (generateForm.type === 'yearly') {
    generateForm.start_date = `${today.getFullYear()}-01-01`
    generateForm.end_date = `${today.getFullYear()}-12-31`
  }
  showTypePicker.value = false
  reportStore.fetchTemplates(generateForm.type)
}

function onDateConfirm({ selectedValues }: { selectedValues: string[] }) {
  const date = selectedValues.join('-')
  generateForm.start_date = date
  generateForm.end_date = date
  showDatePicker.value = false
}

function onDateRangeConfirm(dates: Date[]) {
  const [start, end] = dates
  generateForm.start_date = start.toISOString().split('T')[0]
  generateForm.end_date = end.toISOString().split('T')[0]
  showDateRangePicker.value = false
}

function onTemplateConfirm({ selectedOptions }: { selectedOptions: { text: string; value: number | undefined }[] }) {
  generateForm.template_id = selectedOptions[0].value
  showTemplatePicker.value = false
}

async function previewReport() {
  if (previewing.value) return
  previewing.value = true
  try {
    await reportStore.previewReport(generateForm)
    // AI润色时默认显示润色版本
    previewTab.value = generateForm.use_ai && reportStore.currentPreview?.ai_enhanced_content ? 1 : 0
    showPreview.value = true
  } finally {
    previewing.value = false
  }
}

async function saveReport() {
  saving.value = true
  try {
    await reportStore.generateReport(generateForm)
    showToast('保存成功')
    showPreview.value = false
    activeTab.value = 1
  } finally {
    saving.value = false
  }
}

function viewReport(report: Report) {
  viewingReport.value = report
  // 有AI润色版本时默认显示润色版
  viewTab.value = report.ai_enhanced_content ? 1 : 0
  showViewReport.value = true
}

async function exportReport() {
  if (!viewingReport.value || exporting.value) return
  exporting.value = true
  try {
    const useAi = viewTab.value === 1 && !!viewingReport.value.ai_enhanced_content
    const response = await reportApi.exportMarkdown(viewingReport.value.id, useAi)
    const blob = new Blob([response.data], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${viewingReport.value.type}_${viewingReport.value.start_date}.md`
    a.click()
    URL.revokeObjectURL(url)
    showToast('导出成功')
  } catch {
    // Error handled by interceptor
  } finally {
    exporting.value = false
  }
}

async function deleteReport(id: number) {
  await showConfirmDialog({
    title: '确认删除',
    message: '删除后无法恢复，确定删除吗？'
  })
  await reportStore.deleteReport(id)
  showToast('删除成功')
}

// 生成演示文稿（从预览）
async function generatePresentation() {
  if (exportingPresentation.value) return
  showStylePicker.value = true
}

// 导出已有报告为演示文稿
async function exportReportPresentation() {
  if (!viewingReport.value || exportingPresentation.value) return
  showStylePicker.value = true
}

// 确认风格后导出演示文稿
async function onStyleConfirm({ selectedOptions }: { selectedOptions: { text: string; value: string }[] }) {
  selectedStyle.value = selectedOptions[0].value
  showStylePicker.value = false
  exportingPresentation.value = true

  try {
    let response
    if (viewingReport.value) {
      // 导出已有报告
      response = await reportApi.exportPresentation(viewingReport.value.id, selectedStyle.value)
    } else {
      // 从预览生成
      response = await reportApi.generatePresentation({
        type: generateForm.type,
        start_date: generateForm.start_date,
        end_date: generateForm.end_date,
        style: selectedStyle.value
      })
    }

    const blob = new Blob([response.data], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const filename = viewingReport.value
      ? `presentation_${viewingReport.value.type}_${viewingReport.value.start_date}.html`
      : `presentation_${generateForm.type}_${generateForm.start_date}.html`
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
    showToast('演示文稿已生成')
  } catch {
    // Error handled by interceptor
  } finally {
    exportingPresentation.value = false
  }
}

onMounted(async () => {
  await reportStore.initDefaultTemplates()
  await reportStore.fetchTemplates()
  await reportStore.fetchReports()
  // 获取演示文稿风格
  try {
    const response = await reportApi.getPresentationStyles()
    presentationStyles.value = response.data
  } catch {
    // 默认风格
    presentationStyles.value = {
      'modern-dark': '现代深色',
      'clean-light': '简洁浅色',
      'warm-cream': '温暖奶油',
      'tech-cyber': '科技霓虹'
    }
  }
})
</script>

<style scoped>
.reports-page {
  height: 100vh;
  height: 100dvh;
  background: var(--bg-primary);
  padding-bottom: 50px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 生成区域 */
.generate-section {
  padding: 20px;
}

.generate-section :deep(.van-cell-group--inset) {
  border-radius: 10px;
}

.generate-section :deep(.van-switch--on) {
  background: var(--success);
}

.generate-actions {
  margin-top: 24px;
}

.generate-actions :deep(.van-button) {
  height: 50px;
  font-size: 17px;
}

.loading {
  text-align: center;
  padding: 60px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* 报告列表 */
.report-list {
  padding: 0 20px;
}

.reports-page :deep(.van-swipe-cell) {
  margin-bottom: 12px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.report-item {
  padding: 16px;
  background: var(--bg-secondary);
}

.report-type {
  margin-bottom: 8px;
}

.report-date {
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--text-primary);
}

.report-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-tertiary);
}

/* 预览弹窗 */
.preview-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: var(--bg-primary);
}

.preview-header {
  margin-bottom: 16px;
}

.preview-header h3 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
}

.preview-header p {
  color: var(--text-tertiary);
  font-size: 15px;
}

.version-tabs {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.version-tab {
  padding: 8px 16px;
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.version-tab.active {
  color: white;
  background: var(--primary);
  font-weight: 500;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 16px;
}

.preview-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
}

.preview-actions :deep(.van-button) {
  height: 50px;
  font-size: 17px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-buttons :deep(.van-button) {
  flex: 1;
}
</style>
