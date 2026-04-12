<template>
  <div class="templates-page">
    <van-nav-bar title="模板管理" left-arrow fixed placeholder @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="20" @click="showAddForm = true" />
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="activeType" @change="onTypeChange">
      <van-tab title="日报" name="daily" />
      <van-tab title="周报" name="weekly" />
      <van-tab title="月报" name="monthly" />
      <van-tab title="年报" name="yearly" />
    </van-tabs>

    <van-loading v-if="loading" class="loading" />

    <div v-else-if="filteredTemplates.length === 0" class="empty-state">
      <van-empty description="暂无模板">
        <van-button type="primary" size="small" @click="showAddForm = true">
          创建模板
        </van-button>
      </van-empty>
    </div>

    <div v-else class="template-list">
      <van-swipe-cell v-for="template in filteredTemplates" :key="template.id">
        <div class="template-item" @click="viewTemplate(template)">
          <div class="template-header">
            <span class="template-name">{{ template.name }}</span>
            <van-tag v-if="template.is_default" type="primary" size="small">默认</van-tag>
            <van-tag v-if="!template.user_id" type="success" size="small">系统</van-tag>
          </div>
          <div class="template-preview">
            {{ template.template_content.slice(0, 100) }}...
          </div>
        </div>
        <template #right>
          <van-button
            v-if="template.user_id"
            square
            type="primary"
            text="编辑"
            @click="editTemplate(template)"
          />
          <van-button
            v-if="template.user_id"
            square
            type="danger"
            text="删除"
            @click="deleteTemplate(template.id)"
          />
        </template>
      </van-swipe-cell>
    </div>

    <!-- Variable Reference -->
    <div class="variable-reference">
      <van-collapse v-model="showVariables">
        <van-collapse-item title="可用变量参考" name="1">
          <div class="variable-list">
            <div v-for="v in variables" :key="v.name" class="variable-item">
              <code v-text="v.name"></code>
              <span>{{ v.desc }}</span>
            </div>
          </div>
        </van-collapse-item>
      </van-collapse>
    </div>

    <!-- Add/Edit Form -->
    <van-popup v-model:show="showAddForm" position="bottom" round style="height: 90%">
      <div class="form-popup">
        <van-nav-bar
          :title="editingTemplate ? '编辑模板' : '新建模板'"
          left-text="取消"
          @click-left="closeForm"
        >
          <template #right>
            <span
              class="nav-save-btn"
              :class="{ disabled: savingTemplate }"
              @click="saveTemplate"
            >
              {{ savingTemplate ? '保存中...' : '保存' }}
            </span>
          </template>
        </van-nav-bar>
        <van-form ref="formRef" class="template-form">
          <van-cell-group inset>
            <van-field
              v-model="form.name"
              label="模板名称"
              placeholder="请输入模板名称"
              :rules="[{ required: true, message: '请输入名称' }]"
            />
            <van-field
              v-model="form.type"
              is-link
              readonly
              label="模板类型"
              placeholder="选择类型"
              @click="showTypePicker = true"
            />
            <van-cell title="设为默认">
              <template #right-icon>
                <van-switch v-model="form.is_default" size="20" />
              </template>
            </van-cell>
          </van-cell-group>

          <div class="content-editor">
            <div class="content-header">
              <h4>模板内容</h4>
              <span class="ai-btn" @click="showAIGenerator = true">✨ AI生成</span>
            </div>
            <van-field
              v-model="form.template_content"
              type="textarea"
              rows="15"
              placeholder="请输入模板内容，支持 Markdown 格式和变量占位符"
              :rules="[{ required: true, message: '请输入内容' }]"
            />
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- View Template -->
    <van-popup v-model:show="showViewTemplate" position="bottom" round style="height: 80%">
      <div class="view-popup" v-if="viewingTemplate">
        <div class="view-header">
          <h3>{{ viewingTemplate.name }}</h3>
          <van-tag v-if="viewingTemplate.is_default" type="primary">默认</van-tag>
        </div>
        <div class="view-content">
          <pre>{{ viewingTemplate.template_content }}</pre>
        </div>
      </div>
    </van-popup>

    <!-- Type Picker -->
    <van-popup v-model:show="showTypePicker" position="bottom">
      <van-picker
        :columns="typeOptions"
        @confirm="onFormTypeConfirm"
        @cancel="showTypePicker = false"
      />
    </van-popup>

    <!-- AI Generator -->
    <van-popup v-model:show="showAIGenerator" position="bottom" round style="height: 85%">
      <div class="ai-popup">
        <van-nav-bar
          title="AI 生成模板"
          left-text="取消"
          @click-left="showAIGenerator = false"
        >
          <template #right>
            <span
              class="generate-btn"
              :class="{ disabled: !aiInput.trim() || aiGenerating }"
              @click="generateWithAI"
            >
              {{ aiGenerating ? '生成中...' : '生成' }}
            </span>
          </template>
        </van-nav-bar>

        <div class="ai-content">
          <van-tabs v-model:active="aiMode" shrink>
            <van-tab title="描述需求" name="describe" />
            <van-tab title="转换内容" name="convert" />
          </van-tabs>

          <div class="ai-hint">
            <template v-if="aiMode === 'describe'">
              描述你想要的报告模板，AI 会自动生成包含变量占位符的模板。
            </template>
            <template v-else>
              粘贴你已有的报告内容，AI 会将其转换为可复用的模板。
            </template>
          </div>

          <van-field
            v-model="aiInput"
            type="textarea"
            :rows="12"
            :placeholder="aiMode === 'describe'
              ? '例如：我需要一个简洁的周报模板，包含本周完成的工作、遇到的问题、下周计划，突出工作成果...'
              : '粘贴你已有的报告内容，例如：\n\n# 2024年第10周工作周报\n\n## 本周完成\n1. 完成用户登录功能开发\n2. 修复了3个bug...'"
          />
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import { templateApi, type ReportTemplate, type TemplateCreate } from '@/api/templates'

