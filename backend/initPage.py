#!/usr/bin/env python
"""
超市库存管理系统 - 前端Vue项目结构创建脚本
创建基于Vue 3 + Element Plus + Vue Router + Pinia的完整前端项目
"""
import os
import sys
import json
from pathlib import Path

def create_vue_project_structure(base_dir):
    """创建Vue项目完整结构"""
    project_root = Path(base_dir)
    frontend_dir = project_root / "frontend"
    
    print("=" * 60)
    print("创建超市库存管理系统前端项目")
    print("=" * 60)
    print(f"项目根目录: {project_root}")
    print(f"前端目录: {frontend_dir}")
    
    # 创建完整的目录结构
    directories = [
        frontend_dir / "public",
        frontend_dir / "src" / "api",
        frontend_dir / "src" / "assets" / "styles",
        frontend_dir / "src" / "assets" / "images",
        frontend_dir / "src" / "components" / "layout",
        frontend_dir / "src" / "components" / "common",
        frontend_dir / "src" / "components" / "charts",
        frontend_dir / "src" / "router",
        frontend_dir / "src" / "stores",
        frontend_dir / "src" / "utils",
        frontend_dir / "src" / "views" / "auth",
        frontend_dir / "src" / "views" / "dashboard",
        frontend_dir / "src" / "views" / "users",
        frontend_dir / "src" / "views" / "products",
        frontend_dir / "src" / "views" / "operations",
        frontend_dir / "src" / "views" / "settings",
    ]
    
    print("\n📁 创建目录结构:")
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        rel_path = directory.relative_to(project_root)
        print(f"  mkdir -p {rel_path}")
    
    return frontend_dir

def create_package_json(frontend_dir):
    """创建package.json文件"""
    package_json = {
        "name": "supermarket-frontend",
        "private": True,
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
            "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs --fix --ignore-path .gitignore"
        },
        "dependencies": {
            "vue": "^3.4.0",
            "vue-router": "^4.2.0",
            "pinia": "^2.1.0",
            "axios": "^1.6.0",
            "element-plus": "^2.4.0",
            "echarts": "^5.4.0",
            "@element-plus/icons-vue": "^2.3.0",
            "dayjs": "^1.11.0",
            "nprogress": "^0.2.0"
        },
        "devDependencies": {
            "@vitejs/plugin-vue": "^4.5.0",
            "@vue/compiler-sfc": "^3.4.0",
            "@vitejs/plugin-vue-jsx": "^3.0.0",
            "vite": "^5.0.0",
            "eslint": "^8.55.0",
            "eslint-plugin-vue": "^9.19.0",
            "sass": "^1.69.0"
        }
    }
    
    package_json_path = frontend_dir / "package.json"
    with open(package_json_path, "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 创建文件: {package_json_path.relative_to(frontend_dir.parent)}")
    return package_json_path

def create_vite_config(frontend_dir):
    """创建Vite配置文件"""
    config_content = '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\\/api/, '')
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  }
})
'''
    
    config_path = frontend_dir / "vite.config.js"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print(f"📄 创建文件: {config_path.relative_to(frontend_dir.parent)}")
    return config_path

def create_html_template(frontend_dir):
    """创建HTML模板"""
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>超市库存管理系统</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
'''
    
    html_path = frontend_dir / "index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"📄 创建文件: {html_path.relative_to(frontend_dir.parent)}")
    return html_path

def create_main_js(frontend_dir):
    """创建应用主入口文件"""
    main_content = '''import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
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
'''
    
    main_path = frontend_dir / "src" / "main.js"
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)
    
    print(f"📄 创建文件: {main_path.relative_to(frontend_dir.parent)}")
    return main_path

def create_app_vue(frontend_dir):
    """创建App.vue主组件"""
    app_content = '''<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('超市库存管理系统前端应用已启动')
})
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  overflow: hidden;
  background-color: #f0f2f5;
}
</style>
'''
    
    app_path = frontend_dir / "src" / "App.vue"
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_content)
    
    print(f"📄 创建文件: {app_path.relative_to(frontend_dir.parent)}")
    return app_path

