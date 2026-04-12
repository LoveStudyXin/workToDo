<template>
  <van-config-provider :theme-vars="themeVars">
    <router-view />
  </van-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, provide } from 'vue'

// 主题切换: 'glass' | 'minimal' | 'gradient'
// 修改这里来切换主题预览
const currentTheme = ref<'glass' | 'minimal' | 'gradient'>('gradient')

provide('currentTheme', currentTheme)
provide('setTheme', (theme: 'glass' | 'minimal' | 'gradient') => {
  currentTheme.value = theme
  document.documentElement.setAttribute('data-theme', theme)
})

// 初始化主题
document.documentElement.setAttribute('data-theme', currentTheme.value)

const themeVars = computed(() => {
  if (currentTheme.value === 'glass') {
    return {
      primaryColor: '#6366F1',
      successColor: '#10B981',
      warningColor: '#F59E0B',
      dangerColor: '#EF4444',
      buttonPrimaryBackground: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
      tabbarItemActiveColor: '#6366F1',
    }
  } else if (currentTheme.value === 'minimal') {
    return {
      primaryColor: '#000000',
      successColor: '#22C55E',
      warningColor: '#EAB308',
      dangerColor: '#DC2626',
      buttonPrimaryBackground: '#000000',
      tabbarItemActiveColor: '#000000',
    }
  } else {
    return {
      primaryColor: '#8B5CF6',
      successColor: '#10B981',
      warningColor: '#F97316',
      dangerColor: '#EF4444',
      buttonPrimaryBackground: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      tabbarItemActiveColor: '#8B5CF6',
    }
  }
})
</script>

<style>
/* ============================================
   主题 A: 毛玻璃现代风 (glass)
   ============================================ */
:root[data-theme="glass"] {
  --primary: #6366F1;
  --primary-light: rgba(99, 102, 241, 0.12);
  --secondary: #8B5CF6;
  --success: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --bg-primary: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  --bg-secondary: rgba(255, 255, 255, 0.7);
  --bg-card: rgba(255, 255, 255, 0.6);
  --text-primary: #1F2937;
  --text-secondary: #4B5563;
  --text-tertiary: #9CA3AF;
  --separator: rgba(0, 0, 0, 0.06);
  --shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
  --shadow-sm: 0 4px 16px rgba(0, 0, 0, 0.06);
  --radius: 20px;
  --radius-sm: 12px;
  --blur: blur(20px);
}

/* ============================================
   主题 C: 极简扁平风 (minimal)
   ============================================ */
:root[data-theme="minimal"] {
  --primary: #000000;
  --primary-light: rgba(0, 0, 0, 0.05);
  --secondary: #525252;
  --success: #22C55E;
  --warning: #EAB308;
  --danger: #DC2626;
  --bg-primary: #FFFFFF;
  --bg-secondary: #FFFFFF;
  --bg-card: #FAFAFA;
  --text-primary: #171717;
  --text-secondary: #525252;
  --text-tertiary: #A3A3A3;
  --separator: #F5F5F5;
  --shadow: none;
  --shadow-sm: none;
  --radius: 8px;
  --radius-sm: 6px;
  --blur: none;
}

/* ============================================
   主题 D: 活力渐变风 (gradient)
   ============================================ */
:root[data-theme="gradient"] {
  --primary: #8B5CF6;
  --primary-light: rgba(139, 92, 246, 0.12);
  --secondary: #EC4899;
  --success: #10B981;
  --warning: #F97316;
  --danger: #EF4444;
  --bg-primary: #F8FAFC;
  --bg-secondary: #FFFFFF;
  --bg-card: #FFFFFF;
  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-tertiary: #94A3B8;
  --separator: rgba(0, 0, 0, 0.05);
  --shadow: 0 10px 40px rgba(139, 92, 246, 0.15);
  --shadow-sm: 0 4px 20px rgba(0, 0, 0, 0.08);
  --radius: 16px;
  --radius-sm: 10px;
  --blur: none;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'PingFang SC', 'Helvetica Neue', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 16px;
  line-height: 1.5;
}

#app {
  height: 100%;
  overflow: hidden;
}