const loading = ref(false)
const templates = ref<ReportTemplate[]>([])
const activeType = ref('daily')
const showAddForm = ref(false)
const showViewTemplate = ref(false)
const showTypePicker = ref(false)
const showVariables = ref<string[]>([])
const editingTemplate = ref<ReportTemplate | null>(null)
const viewingTemplate = ref<ReportTemplate | null>(null)

// AI 生成相关
const showAIGenerator = ref(false)
const aiMode = ref<'describe' | 'convert'>('describe')
const aiInput = ref('')
const aiGenerating = ref(false)
const savingTemplate = ref(false)

const form = reactive<TemplateCreate>({
  name: '',
  type: 'daily',
  template_content: '',
  is_default: false
})

const typeOptions = [
  { text: '日报', value: 'daily' },
  { text: '周报', value: 'weekly' },
  { text: '月报', value: 'monthly' },
  { text: '年报', value: 'yearly' }
]

const variables = [
  { name: '{{date_range}}', desc: '日期范围' },
  { name: '{{completed_tasks}}', desc: '已完成任务列表' },
  { name: '{{in_progress_tasks}}', desc: '进行中任务' },
  { name: '{{total_hours}}', desc: '工作时长统计' },
  { name: '{{completed_count}}', desc: '完成任务数' },
  { name: '{{category_stats}}', desc: '分类统计' },
  { name: '{{highlights}}', desc: '亮点/成果' },
  { name: '{{issues}}', desc: '问题/困难' },
  { name: '{{next_plans}}', desc: '下一步计划' }
]

const filteredTemplates = computed(() => {
  return templates.value.filter(t => t.type === activeType.value)
})

function resetForm() {
  form.name = ''
  form.type = activeType.value
  form.template_content = ''
  form.is_default = false
  editingTemplate.value = null
}

function closeForm() {
  showAddForm.value = false
  resetForm()
}

function viewTemplate(template: ReportTemplate) {
  viewingTemplate.value = template
  showViewTemplate.value = true
}

function editTemplate(template: ReportTemplate) {
  editingTemplate.value = template
  form.name = template.name
  form.type = template.type
  form.template_content = template.template_content
  form.is_default = template.is_default
  showAddForm.value = true
}

async function saveTemplate() {
  if (!form.name.trim() || !form.template_content.trim()) {
    showToast('请填写完整信息')
    return
  }
  if (savingTemplate.value) return

  savingTemplate.value = true
  try {
    if (editingTemplate.value) {
      await templateApi.update(editingTemplate.value.id, {
        name: form.name,
        template_content: form.template_content,
        is_default: form.is_default
      })
      showToast('更新成功')
    } else {
      await templateApi.create(form)
      showToast('创建成功')
    }
    closeForm()
    await fetchTemplates()
  } catch {
    // Error handled by interceptor
  } finally {
    savingTemplate.value = false
  }
}