def create_api_config(frontend_dir):
    """创建API配置"""
    api_index_content = '''import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    if (response.status === 200) {
      return res
    } else {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    
    return Promise.reject(error)
  }
)

export default service
'''
    
    api_index_path = frontend_dir / "src" / "api" / "index.js"
    with open(api_index_path, "w", encoding="utf-8") as f:
        f.write(api_index_content)
    
    # 创建API模块文件
    api_modules = {
        'auth.js': '''// 认证相关API
import request from './index'

export default {
  // 登录
  login(data) {
    return request.post('/auth/login/', data)
  },
  
  // 登出
  logout() {
    return request.post('/auth/logout/')
  },
  
  // 注册
  register(data) {
    return request.post('/auth/register/', data)
  },
  
  // 获取用户信息
  getUserInfo() {
    return request.get('/auth/user-info/')
  },
  
  // 刷新token
  refreshToken(token) {
    return request.post('/auth/refresh/', { refresh: token })
  }
}
''',
        'user.js': '''// 用户管理API
import request from './index'

export default {
  // 获取用户列表
  getUsers(params) {
    return request.get('/users/', { params })
  },
  
  // 获取单个用户
  getUser(id) {
    return request.get(`/users/${id}/`)
  },
  
  // 创建用户
  createUser(data) {
    return request.post('/users/', data)
  },
  
  // 更新用户
  updateUser(id, data) {
    return request.put(`/users/${id}/`, data)
  },
  
  // 删除用户
  deleteUser(id) {
    return request.delete(`/users/${id}/`)
  },
  
  // 修改密码
  changePassword(id, data) {
    return request.post(`/users/${id}/change-password/`, data)
  }
}
''',
        'product.js': '''// 商品管理API
import request from './index'

export default {
  // 商品分类
  getCategories(params) {
    return request.get('/products/categories/', { params })
  },
  
  createCategory(data) {
    return request.post('/products/categories/', data)
  },
  
  updateCategory(id, data) {
    return request.put(`/products/categories/${id}/`, data)
  },
  
  deleteCategory(id) {
    return request.delete(`/products/categories/${id}/`)
  },
  
  // 商品管理
  getProducts(params) {
    return request.get('/products/products/', { params })
  },
  
  getProduct(id) {
    return request.get(`/products/products/${id}/`)
  },
  
  createProduct(data) {
    return request.post('/products/products/', data)
  },
  
  updateProduct(id, data) {
    return request.put(`/products/products/${id}/`, data)
  },
  
  deleteProduct(id) {
    return request.delete(`/products/products/${id}/`)
  },
  
  // 库存管理
  getInventories(params) {
    return request.get('/products/inventories/', { params })
  },
  
  updateInventory(id, data) {
    return request.put(`/products/inventories/${id}/`, data)
  },
  
  // 入库/出库
  inventoryInOut(data) {
    return request.post('/operations/inventory-transactions/in-out/', data)
  }
}
''',
        'operation.js': '''// 运营管理API
import request from './index'

export default {
  // 操作日志
  getOperationLogs(params) {
    return request.get('/operations/operation-logs/', { params })
  },
  
  // 库存交易
  getInventoryTransactions(params) {
    return request.get('/operations/inventory-transactions/', { params })
  },
  
  // 销售记录
  getSalesRecords(params) {
    return request.get('/operations/sales-records/', { params })
  },
  
  createSalesRecord(data) {
    return request.post('/operations/sales-records/', data)
  },
  
  // 销售分析
  getSalesAnalysis(params) {
    return request.get('/operations/sales-analyses/', { params })
  },
  
  // 收银数据导入
  uploadCashData(formData) {
    return request.post('/operations/cash-imports/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}
'''
    }
    
    for filename, content in api_modules.items():
        api_path = frontend_dir / "src" / "api" / filename
        with open(api_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 创建文件: {api_path.relative_to(frontend_dir.parent)}")
    
    return True

def create_router_config(frontend_dir):
    """创建路由配置"""
    router_content = '''import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 路由懒加载
const Layout = () => import('@/components/layout/Layout.vue')
const Login = () => import('@/views/auth/Login.vue')
const Dashboard = () => import('@/views/dashboard/Dashboard.vue')
const UserList = () => import('@/views/users/UserList.vue')
const ProductList = () => import('@/views/products/ProductList.vue')
const CategoryList = () => import('@/views/products/CategoryList.vue')
const InventoryList = () => import('@/views/products/InventoryList.vue')
const SupplierList = () => import('@/views/operations/SupplierList.vue')
const SalesAnalysis = () => import('@/views/operations/SalesAnalysis.vue')
const OperationLog = () => import('@/views/operations/OperationLog.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '仪表板', icon: 'DataLine' }
      },
      {
        path: 'users',
        name: 'UserList',
        component: UserList,
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'products',
        name: 'ProductList',
        component: ProductList,
        meta: { title: '商品管理', icon: 'Goods' }
      },
      {
        path: 'categories',
        name: 'CategoryList',
        component: CategoryList,
        meta: { title: '分类管理', icon: 'Folder' }
      },
      {
        path: 'inventory',
        name: 'InventoryList',
        component: InventoryList,
        meta: { title: '库存管理', icon: 'Box' }
      },
      {
        path: 'suppliers',
        name: 'SupplierList',
        component: SupplierList,
        meta: { title: '供货商管理', icon: 'Truck' }
      },
      {
        path: 'sales-analysis',
        name: 'SalesAnalysis',
        component: SalesAnalysis,
        meta: { title: '销售分析', icon: 'TrendCharts' }
      },
      {
        path: 'operation-logs',
        name: 'OperationLog',
        component: OperationLog,
        meta: { title: '操作日志', icon: 'Document' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 进度条配置
NProgress.configure({ showSpinner: false })

// 路由守卫
router.beforeEach((to, from, next) => {
  NProgress.start()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title + ' - 超市库存管理系统'
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      next('/login')
      NProgress.done()
      return
    }
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
'''
    
    router_path = frontend_dir / "src" / "router" / "index.js"
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(router_content)
    
    print(f"📄 创建文件: {router_path.relative_to(frontend_dir.parent)}")
    return router_path

def create_store_config(frontend_dir):
    """创建状态管理配置"""
    # 创建auth store
    auth_store_content = '''import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || '')
  const userName = computed(() => user.value?.username || '')
  
  // 登录
  async function login(loginData) {
    try {
      const response = await authApi.login(loginData)
      
      // 假设返回的数据结构
      const { access, refresh, user: userInfo } = response
      
      token.value = access
      user.value = userInfo
      
      localStorage.setItem('token', access)
      localStorage.setItem('refresh_token', refresh || '')
      localStorage.setItem('user', JSON.stringify(userInfo))
      
      return Promise.resolve(response)
    } catch (error) {
      return Promise.reject(error)
    }
  }
  
  // 登出
  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearAuthData()
    }
  }
  
  // 清除认证数据
  function clearAuthData() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }
  
  // 获取用户信息
  async function getUserInfo() {
    try {
      const response = await authApi.getUserInfo()
      user.value = response
      localStorage.setItem('user', JSON.stringify(response))
      return Promise.resolve(response)
    } catch (error) {
      return Promise.reject(error)
    }
  }
  
  return {
    token,
    user,
    isAuthenticated,
    userRole,
    userName,
    login,
    logout,
    clearAuthData,
    getUserInfo
  }
})
'''
    
    # 创建app store
    app_store_content = '''import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const theme = ref('light')
  const loading = ref(false)
  
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  function setSidebarCollapsed(collapsed) {
    sidebarCollapsed.value = collapsed
  }
  
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }
  
  function setLoading(value) {
    loading.value = value
  }
  
  return {
    sidebarCollapsed,
    theme,
    loading,
    toggleSidebar,
    setSidebarCollapsed,
    toggleTheme,
    setLoading
  }
})
'''
    
    # 创建store主文件
    store_index_content = '''import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia
'''
    
    # 写入文件
    auth_store_path = frontend_dir / "src" / "stores" / "auth.js"
    with open(auth_store_path, "w", encoding="utf-8") as f:
        f.write(auth_store_content)
    
    app_store_path = frontend_dir / "src" / "stores" / "app.js"
    with open(app_store_path, "w", encoding="utf-8") as f:
        f.write(app_store_content)
    
    store_index_path = frontend_dir / "src" / "stores" / "index.js"
    with open(store_index_path, "w", encoding="utf-8") as f:
        f.write(store_index_content)
    
    print(f"📄 创建文件: {auth_store_path.relative_to(frontend_dir.parent)}")
    print(f"📄 创建文件: {app_store_path.relative_to(frontend_dir.parent)}")
    print(f"📄 创建文件: {store_index_path.relative_to(frontend_dir.parent)}")
    
    return True

def create_assets_styles(frontend_dir):
    """创建样式文件"""
    # 变量文件
    variables_content = '''// 主题颜色
$primary-color: #409EFF;
$success-color: #67C23A;
$warning-color: #E6A23C;
$danger-color: #F56C6C;
$info-color: #909399;

// 文本颜色
$text-primary: #303133;
$text-regular: #606266;
$text-secondary: #909399;
$text-placeholder: #C0C4CC;

// 背景颜色
$bg-color: #f0f2f5;
$bg-color-light: #f5f7fa;
$bg-color-lighter: #fafafa;

// 边框颜色
$border-color-base: #DCDFE6;
$border-color-light: #E4E7ED;
$border-color-lighter: #EBEEF5;
$border-color-extra-light: #F2F6FC;

// 边框圆角
$border-radius-base: 4px;
$border-radius-small: 2px;
$border-radius-round: 20px;
$border-radius-circle: 100%;

// 阴影
$box-shadow-base: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04);
$box-shadow-light: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

// 间距
$spacing-xs: 8px;
$spacing-sm: 12px;
$spacing-base: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;

// 字体
$font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
  'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
$font-size-xs: 12px;
$font-size-sm: 13px;
$font-size-base: 14px;
$font-size-lg: 16px;
$font-size-xl: 18px;
$font-size-xxl: 20px;

// 行高
$line-height-base: 1.5;
'''
    
    # 全局样式
    global_style_content = '''@import './variables.scss';

// 全局重置
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: $font-family;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: $text-primary;
  background-color: $bg-color;
}

#app {
  height: 100%;
}

// 滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
  
  &:hover {
    background: #a8a8a8;
  }
}

// 工具类
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }
.text-primary { color: $primary-color; }
.text-success { color: $success-color; }
.text-warning { color: $warning-color; }
.text-danger { color: $danger-color; }
.text-info { color: $info-color; }

.mt-1 { margin-top: $spacing-xs; }
.mt-2 { margin-top: $spacing-sm; }
.mt-3 { margin-top: $spacing-base; }
.mt-4 { margin-top: $spacing-lg; }
.mt-5 { margin-top: $spacing-xl; }

.mb-1 { margin-bottom: $spacing-xs; }
.mb-2 { margin-bottom: $spacing-sm; }
.mb-3 { margin-bottom: $spacing-base; }
.mb-4 { margin-bottom: $spacing-lg; }
.mb-5 { margin-bottom: $spacing-xl; }

.ml-1 { margin-left: $spacing-xs; }
.ml-2 { margin-left: $spacing-sm; }
.ml-3 { margin-left: $spacing-base; }
.ml-4 { margin-left: $spacing-lg; }
.ml-5 { margin-left: $spacing-xl; }

.mr-1 { margin-right: $spacing-xs; }
.mr-2 { margin-right: $spacing-sm; }
.mr-3 { margin-right: $spacing-base; }
.mr-4 { margin-right: $spacing-lg; }
.mr-5 { margin-right: $spacing-xl; }

.p-1 { padding: $spacing-xs; }
.p-2 { padding: $spacing-sm; }
.p-3 { padding: $spacing-base; }
.p-4 { padding: $spacing-lg; }
.p-5 { padding: $spacing-xl; }

.flex { display: flex; }
.flex-column { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-around { justify-content: space-around; }
.justify-end { justify-content: flex-end; }
.align-center { align-items: center; }
.align-start { align-items: flex-start; }
.align-end { align-items: flex-end; }
.flex-1 { flex: 1; }
.flex-auto { flex: auto; }

// 表单相关
.form-container {
  background: white;
  padding: $spacing-lg;
  border-radius: $border-radius-base;
  box-shadow: $box-shadow-base;
  
  .form-title {
    margin-bottom: $spacing-lg;
    padding-bottom: $spacing-sm;
    border-bottom: 1px solid $border-color-light;
    font-size: $font-size-xl;
    font-weight: 600;
  }
}

// 表格相关
.table-container {
  background: white;
  border-radius: $border-radius-base;
  box-shadow: $box-shadow-base;
  padding: $spacing-base;
  
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-base;
    
    .table-title {
      font-size: $font-size-lg;
      font-weight: 600;
    }
  }
}
'''
    
    # 写入文件
    variables_path = frontend_dir / "src" / "assets" / "styles" / "variables.scss"
    with open(variables_path, "w", encoding="utf-8") as f:
        f.write(variables_content)
    
    global_style_path = frontend_dir / "src" / "assets" / "styles" / "global.scss"
    with open(global_style_path, "w", encoding="utf-8") as f:
        f.write(global_style_content)
    
    # 创建main.js中导入的样式文件
    main_style_path = frontend_dir / "src" / "assets" / "styles" / "index.scss"
    with open(main_style_path, "w", encoding="utf-8") as f:
        f.write('''@import './global.scss';
''')
    
    print(f"📄 创建文件: {variables_path.relative_to(frontend_dir.parent)}")
    print(f"📄 创建文件: {global_style_path.relative_to(frontend_dir.parent)}")
    print(f"📄 创建文件: {main_style_path.relative_to(frontend_dir.parent)}")
    
    return True

def main():
    """主函数"""
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = input("请输入项目根目录路径 (直接回车使用当前目录): ").strip()
    
    if not base_dir:
        base_dir = "."
    
    print("超市库存管理系统 - 第四阶段：前端页面开发")
    print("=" * 60)
    
    try:
        # 1. 创建项目结构
        frontend_dir = create_vue_project_structure(base_dir)
        
        # 2. 创建配置文件
        print("\n🔧 创建配置文件:")
        create_package_json(frontend_dir)
        create_vite_config(frontend_dir)
        create_html_template(frontend_dir)
        
        # 3. 创建应用代码
        print("\n💻 创建应用代码:")
        create_main_js(frontend_dir)
        create_app_vue(frontend_dir)
        
        # 4. 创建API配置
        print("\n🔌 创建API配置:")
        create_api_config(frontend_dir)
        
        # 5. 创建路由配置
        print("\n🛣️ 创建路由配置:")
        create_router_config(frontend_dir)
        
        # 6. 创建状态管理
        print("\n🗂️ 创建状态管理:")
        create_store_config(frontend_dir)
        
        # 7. 创建样式文件
        print("\n🎨 创建样式文件:")
        create_assets_styles(frontend_dir)
        
        print("\n" + "=" * 60)
        print("✅ 前端项目创建完成!")
        print("=" * 60)
        
        # 显示项目结构
        project_structure = '''
📁 项目结构:
frontend/
├── package.json             # 项目配置
├── vite.config.js          # 构建配置
├── index.html              # HTML模板
└── src/
    ├── main.js             # 应用入口
    ├── App.vue             # 根组件
    ├── api/                # API接口
    │   ├── index.js        # axios配置
    │   ├── auth.js         # 认证API
    │   ├── user.js         # 用户API
    │   ├── product.js      # 商品API
    │   └── operation.js    # 运营API
    ├── assets/             # 静态资源
    │   └── styles/         # 样式文件
    │       ├── variables.scss
    │       ├── global.scss
    │       └── index.scss
    ├── components/         # 公共组件
    │   ├── layout/         # 布局组件
    │   ├── common/         # 通用组件
    │   └── charts/         # 图表组件
    ├── router/             # 路由配置
    │   └── index.js
    ├── stores/             # 状态管理
    │   ├── index.js
    │   ├── auth.js         # 认证状态
    │   └── app.js          # 应用状态
    ├── utils/              # 工具函数
    └── views/              # 页面视图
        ├── auth/           # 认证页面
        ├── dashboard/      # 仪表板
        ├── users/          # 用户管理
        ├── products/       # 商品管理
        ├── operations/     # 运营管理
        └── settings/       # 系统设置
        '''
        
        print(project_structure)
        
        print("\n🚀 下一步操作:")
        print("1. 安装依赖:")
        print("   cd frontend")
        print("   npm install  # 或使用 pnpm install / yarn install")
        print("\n2. 启动开发服务器:")
        print("   npm run dev")
        print("\n3. 访问前端应用:")
        print("   http://localhost:3000")
        print("\n4. 确保后端服务器正在运行:")
        print("   cd backend")
        print("   python manage.py runserver")
        print("\n5. 开始开发具体页面组件")
        
    except Exception as e:
        print(f"\n❌ 创建过程中出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())