::-webkit-scrollbar {
  display: none;
}

/* ============================================
   毛玻璃主题特有样式
   ============================================ */
[data-theme="glass"] .van-nav-bar {
  background: rgba(255, 255, 255, 0.7) !important;
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

[data-theme="glass"] .van-tabbar {
  background: rgba(255, 255, 255, 0.7) !important;
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 -10px 40px rgba(99, 102, 241, 0.1) !important;
}

[data-theme="glass"] .van-button--primary {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
  border: none !important;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
}

[data-theme="glass"] .van-cell-group--inset {
  background: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* ============================================
   极简主题特有样式
   ============================================ */
[data-theme="minimal"] .van-nav-bar {
  background: #FFFFFF !important;
  border-bottom: 1px solid #F5F5F5 !important;
}

[data-theme="minimal"] .van-tabbar {
  background: #FFFFFF !important;
  border-top: 1px solid #F5F5F5 !important;
  box-shadow: none !important;
}

[data-theme="minimal"] .van-button--primary {
  background: #000000 !important;
  border: none !important;
  border-radius: 6px !important;
  box-shadow: none !important;
}

[data-theme="minimal"] .van-button--round {
  border-radius: 6px !important;
}

[data-theme="minimal"] .van-cell-group--inset {
  border: 1px solid #F5F5F5 !important;
  box-shadow: none !important;
}

[data-theme="minimal"] .van-tag {
  border-radius: 4px !important;
  background: #F5F5F5 !important;
  color: #525252 !important;
}

[data-theme="minimal"] .van-tag--primary {
  background: #000000 !important;
  color: #FFFFFF !important;
}

/* ============================================
   渐变主题特有样式
   ============================================ */
[data-theme="gradient"] .van-nav-bar {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%) !important;
  backdrop-filter: blur(10px);
  border-bottom: none !important;
}

[data-theme="gradient"] .van-tabbar {
  background: #FFFFFF !important;
  border-top: none !important;
  box-shadow: 0 -4px 30px rgba(0, 0, 0, 0.1) !important;
}

[data-theme="gradient"] .van-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
}

[data-theme="gradient"] .van-cell-group--inset {
  background: #FFFFFF !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
  border: none !important;
}

[data-theme="gradient"] .van-tag--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: #FFFFFF !important;
}

[data-theme="gradient"] .van-tag--success {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
  color: #FFFFFF !important;
}

[data-theme="gradient"] .van-tag--warning {
  background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important;
  color: #FFFFFF !important;
}

/* ============================================
   通用组件样式
   ============================================ */
.van-nav-bar__title {
  font-weight: 600 !important;
  font-size: 17px !important;
  color: var(--text-primary) !important;
}

.van-nav-bar__arrow {
  color: var(--primary) !important;
}

.van-cell-group--inset {
  margin: 0 !important;
  border-radius: var(--radius-sm) !important;
  overflow: hidden;
}

.van-cell {
  padding: 14px 16px !important;
  font-size: 16px !important;
  background: transparent !important;
}

.van-cell::after {
  left: 16px !important;
  border-color: var(--separator) !important;
}

.van-field__label {
  color: var(--text-primary) !important;
  font-size: 16px !important;
}

.van-button--primary {
  font-weight: 600 !important;
  font-size: 16px !important;
  transition: all 0.3s ease;
}

.van-button--primary:active {
  transform: scale(0.98);
}

.van-button--round {
  border-radius: var(--radius-sm) !important;
}

.van-tag {
  border-radius: 6px !important;
  font-weight: 500 !important;
  padding: 2px 8px !important;
}

.van-empty__description {
  color: var(--text-tertiary) !important;
}

.van-tabs__line {
  background: var(--primary) !important;
  border-radius: 2px !important;
}

.van-tab--active {
  color: var(--primary) !important;
  font-weight: 600 !important;
}

.van-dropdown-menu__bar {
  box-shadow: none !important;
  background: var(--bg-secondary) !important;
}

.van-loading__spinner {
  color: var(--primary) !important;
}

.van-tabbar-item--active {
  color: var(--primary) !important;
}
</style>