async function deleteTemplate(id: number) {
  await showConfirmDialog({
    title: '确认删除',
    message: '删除后无法恢复，确定删除吗？'
  })
  await templateApi.delete(id)
  showToast('删除成功')
  await fetchTemplates()
}

function onTypeChange() {
  form.type = activeType.value
}

function onFormTypeConfirm({ selectedOptions }: { selectedOptions: { text: string; value: string }[] }) {
  form.type = selectedOptions[0].value
  showTypePicker.value = false
}

async function generateWithAI() {
  if (!aiInput.value.trim() || aiGenerating.value) {
    if (!aiInput.value.trim()) {
      showToast('请输入内容')
    }
    return
  }

  aiGenerating.value = true
  try {
    const response = await templateApi.generateWithAI({
      user_input: aiInput.value,
      template_type: form.type,
      mode: aiMode.value
    })
    form.template_content = response.data.template_content
    showAIGenerator.value = false
    aiInput.value = ''
    showToast('生成成功')
  } catch {
    showToast('生成失败，请检查AI服务配置')
  } finally {
    aiGenerating.value = false
  }
}

async function fetchTemplates() {
  loading.value = true
  try {
    const response = await templateApi.getAll()
    templates.value = response.data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await templateApi.initDefaults()
  await fetchTemplates()
})
</script>

<style scoped>
.templates-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.loading {
  text-align: center;
  padding: 60px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* 模板列表 */
.template-list {
  padding: 16px 20px;
}

.templates-page :deep(.van-swipe-cell) {
  margin-bottom: 12px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.template-item {
  padding: 16px;
  background: var(--bg-secondary);
}

.template-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.template-name {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.template-preview {
  font-size: 15px;
  color: var(--text-tertiary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 变量参考 */
.variable-reference {
  margin: 0 20px 20px;
}

.variable-reference :deep(.van-collapse-item) {
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.variable-reference :deep(.van-collapse-item__title) {
  font-weight: 600;
}

.variable-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.variable-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.variable-item code {
  background: rgba(0,122,255,0.1);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--primary);
  font-weight: 500;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
}

.variable-item span {
  font-size: 15px;
  color: var(--text-tertiary);
}

/* 表单弹窗 */
.form-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.template-form {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.template-form :deep(.van-cell-group--inset) {
  border-radius: 10px;
}

.template-form :deep(.van-switch--on) {
  background: var(--success);
}

.nav-save-btn {
  font-size: 15px;
  color: var(--primary);
  font-weight: 500;
}

.nav-save-btn.disabled {
  color: var(--text-tertiary);
  pointer-events: none;
}

.content-editor {
  margin-top: 20px;
}

.content-editor h4 {
  font-size: 15px;
  color: var(--text-tertiary);
  margin-bottom: 10px;
  font-weight: 600;
}

.content-editor :deep(.van-field) {
  background: var(--bg-secondary);
  border-radius: 10px;
}

.content-editor :deep(.van-field__control) {
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 14px;
  line-height: 1.6;
}

/* 查看弹窗 */
.view-popup {
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.view-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.view-header h3 {
  font-size: 22px;
  font-weight: 700;
}

.view-content {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 10px;
}

.view-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
}

/* 内容编辑器头部 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.content-header h4 {
  margin: 0;
}

.ai-btn {
  font-size: 14px;
  color: var(--primary);
  padding: 6px 12px;
  background: rgba(0,122,255,0.1);
  border-radius: 6px;
  cursor: pointer;
}

.generate-btn {
  font-size: 15px;
  color: var(--primary);
  font-weight: 500;
  padding: 8px 16px;
  cursor: pointer;
}

.generate-btn.disabled {
  color: var(--text-tertiary);
  pointer-events: none;
}

/* AI 生成弹窗 */
.ai-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.ai-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.ai-content :deep(.van-tabs__nav) {
  background: transparent;
}

.ai-content :deep(.van-tabs__wrap) {
  margin-bottom: 16px;
}

.ai-hint {
  font-size: 14px;
  color: var(--text-tertiary);
  line-height: 1.5;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(0,122,255,0.08);
  border-radius: 8px;
}

.ai-content :deep(.van-field) {
  background: var(--bg-secondary);
  border-radius: 10px;
}

.ai-content :deep(.van-field__control) {
  font-size: 15px;
  line-height: 1.6;
}
</style>
