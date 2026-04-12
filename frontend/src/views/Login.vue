<template>
  <div class="login-page">
    <!-- 装饰背景 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="login-container">
      <!-- Logo 区域 -->
      <div class="brand-section">
        <div class="app-logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
        </div>
        <h1 class="app-title">WorkFlow</h1>
        <p class="app-slogan">任务 · 日志 · 报告，一站搞定</p>
      </div>

      <!-- 登录卡片 -->
      <div class="login-card">
        <p class="card-title">登录账号</p>
        <van-form @submit="handleLogin">
          <div class="input-group">
            <div class="input-wrapper">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2"/>
                  <path d="M4 20C4 16.6863 7.58172 14 12 14C16.4183 14 20 16.6863 20 20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <input
                v-model="form.username"
                type="text"
                placeholder="用户名"
                class="custom-input"
              />
            </div>
            <div class="input-wrapper">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M8 11V7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <input
                v-model="form.password"
                type="password"
                placeholder="密码"
                class="custom-input"
              />
            </div>
          </div>

          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="!loading">登录</span>
            <span v-else class="loading-dots">
              <i></i><i></i><i></i>
            </span>
          </button>
        </van-form>

        <div class="divider">
          <span>或</span>
        </div>

        <router-link to="/register" class="register-btn">
          注册新账号
        </router-link>
      </div>

      <!-- 产品亮点 -->
      <div class="features-hint">
        <span class="feature-tag">任务追踪</span>
        <span class="feature-tag">工作日志</span>
        <span class="feature-tag">智能报告</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    showToast('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    await authStore.login(form.value)
    showToast('登录成功')
    router.push('/')
  } catch (error: any) {
    const message = error.response?.data?.detail || '登录失败，请检查用户名和密码'
    showToast(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  height: 100dvh;
  background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 50%, #f0abfc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 装饰背景 */
.bg-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -100px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: 10%;
  left: -80px;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: -50px;
  right: 20%;
}

.login-container {
  width: 100%;
  max-width: 360px;
  position: relative;
  z-index: 1;
}

/* Logo 区域 */
.brand-section {
  text-align: center;
  margin-bottom: 24px;
}

.app-logo {
  margin-bottom: 12px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.logo-icon svg {
  width: 32px;
  height: 32px;
}

.app-title {
  font-size: 26px;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.app-slogan {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
}

/* 登录卡片 */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1F2937;
  text-align: center;
  margin-bottom: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #F5F5F7;
  border-radius: 12px;
  padding: 0 14px;
  height: 50px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.input-wrapper:focus-within {
  background: white;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.input-icon {
  width: 20px;
  height: 20px;
  color: #9CA3AF;
  margin-right: 10px;
  flex-shrink: 0;
}

.input-icon svg {
  width: 100%;
  height: 100%;
}

.custom-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  color: #1F2937;
  outline: none;
}

.custom-input::placeholder {
  color: #9CA3AF;
}

.login-btn {
  width: 100%;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.35);
}

.login-btn:active {
  transform: scale(0.98);
}

.login-btn:disabled {
  opacity: 0.7;
}

/* Loading 动画 */
.loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.loading-dots i {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots i:nth-child(1) { animation-delay: -0.32s; }
.loading-dots i:nth-child(2) { animation-delay: -0.16s; }
.loading-dots i:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 分隔线 */
.divider {
  display: flex;
  align-items: center;
  margin: 16px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #E5E7EB;
}

.divider span {
  padding: 0 12px;
  color: #9CA3AF;
  font-size: 13px;
}

/* 注册按钮 */
.register-btn {
  display: block;
  width: 100%;
  height: 46px;
  line-height: 46px;
  text-align: center;
  background: transparent;
  border: 1.5px solid #E5E7EB;
  border-radius: 12px;
  color: #4B5563;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;
}

.register-btn:active {
  background: #F5F5F7;
}

/* 产品亮点 */
.features-hint {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.feature-tag {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  font-size: 12px;
  color: white;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 隐藏 vant 表单默认样式 */
.login-card :deep(.van-form) {
  background: transparent;
}

.login-card :deep(.van-cell) {
  display: none;
}
</style>
