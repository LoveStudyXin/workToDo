<template>
  <div class="worklog-page">
    <van-nav-bar title="工作日志" left-arrow fixed placeholder @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="20" @click="showAddForm = true" />
      </template>
    </van-nav-bar>

    <div class="date-filter">
      <van-field
        v-model="dateRange"
        is-link
        readonly
        label="日期范围"
        placeholder="选择日期范围"
        @click="showDatePicker = true"
      />
    </div>

    <van-pull-refresh v-model="refreshing" @refresh="handleRefresh">
      <van-loading v-if="loading && !refreshing" class="loading" />

      <div v-else-if="workLogs.length === 0" class="empty-state">
        <van-empty description="暂无日志">
          <van-button type="primary" size="small" @click="showAddForm = true">
            添加日志
          </van-button>
        </van-empty>
      </div>

      <div v-else class="log-list">
        <van-swipe-cell v-for="log in workLogs" :key="log.id">
          <div class="log-item" @click="editLog(log)">
            <div class="log-date">{{ log.date }}</div>
            <div class="log-content">{{ log.content }}</div>
            <div class="log-meta">
              <van-tag v-if="log.todo" type="primary" size="small">
                {{ log.todo.title }}
              </van-tag>
              <span class="hours">{{ log.hours_spent }}h</span>
              <span v-if="log.progress_update !== null" class="progress">
                进度: {{ log.progress_update }}%
              </span>
            </div>
            <div v-if="log.notes" class="log-notes">
              <van-icon name="warning-o" size="12" />
              {{ log.notes }}
            </div>
          </div>
          <template #right>
            <van-button square type="danger" text="删除" @click="deleteLog(log.id)" />
          </template>
        </van-swipe-cell>
      </div>
    </van-pull-refresh>

    <van-tabbar v-model="activeTab" route fixed>
      <van-tabbar-item replace to="/" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item replace to="/todos" icon="todo-list-o">任务</van-tabbar-item>
      <van-tabbar-item replace to="/work-logs" icon="notes-o">日志</van-tabbar-item>
      <van-tabbar-item replace to="/reports" icon="chart-trending-o">报告</van-tabbar-item>
    </van-tabbar>

    <!-- Add/Edit Form -->
    <van-popup v-model:show="showAddForm" position="bottom" round style="height: 80%">
      <div class="form-popup">
        <van-nav-bar
          :title="editingLog ? '编辑日志' : '新建日志'"
          left-text="取消"
          @click-left="closeForm"
        >
          <template #right>
            <span class="nav-save-btn" :class="{ disabled: savingLog }" @click="saveLog">
              {{ savingLog ? '保存中...' : '保存' }}
            </span>
          </template>
        </van-nav-bar>
        <van-form ref="formRef">
          <van-cell-group inset>
            <van-field
              v-model="form.date"
              is-link
              readonly
              label="日期"
              placeholder="选择日期"
              @click="showFormDatePicker = true"
            />
            <van-field
              v-model="selectedTodoTitle"
              is-link
              readonly
              label="关联任务"
              placeholder="选择任务（可选）"
              @click="showTodoPicker = true"
            />
            <van-field
              v-model="form.content"
              label="工作内容"
              type="textarea"
              rows="3"
              placeholder="请描述工作内容"
              :rules="[{ required: true, message: '请输入工作内容' }]"
            />
            <van-field
              v-model="form.hours_spent"
              label="工作时长"
              type="number"
              placeholder="小时"
            />
            <van-field v-if="form.todo_id" label="进度更新">
              <template #input>
                <div class="progress-selector">
                  <span
                    v-for="p in [0, 25, 50, 75, 100]"
                    :key="p"
                    class="progress-btn"
                    :class="{ active: form.progress_update === p }"
                    @click="form.progress_update = p"
                  >
                    {{ p }}%
                  </span>
                </div>
              </template>
            </van-field>
            <van-field
              v-model="form.notes"
              label="备注/问题"
              type="textarea"
              rows="2"
              placeholder="遇到的问题或备注"
            />
          </van-cell-group>
        </van-form>
      </div>
    </van-popup>

    <!-- Date Range Picker -->
    <van-calendar
      v-model:show="showDatePicker"
      type="range"
      @confirm="onDateRangeConfirm"
    />

    <!-- Form Date Picker -->
    <van-popup v-model:show="showFormDatePicker" position="bottom">
      <van-date-picker
        v-model="formSelectedDate"
        title="选择日期"
        @confirm="onFormDateConfirm"
        @cancel="showFormDatePicker = false"
      />
    </van-popup>

    <!-- Todo Picker -->
    <van-popup v-model:show="showTodoPicker" position="bottom">
      <van-picker
        :columns="todoColumns"
        @confirm="onTodoConfirm"
        @cancel="showTodoPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import { workLogApi, type WorkLog, type WorkLogCreate } from '@/api/workLogs'
import { todoApi, type Todo } from '@/api/todos'

const activeTab = ref(2)
const refreshing = ref(false)
const loading = ref(false)
const workLogs = ref<WorkLog[]>([])
const todos = ref<Todo[]>([])
const showAddForm = ref(false)
const showDatePicker = ref(false)
const showFormDatePicker = ref(false)
const showTodoPicker = ref(false)
const editingLog = ref<WorkLog | null>(null)
const savingLog = ref(false)
const formSelectedDate = ref<string[]>([])

