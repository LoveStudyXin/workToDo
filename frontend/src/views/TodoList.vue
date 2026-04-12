<template>
  <div class="todo-page">
    <van-nav-bar title="任务列表" left-arrow fixed placeholder @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="20" @click="showAddForm = true" />
      </template>
    </van-nav-bar>

    <div class="filter-bar">
      <van-dropdown-menu>
        <van-dropdown-item v-model="filters.status" :options="statusOptions" />
        <van-dropdown-item v-model="filters.category" :options="categoryOptions" />
        <van-dropdown-item v-model="filters.priority" :options="priorityOptions" />
      </van-dropdown-menu>
    </div>

    <van-pull-refresh v-model="refreshing" @refresh="handleRefresh">
      <van-loading v-if="todoStore.loading && !refreshing" class="loading" />

      <div v-else-if="todoStore.todos.length === 0" class="empty-state">
        <van-empty description="暂无任务">
          <van-button type="primary" size="small" @click="showAddForm = true">
            创建任务
          </van-button>
        </van-empty>
      </div>

      <van-swipe-cell v-for="todo in todoStore.todos" :key="todo.id">
        <div class="todo-item" @click="openQuickEdit(todo)">
          <div class="todo-checkbox" @click.stop="toggleTodo(todo)">
            <van-icon
              :name="todo.status === 'completed' ? 'checked' : 'circle'"
              :color="todo.status === 'completed' ? '#07c160' : '#ddd'"
              size="22"
            />
          </div>
          <div class="todo-content">
            <div class="todo-title" :class="{ completed: todo.status === 'completed' }">
              {{ todo.title }}
            </div>
            <div class="todo-meta">
              <van-tag :type="getPriorityType(todo.priority)" size="small">
                {{ getPriorityLabel(todo.priority) }}
              </van-tag>
              <span class="category">{{ todo.category }}</span>
              <van-progress
                :percentage="todo.progress"
                :show-pivot="false"
                stroke-width="4"
                class="progress-bar"
              />
            </div>
            <div v-if="todo.due_date" class="due-date">
              <van-icon name="clock-o" size="12" />
              截止: {{ todo.due_date }}
            </div>
          </div>
          <div class="todo-edit-btn" @click.stop="editTodo(todo)">
            <van-icon name="edit" size="18" />
          </div>
        </div>
        <template #right>
          <van-button square type="danger" text="删除" @click="deleteTodo(todo.id)" />
        </template>
      </van-swipe-cell>
    </van-pull-refresh>

    <van-tabbar v-model="activeTab" route fixed>
      <van-tabbar-item replace to="/" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item replace to="/todos" icon="todo-list-o">任务</van-tabbar-item>
      <van-tabbar-item replace to="/work-logs" icon="notes-o">日志</van-tabbar-item>
      <van-tabbar-item replace to="/reports" icon="chart-trending-o">报告</van-tabbar-item>
    </van-tabbar>

    <!-- 快速更新进度 -->
    <van-action-sheet v-model:show="showQuickEdit" :title="quickEditingTodo?.title">
      <div class="quick-edit-content">
        <div class="progress-label">更新进度</div>
        <div class="progress-selector">
          <span
            v-for="p in [0, 25, 50, 75, 100]"
            :key="p"
            class="progress-btn"
            :class="{ active: quickProgress === p }"
            @click="quickProgress = p"
          >
            {{ p }}%
          </span>
        </div>
        <van-button type="primary" block round @click="saveQuickProgress" :disabled="savingProgress">
          {{ savingProgress ? '保存中...' : '保存' }}
        </van-button>
        <div class="quick-edit-link" @click="goToFullEdit">
          编辑更多 →
        </div>
      </div>
    </van-action-sheet>

    <!-- Add/Edit Form -->
    <van-popup v-model:show="showAddForm" position="bottom" round style="height: 80%">
      <div class="form-popup">
        <van-nav-bar
          :title="editingTodo ? '编辑任务' : '新建任务'"
          left-text="取消"
          @click-left="closeForm"
        >
          <template #right>
            <span class="nav-save-btn" :class="{ disabled: savingTodo }" @click="saveTodo">
              {{ savingTodo ? '保存中...' : '保存' }}
            </span>
          </template>
        </van-nav-bar>
        <van-form ref="formRef">
          <van-cell-group inset>
            <van-field
              v-model="form.title"
              label="标题"
              placeholder="请输入任务标题"
              :rules="[{ required: true, message: '请输入标题' }]"
            />
            <van-field
              v-model="form.description"
              label="描述"
              type="textarea"
              rows="2"
              placeholder="请输入任务描述"
            />
            <van-field
              v-model="form.category"
              is-link
              readonly
              label="分类"
              placeholder="选择分类"
              @click="showCategoryPicker = true"
            />
            <van-field
              v-model="priorityText"
              is-link
              readonly
              label="优先级"
              placeholder="选择优先级"
              @click="showPriorityPicker = true"
            />
            <van-field
              v-model="form.estimated_hours"
              label="预估工时"
              type="number"
              placeholder="小时"
            />
            <van-field
              v-model="form.due_date"
              is-link
              readonly
              label="截止日期"
              placeholder="选择日期"
              @click="showDatePicker = true"
            />
            <van-field v-if="editingTodo" label="进度">
              <template #input>
                <div class="progress-selector">
                  <span
                    v-for="p in [0, 25, 50, 75, 100]"
                    :key="p"
                    class="progress-btn"
                    :class="{ active: form.progress === p }"
                    @click="form.progress = p"
                  >
                    {{ p }}%
                  </span>
                </div>
              </template>
            </van-field>
          </van-cell-group>
        </van-form>
      </div>
    </van-popup>

    <!-- Category Picker -->
    <van-popup v-model:show="showCategoryPicker" position="bottom">
      <van-picker
        :columns="categories"
        @confirm="onCategoryConfirm"
        @cancel="showCategoryPicker = false"
      />
    </van-popup>

    <!-- Priority Picker -->
    <van-popup v-model:show="showPriorityPicker" position="bottom">
      <van-picker
        :columns="priorities"
        @confirm="onPriorityConfirm"
        @cancel="showPriorityPicker = false"
      />
    </van-popup>

    <!-- Date Picker -->
    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        v-model="selectedDate"
        title="选择截止日期"
        :min-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { useTodoStore } from '@/stores/todo'
