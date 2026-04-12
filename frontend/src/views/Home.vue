<template>
  <div class="home-page">
    <header class="page-header">
      <div class="header-content">
        <div class="greeting">
          <h1>{{ greeting }}</h1>
          <p>{{ formattedDate }}</p>
        </div>
        <div class="avatar" @click="showSettings = true">
          {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
        </div>
      </div>
    </header>

    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-number">{{ todayStats.total }}</span>
        <span class="stat-label">今日任务</span>
      </div>
      <div class="stat-card">
        <span class="stat-number">{{ todayStats.completed }}</span>
        <span class="stat-label">已完成</span>
      </div>
      <div class="stat-card">
        <span class="stat-number">{{ todayStats.inProgress }}</span>
        <span class="stat-label">进行中</span>
      </div>
    </div>

    <section class="section">
      <div class="section-header">
        <h2>今日任务</h2>
        <router-link to="/todos" class="see-all">查看全部</router-link>
      </div>

      <van-loading v-if="todoStore.loading" class="loading" />

      <div v-else-if="todoStore.todayTodos.length === 0" class="empty-state">
        <p>今日暂无任务</p>
        <router-link to="/todos" class="add-link">添加任务</router-link>
      </div>

      <div v-else class="task-list">
        <div
          v-for="todo in todoStore.todayTodos.slice(0, 5)"
          :key="todo.id"
          class="task-item"
          @click="viewTodo(todo)"
        >
          <div class="task-check" @click.stop="toggleTodo(todo)">
            <div class="checkbox" :class="{ checked: todo.status === 'completed' }">
              <svg v-if="todo.status === 'completed'" viewBox="0 0 24 24" fill="none">
                <path d="M5 12L10 17L19 8" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="task-info">
            <span class="task-title" :class="{ done: todo.status === 'completed' }">
              {{ todo.title }}
            </span>
            <div class="task-meta">
              <span class="task-category">{{ todo.category }}</span>
              <span class="task-progress">{{ todo.progress }}%</span>
            </div>
          </div>
          <div class="task-priority" :class="getPriorityClass(todo.priority)"></div>
        </div>
      </div>
    </section>

    <section class="quick-actions">
      <router-link to="/todos?action=add" class="action-item">
        <div class="action-icon blue">
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <span>新建任务</span>
      </router-link>
      <router-link to="/work-logs" class="action-item">
        <div class="action-icon orange">
          <svg viewBox="0 0 24 24" fill="none"><path d="M4 4H20M4 8H20M4 12H12M4 16H8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <span>工作日志</span>
      </router-link>
      <router-link to="/reports" class="action-item">
        <div class="action-icon green">
          <svg viewBox="0 0 24 24" fill="none"><path d="M4 20V10M12 20V4M20 20V14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <span>生成报告</span>
      </router-link>
      <router-link to="/templates" class="action-item">
        <div class="action-icon purple">
          <svg viewBox="0 0 24 24" fill="none"><path d="M4 5H20M4 12H20M4 19H12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <span>模板管理</span>
      </router-link>
    </section>

    <van-tabbar v-model="activeTab" route fixed>
      <van-tabbar-item replace to="/" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item replace to="/todos" icon="todo-list-o">任务</van-tabbar-item>
      <van-tabbar-item replace to="/work-logs" icon="notes-o">日志</van-tabbar-item>
      <van-tabbar-item replace to="/reports" icon="chart-trending-o">报告</van-tabbar-item>
    </van-tabbar>

    <van-action-sheet v-model:show="showSettings" title="设置">
      <div class="settings-content">
        <div class="user-info">
          <div class="user-avatar">
            {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div class="user-details">
            <span class="user-name">{{ authStore.user?.username }}</span>
            <span class="user-email">{{ authStore.user?.email }}</span>
          </div>
        </div>
        <van-button block plain type="danger" @click="handleLogout">退出登录</van-button>
      </div>
    </van-action-sheet>

    <!-- 快速更新进度 -->
    <van-action-sheet v-model:show="showQuickEdit" :title="editingTodo?.title">
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
        <div class="quick-edit-link" @click="goToEdit">
          编辑更多 →
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '@/stores/auth'
import { useTodoStore } from '@/stores/todo'
import type { Todo } from '@/api/todos'

const router = useRouter()
const authStore = useAuthStore()
const todoStore = useTodoStore()

const activeTab = ref(0)
const showSettings = ref(false)
const showQuickEdit = ref(false)
const editingTodo = ref<Todo | null>(null)
const quickProgress = ref(0)
const savingProgress = ref(false)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const formattedDate = computed(() => {
  const now = new Date()
  const options: Intl.DateTimeFormatOptions = { month: 'long', day: 'numeric', weekday: 'long' }
  return now.toLocaleDateString('zh-CN', options)
})

const todayStats = computed(() => {
  const todos = todoStore.todayTodos
  return {
    total: todos.length,
    completed: todos.filter(t => t.status === 'completed').length,
    inProgress: todos.filter(t => t.status === 'in_progress').length
  }
})

function getPriorityClass(priority: number): string {
  if (priority >= 5) return 'high'
  if (priority >= 3) return 'medium'
  return 'low'
}

function viewTodo(todo: Todo) {
  editingTodo.value = todo
  quickProgress.value = todo.progress
  showQuickEdit.value = true
}

async function saveQuickProgress() {
  if (!editingTodo.value || savingProgress.value) return
  savingProgress.value = true
  try {
    await todoStore.updateTodo(editingTodo.value.id, { progress: quickProgress.value })
    await todoStore.fetchTodayTodos()
    showQuickEdit.value = false
    showToast('进度已更新')
  } finally {
    savingProgress.value = false
  }
}

function goToEdit() {
  if (!editingTodo.value) return
  showQuickEdit.value = false
  router.push(`/todos?id=${editingTodo.value.id}`)
}

async function toggleTodo(todo: Todo) {
  // 通过进度来控制状态：100% = completed, 0% = pending
  const newProgress = todo.status === 'completed' ? 0 : 100
  await todoStore.updateTodo(todo.id, { progress: newProgress })
  await todoStore.fetchTodayTodos()
  showToast(newProgress === 100 ? '已完成' : '已取消完成')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  await authStore.fetchCurrentUser()
  await todoStore.fetchTodayTodos()
})
</script>

<style scoped>
.home-page {
  height: 100vh;
  height: 100dvh;
  background: var(--bg-primary);
  padding-bottom: 50px;
  overflow-y: auto;
  overflow-x: hidden;
}

.page-header {
  background: var(--bg-secondary);
  padding: 60px 20px 24px;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.greeting h1 {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.5px;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.greeting p {
  font-size: 15px;
  color: var(--text-tertiary);
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 17px;
  box-shadow: var(--shadow-sm);
}

.stats-row {
  display: flex;
  gap: 12px;
  padding: 20px;
  background: var(--bg-secondary);
  backdrop-filter: var(--blur);
}

.stat-card {
  flex: 1;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  padding: 16px;
  text-align: center;
  box-shadow: var(--shadow-sm);
  backdrop-filter: var(--blur);
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.section {
  padding: 24px 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 22px;
  font-weight: 700;
}

.see-all {
  font-size: 15px;
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 40px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.empty-state p {
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.add-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.task-list {
  background: var(--bg-secondary);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  backdrop-filter: var(--blur);
}

.task-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 0.5px solid var(--separator);
}

.task-item:last-child {
  border-bottom: none;
}

.task-check {
  margin-right: 14px;
}

.checkbox {
  width: 24px;
  height: 24px;
  border: 2px solid var(--text-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.checkbox.checked {
  background: var(--success);
  border-color: var(--success);
  color: white;
}

.checkbox svg {
  width: 14px;
  height: 14px;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title {
  display: block;
  font-size: 17px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.task-title.done {
  color: var(--text-tertiary);
  text-decoration: line-through;
}

.task-meta {
  display: flex;
  gap: 8px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.task-progress {
  color: var(--primary);
}

.task-priority {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-left: 12px;
}

.task-priority.high { background: var(--danger); }
.task-priority.medium { background: var(--warning); }
.task-priority.low { background: var(--success); }

.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 0 20px;
  margin-top: 8px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  padding: 16px 8px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
  backdrop-filter: var(--blur);
  transition: all 0.2s ease;
}

.action-item:active {
  transform: scale(0.96);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.action-icon svg {
  width: 24px;
  height: 24px;
}

.action-icon.blue { background: var(--primary-light); color: var(--primary); }
.action-icon.orange { background: rgba(249, 115, 22, 0.12); color: var(--warning); }
.action-icon.green { background: rgba(16, 185, 129, 0.12); color: var(--success); }
.action-icon.purple { background: rgba(139, 92, 246, 0.12); color: var(--secondary); }

.action-item span {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.settings-content {
  padding: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
}

.user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 22px;
  margin-right: 16px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 2px;
}

.user-email {
  font-size: 14px;
  color: var(--text-tertiary);
}

.settings-content :deep(.van-button--plain) {
  border-radius: 10px;
}

/* 快速编辑进度 */
.quick-edit-content {
  padding: 20px;
}

.progress-label {
  font-size: 15px;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.progress-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
}

.progress-btn {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 15px;
  color: var(--text-secondary);
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.progress-btn.active {
  color: white;
  background: var(--primary);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
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
