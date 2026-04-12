import { defineStore } from 'pinia'
import { ref } from 'vue'
import { todoApi, type Todo, type TodoCreate, type TodoUpdate, type TodoFilters } from '@/api/todos'

export const useTodoStore = defineStore('todo', () => {
  const todos = ref<Todo[]>([])
  const todayTodos = ref<Todo[]>([])
  const loading = ref(false)

  async function fetchTodos(filters?: TodoFilters) {
    loading.value = true
    try {
      const response = await todoApi.getAll(filters)
      todos.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchTodayTodos() {
    loading.value = true
    try {
      const response = await todoApi.getToday()
      todayTodos.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function createTodo(data: TodoCreate) {
    const response = await todoApi.create(data)
    todos.value.unshift(response.data)
    return response.data
  }

  async function updateTodo(id: number, data: TodoUpdate) {
    const response = await todoApi.update(id, data)
    const index = todos.value.findIndex(t => t.id === id)
    if (index !== -1) {
      todos.value[index] = response.data
    }
    return response.data
  }

  async function deleteTodo(id: number) {
    await todoApi.delete(id)
    todos.value = todos.value.filter(t => t.id !== id)
  }

  return {
    todos,
    todayTodos,
    loading,
    fetchTodos,
    fetchTodayTodos,
    createTodo,
    updateTodo,
    deleteTodo
  }
})
