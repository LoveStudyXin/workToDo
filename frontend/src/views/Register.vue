<template>
  <div class="register-page">
    <!-- 装饰背景 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="register-container">
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
        <p class="app-slogan">开启高效工作之旅</p>
      </div>

      <!-- 注册卡片 -->
      <div class="register-card">
        <p class="card-title">创建账号</p>
        <van-form @submit="handleRegister">
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
                placeholder="用户名（3-20位字母数字）"
                class="custom-input"
              />
            </div>
            <div class="input-wrapper">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M3 8L10.89 13.26C11.2187 13.4793 11.6049 13.5963 12 13.5963C12.3951 13.5963 12.7813 13.4793 13.11 13.26L21 8M5 19H19C20.1046 19 21 18.1046 21 17V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V17C3 18.1046 3.89543 19 5 19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <input
                v-model="form.email"
                type="email"
                placeholder="邮箱地址"
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
                placeholder="密码（至少6位）"
                class="custom-input"
              />
            </div>
            <div class="input-wrapper">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M8 11V7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <input
                v-model="confirmPassword"
                type="password"
                placeholder="确认密码"
                class="custom-input"
              />
            </div>
          </div>

          <button type="submit" class="register-btn" :disabled="loading">
            <span v-if="!loading">注册</span>
            <span v-else class="loading-dots">
              <i></i><i></i><i></i>
            </span>
          </button>
        </van-form>

        <div class="divider">
          <span>或</span>
        </div>

        <router-link to="/login" class="login-link">
          已有账号，去登录
        </router-link>
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
  email: '',
  password: ''
})
const confirmPassword = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!form.value.username || !form.value.email || !form.value.password) {
    showToast('请填写完整信息')
    return
  }
  if (!/^[a-zA-Z0-9_]{3,20}$/.test(form.value.username)) {
    showToast('用户名需3-20位字母数字下划线')
    return
  }
  if (!/^\S+@\S+\.\S+$/.test(form.value.email)) {
    showToast('请输入有效邮箱')
    return
  }
  if (form.value.password.length < 6) {
    showToast('密码至少6位')
    return
  }
  if (confirmPassword.value !== form.value.password) {
    showToast('两次密码不一致')
    return
  }

  loading.value = true
  try {
    await authStore.register(form.value)
    showToast('注册成功')
    router.push('/login')
  } catch {
    // Error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
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

.register-container {
  width: 100%;
  max-width: 360px;
  position: relative;
  z-index: 1;
}

/* Logo 区域 */
.brand-section {
  text-align: center;
  margin-bottom: 20px;
}

.app-logo {
  margin-bottom: 10px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.logo-icon svg {
  width: 28px;
  height: 28px;
}

.app-title {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.app-slogan {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
}

/* 注册卡片 */
.register-card {
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
  margin-bottom: 18px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 18px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #F5F5F7;
  border-radius: 12px;
  padding: 0 14px;
  height: 48px;
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
  font-size: 15px;
  color: #1F2937;
  outline: none;
}

.custom-input::placeholder {
  color: #9CA3AF;
}

.register-btn {
  width: 100%;
  height: 48px;
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

.register-btn:active {
  transform: scale(0.98);
}

.register-btn:disabled {
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
  margin: 14px 0;
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

/* 登录链接 */
.login-link {
  display: block;
  width: 100%;
  height: 44px;
  line-height: 44px;
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

.login-link:active {
  background: #F5F5F7;
}

/* 隐藏 vant 表单默认样式 */
.register-card :deep(.van-form) {
  background: transparent;
}

.register-card :deep(.van-cell) {
  display: none;
}
</style>