const dateRange = ref('')
const startDate = ref<string>('')
const endDate = ref<string>('')

const form = reactive<WorkLogCreate>({
  date: new Date().toISOString().split('T')[0],
  todo_id: undefined,
  content: '',
  hours_spent: 0,
  progress_update: undefined,
  notes: ''
})

const selectedTodoTitle = computed(() => {
  if (!form.todo_id) return ''
  const todo = todos.value.find(t => t.id === form.todo_id)
  return todo?.title || ''
})

const todoColumns = computed(() => {
  return [
    { text: '不关联任务', value: null },
    ...todos.value.map(t => ({ text: t.title, value: t.id }))
  ]
})

function resetForm() {
  form.date = new Date().toISOString().split('T')[0]
  form.todo_id = undefined
  form.content = ''
  form.hours_spent = 0
  form.progress_update = undefined
  form.notes = ''
  editingLog.value = null
}

function closeForm() {
  showAddForm.value = false
  resetForm()
}

function editLog(log: WorkLog) {
  editingLog.value = log
  form.date = log.date
  form.todo_id = log.todo_id || undefined
  form.content = log.content
  form.hours_spent = log.hours_spent
  form.progress_update = log.progress_update || undefined
  form.notes = log.notes || ''
  showAddForm.value = true
}

async function saveLog() {
  if (!form.content.trim()) {
    showToast('请输入工作内容')
    return
  }
  if (savingLog.value) return

  savingLog.value = true
  try {
    if (editingLog.value) {
      await workLogApi.update(editingLog.value.id, form)
      showToast('更新成功')
    } else {
      await workLogApi.create(form)
      showToast('创建成功')
    }
    closeForm()
    await fetchWorkLogs()
  } catch {
    // Error handled by interceptor
  } finally {
    savingLog.value = false
  }
}

async function deleteLog(id: number) {
  await showConfirmDialog({
    title: '确认删除',
    message: '删除后无法恢复，确定删除吗？'
  })
  await workLogApi.delete(id)
  showToast('删除成功')
  await fetchWorkLogs()
}

function onDateRangeConfirm(dates: Date[]) {
  const [start, end] = dates
  startDate.value = formatDate(start)
  endDate.value = formatDate(end)
  dateRange.value = `${startDate.value} ~ ${endDate.value}`
  showDatePicker.value = false
  fetchWorkLogs()
}

function onFormDateConfirm({ selectedValues }: { selectedValues: string[] }) {
  form.date = selectedValues.join('-')
  showFormDatePicker.value = false
}

function onTodoConfirm({ selectedOptions }: { selectedOptions: { text: string; value: number | null }[] }) {
  form.todo_id = selectedOptions[0].value || undefined
  showTodoPicker.value = false
}

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0]
}

async function fetchWorkLogs() {
  loading.value = true
  try {
    const params: { start_date?: string; end_date?: string } = {}
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value
    const response = await workLogApi.getAll(params)
    workLogs.value = response.data
  } finally {
    loading.value = false
  }
}

async function fetchTodos() {
  // 获取所有未完成的任务（待办和进行中）
  const [pendingRes, inProgressRes] = await Promise.all([
    todoApi.getAll({ status: 'pending' }),
    todoApi.getAll({ status: 'in_progress' })
  ])
  todos.value = [...inProgressRes.data, ...pendingRes.data]
}

async function handleRefresh() {
  await fetchWorkLogs()
  refreshing.value = false
}

onMounted(() => {
  fetchWorkLogs()
  fetchTodos()
})
</script>

<style scoped>
.worklog-page {
  height: 100vh;
  height: 100dvh;
  background: var(--bg-primary);
  padding-bottom: 50px;
  overflow-y: auto;
  overflow-x: hidden;
}

.date-filter {
  background: var(--bg-secondary);
  margin: 16px 20px;
  border-radius: 10px;
}

.loading {
  text-align: center;
  padding: 60px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* 日志列表 */
.log-list {
  padding: 0 20px;
}

.worklog-page :deep(.van-swipe-cell) {
  margin-bottom: 12px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.log-item {
  padding: 16px;
  background: var(--bg-secondary);
}

.log-date {
  font-size: 13px;
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 8px;
}

.log-content {
  font-size: 17px;
  margin-bottom: 12px;
  line-height: 1.5;
  color: var(--text-primary);
}

.log-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-tertiary);
  flex-wrap: wrap;
}

.log-meta .hours {
  background: rgba(52,199,89,0.12);
  color: var(--success);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.log-meta .progress {
  background: var(--primary-light);
  color: var(--primary);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.log-notes {
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(249, 115, 22, 0.1);
  border-radius: 8px;
  font-size: 15px;
  color: var(--warning);
  display: flex;
  align-items: flex-start;
  gap: 6px;
  line-height: 1.4;
}

/* 表单弹窗 */
.form-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.form-popup .van-form {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.form-popup :deep(.van-cell-group--inset) {
  border-radius: 10px;
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

/* 进度选择器 */
.progress-selector {
  display: flex;
  gap: 8px;
  width: 100%;
}

.progress-btn {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.progress-btn.active {
  color: white;
  background: var(--primary);
  font-weight: 500;
}
</style>