import type { Todo, TodoCreate, TodoUpdate } from '@/api/todos'

const route = useRoute()
const router = useRouter()
const todoStore = useTodoStore()

const activeTab = ref(1)
const refreshing = ref(false)
const showAddForm = ref(false)
const showCategoryPicker = ref(false)
const showPriorityPicker = ref(false)
const showDatePicker = ref(false)
const editingTodo = ref<Todo | null>(null)
const savingTodo = ref(false)
const selectedDate = ref<string[]>([])

// 快速编辑进度
const showQuickEdit = ref(false)
const quickEditingTodo = ref<Todo | null>(null)
const quickProgress = ref(0)
const savingProgress = ref(false)

const filters = reactive({
  status: '',
  category: '',
  priority: ''
})

const form = reactive<TodoCreate & { progress?: number }>({
  title: '',
  description: '',
  category: '其他',
  priority: 3,
  estimated_hours: undefined,
  due_date: undefined,
  progress: 0
})

const categoryList = ['开发', '测试', '会议', '文档', '设计', '运维', '其他']
const categories = categoryList.map(c => ({ text: c, value: c }))
const priorities = [
  { text: '紧急', value: 5 },
  { text: '高', value: 4 },
  { text: '中', value: 3 },
  { text: '低', value: 2 },
  { text: '最低', value: 1 }
]

const statusOptions = [
  { text: '全部状态', value: '' },
  { text: '待处理', value: 'pending' },
  { text: '进行中', value: 'in_progress' },
  { text: '已完成', value: 'completed' }
]

const categoryOptions = [
  { text: '全部分类', value: '' },
  ...categoryList.map(c => ({ text: c, value: c }))
]

const priorityOptions = [
  { text: '全部优先级', value: '' },
  ...priorities.map(p => ({ text: p.text, value: String(p.value) }))
]

const priorityText = computed(() => {
  const p = priorities.find(item => item.value === form.priority)
  return p?.text || '中'
})

function getPriorityType(priority: number): 'danger' | 'warning' | 'primary' | 'success' | 'default' {
  if (priority >= 5) return 'danger'
  if (priority >= 4) return 'warning'
  if (priority >= 3) return 'primary'
  return 'default'
}

function getPriorityLabel(priority: number): string {
  const p = priorities.find(item => item.value === priority)
  return p?.text || '中'
}

function resetForm() {
  form.title = ''
  form.description = ''
  form.category = '其他'
  form.priority = 3
  form.estimated_hours = undefined
  form.due_date = undefined
  form.progress = 0
  editingTodo.value = null
}

function closeForm() {
  showAddForm.value = false
  resetForm()
}

function editTodo(todo: Todo) {
  editingTodo.value = todo
  form.title = todo.title
  form.description = todo.description || ''
  form.category = todo.category
  form.priority = todo.priority
  form.estimated_hours = todo.estimated_hours || undefined
  form.due_date = todo.due_date || undefined
  form.progress = todo.progress
  showAddForm.value = true
}

async function saveTodo() {
  if (!form.title.trim()) {
    showToast('请输入标题')
    return
  }
  if (savingTodo.value) return

  savingTodo.value = true
  try {
    if (editingTodo.value) {
      const updateData: TodoUpdate = {
        title: form.title,
        description: form.description,
        category: form.category,
        priority: form.priority,
        estimated_hours: form.estimated_hours,
        due_date: form.due_date,
        progress: form.progress
      }
      await todoStore.updateTodo(editingTodo.value.id, updateData)
      showToast('更新成功')
    } else {
      await todoStore.createTodo(form)
      showToast('创建成功')
    }
    closeForm()
    await fetchTodos()
  } catch {
    // Error handled by interceptor
  } finally {
    savingTodo.value = false
  }
}

