import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Vant
import 'vant/lib/index.css'
import '@vant/touch-emulator'

// Vant components that need manual import
import { Locale, ConfigProvider } from 'vant'
import zhCN from 'vant/es/locale/lang/zh-CN'

Locale.use('zh-CN', zhCN)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ConfigProvider)

app.mount('#app')
