import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import '@/assets/styles/variables.scss'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 创建Vue应用实例
const app = createApp(App)
const pinia = createPinia()

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(ElementPlus)
app.use(pinia)
app.use(router)

// 挂载应用
app.mount('#app')

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue应用错误:', err, instance, info)
}