async function toggleTodo(todo: Todo) {
  // 通过进度来控制状态：100% = completed, 0% = pending
  const newProgress = todo.status === 'completed' ? 0 : 100
  await todoStore.updateTodo(todo.id, { progress: newProgress })
  showToast(newProgress === 100 ? '已完成' : '已取消完成')
}

// 快速编辑进度
function openQuickEdit(todo: Todo) {
  quickEditingTodo.value = todo
  quickProgress.value = todo.progress
  showQuickEdit.value = true
}

async function saveQuickProgress() {
  if (!quickEditingTodo.value || savingProgress.value) return
  savingProgress.value = true
  try {
    await todoStore.updateTodo(quickEditingTodo.value.id, { progress: quickProgress.value })
    await fetchTodos()
    showQuickEdit.value = false
    showToast('进度已更新')
  } finally {
    savingProgress.value = false
  }
}

function goToFullEdit() {
  if (!quickEditingTodo.value) return
  showQuickEdit.value = false
  editTodo(quickEditingTodo.value)
}

async function deleteTodo(id: number) {
  await showConfirmDialog({
    title: '确认删除',
    message: '删除后无法恢复，确定删除吗？'
  })
  await todoStore.deleteTodo(id)
  showToast('删除成功')
}

function onCategoryConfirm({ selectedOptions }: { selectedOptions: { text: string }[] }) {
  form.category = selectedOptions[0].text
  showCategoryPicker.value = false
}

function onPriorityConfirm({ selectedOptions }: { selectedOptions: { text: string; value: number }[] }) {
  form.priority = selectedOptions[0].value
  showPriorityPicker.value = false
}

function onDateConfirm({ selectedValues }: { selectedValues: string[] }) {
  form.due_date = selectedValues.join('-')
  showDatePicker.value = false
}

async function fetchTodos() {
  const filterParams: Record<string, string | number | undefined> = {}
  if (filters.status) filterParams.status = filters.status
  if (filters.category) filterParams.category = filters.category
  if (filters.priority) filterParams.priority = parseInt(filters.priority)
  await todoStore.fetchTodos(filterParams)
}

async function handleRefresh() {
  await fetchTodos()
  refreshing.value = false
}

watch(filters, () => {
  fetchTodos()
})

onMounted(async () => {
  await fetchTodos()
  // 如果从首页点击"新建任务"跳转过来，自动打开新建表单
  if (route.query.action === 'add') {
    showAddForm.value = true
    router.replace({ path: '/todos' })
  }
  // 如果有任务ID参数，自动打开编辑表单
  if (route.query.id) {
    const todoId = Number(route.query.id)
    const todo = todoStore.todos.find(t => t.id === todoId)
    if (todo) {
      editTodo(todo)
    }
    router.replace({ path: '/todos' })
  }
})
</script>

<style scoped>
.todo-page {
  height: 100vh;
  height: 100dvh;
  background: var(--bg-primary);
  padding-bottom: 50px;
  overflow-y: auto;
  overflow-x: hidden;
}

.filter-bar {
  background: var(--bg-secondary);
}

.filter-bar :deep(.van-dropdown-menu__bar) {
  height: 44px;
}

.filter-bar :deep(.van-dropdown-menu__title) {
  font-size: 15px;
}

.loading {
  text-align: center;
  padding: 60px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-state :deep(.van-empty__description) {
  margin-top: 16px;
}

.empty-state :deep(.van-button) {
  margin-top: 16px;
}

/* 任务列表 */
.todo-page :deep(.van-swipe-cell) {
  margin: 0;
  background: var(--bg-secondary);
}

.todo-item {
  display: flex;
  align-items: flex-start;
  padding: 14px 20px;
  background: var(--bg-secondary);
  border-bottom: 0.5px solid var(--separator);
}

.todo-checkbox {
  margin-right: 14px;
  padding-top: 2px;
}

.todo-checkbox :deep(.van-icon) {
  font-size: 24px;
}

.todo-content {
  flex: 1;
  min-width: 0;
}

.todo-title {
  font-size: 17px;
  color: var(--text-primary);
  margin-bottom: 6px;
  line-height: 1.4;
}

.todo-title.completed {
  color: var(--text-tertiary);
  text-decoration: line-through;
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 6px;
}

.todo-meta .category {
  background: var(--bg-primary);
  padding: 2px 8px;
  border-radius: 4px;
}

.progress-bar {
  width: 60px;
}

.progress-bar :deep(.van-progress__portion) {
  background: var(--primary);
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

.due-date {
  font-size: 13px;
  color: var(--warning);
  display: flex;
  align-items: center;
  gap: 4px;
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
  overflow: hidden;
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

/* 编辑按钮 */
.todo-edit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  margin-left: 8px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.todo-edit-btn:active {
  color: var(--primary);
}

/* 快速编辑弹窗 */
.quick-edit-content {
  padding: 20px;
}

.progress-label {
  font-size: 15px;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.quick-edit-content .progress-selector {
  margin-bottom: 24px;
}

.quick-edit-content :deep(.van-button) {
  height: 44px;
  font-size: 16px;
}

.quick-edit-link {
  text-align: center;
  margin-top: 16px;
  color: var(--primary);
  font-size: 15px;
  cursor: pointer;
  font-weight: 500;
}
</style>
