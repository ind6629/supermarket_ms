<template>
  <div id="app">
    <!-- 登录页不需要侧边栏，仪表板页需要 -->
    <el-container v-if="!$route.meta.requiresAuth" class="login-layout-wrap">
      <router-view />
    </el-container>
    <el-container v-else>
      <el-aside width="200px" class="sidebar">
        <div class="logo">超市库存管理系统</div>
        <el-menu :default-active="$route.path" class="sidebar-menu" router>
          <template v-for="menu in visibleMenus">
            <el-menu-item v-if="!menu.children" :key="menu.index" :index="menu.index">
              <el-icon><component :is="menu.icon" /></el-icon>
              <span>{{ menu.label }}</span>
            </el-menu-item>
            <el-sub-menu v-else :key="menu.index + ''" :index="menu.index">
              <template #title>
                <el-icon><component :is="menu.icon" /></el-icon>
                <span>{{ menu.label }}</span>
              </template>
              <el-menu-item v-for="child in menu.children" :key="child.index" :index="child.index">
                {{ child.label }}
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-icon @click="toggleSidebar"><Menu /></el-icon>
            <span>超市库存管理系统</span>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="32" :src="avatarUrl">
                  <el-icon><User /></el-icon>
                </el-avatar>
                {{ displayUserName }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="theme">{{
                    isDark ? '浅色模式' : '深色模式'
                  }}</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import {
  Menu,
  House,
  ShoppingBag,
  Van,
  DataAnalysis,
  User,
  Document,
  OfficeBuilding,
} from '@element-plus/icons-vue'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from './stores/auth'
import { ROLE, hasRouteAccess } from '@/utils/permissions'

const router = useRouter()
const authStore = useAuthStore()
const isCollapse = ref(false)
const isDark = ref(localStorage.getItem('sims-theme') === 'dark')

const applyTheme = (dark) => {
  isDark.value = dark
  if (dark) {
    document.documentElement.setAttribute('data-theme', 'dark')
    localStorage.setItem('sims-theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
    localStorage.setItem('sims-theme', 'light')
  }
}
// 初始化侧边栏时应用已保存的主题
if (isDark.value) {
  document.documentElement.setAttribute('data-theme', 'dark')
}
const displayUserName = computed(() => authStore.userName || '管理员')

const avatarUrl = computed(() => {
  const u = authStore.user
  if (!u?.avatar) return ''
  const path = u.avatar
  if (path.startsWith('http')) return path
  return `${window.location.origin}/media/${path.replace(/^\//, '')}`
})
const menuList = [
  {
    index: '/dashboard',
    label: '仪表板',
    icon: House,
    allowedRoles: [
      ROLE.SUPER_ADMIN,
      ROLE.ADMIN,
      ROLE.INVENTORY_MANAGER,
      ROLE.FINANCE,
      ROLE.CASHIER,
    ],
  },
  {
    index: 'product',
    label: '商品管理',
    icon: ShoppingBag,
    children: [
      {
        index: '/products',
        label: '商品列表',
        allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
      },
      {
        index: '/categories',
        label: '分类管理',
        allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
      },
      {
        index: '/inventory',
        label: '库存管理',
        allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
      },
      {
        index: '/warehouses',
        label: '仓库管理',
        allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
      },
    ],
  },
  {
    index: '/suppliers',
    label: '供货商管理',
    icon: Van,
    allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
  },
  {
    index: '/supplier-records',
    label: '供货记录',
    icon: OfficeBuilding,
    allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
  },
  {
    index: 'analysis',
    label: '统计分析',
    icon: DataAnalysis,
    children: [
      {
        index: '/sales-analysis',
        label: '销售分析',
        allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.FINANCE],
      },
    ],
  },
  {
    index: '/users',
    label: '用户管理',
    icon: User,
    allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN],
  },
  {
    index: '/operation-log',
    label: '操作日志',
    icon: Document,
    allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN],
  },
]

const visibleMenus = computed(() =>
  menuList
    .map((menu) => {
      if (!menu.children) {
        return hasRouteAccess(authStore.userRole, menu.allowedRoles) ? menu : null
      }

      const children = menu.children.filter((child) =>
        hasRouteAccess(authStore.userRole, child.allowedRoles)
      )
      return children.length ? { ...menu, children } : null
    })
    .filter(Boolean)
)

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/profile')
    return
  }

  if (command === 'theme') {
    applyTheme(!isDark.value)
    ElMessage.success(isDark.value ? '已切换为深色模式' : '已切换为浅色模式')
    return
  }

  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      })

      await authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('退出登录失败')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
#app {
  height: 100%;
  width: 100%;
}

.login-layout-wrap {
  width: 100%;
  min-height: 100vh;
}
.login-layout-wrap > * {
  width: 100%;
  min-height: 100vh;
}

.el-container {
  height: 100%;
}

.sidebar {
  background: linear-gradient(180deg, $primary-dark-color 0%, $primary-color 100%);
  color: #fff;
  transition: width 0.3s ease;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: $font-size-large + 2px;
  font-weight: 600;
  background-color: $primary-dark-color;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  letter-spacing: 0.5px;
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

/* 默认菜单项：提高对比度，使文字与图标更清晰 */
.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  color: rgba(255, 255, 255, 0.92);
  height: 50px;
  line-height: 50px;
  font-size: $font-size-medium;
  font-weight: 500;
}

.sidebar-menu :deep(.el-menu-item .el-icon),
.sidebar-menu :deep(.el-sub-menu__title .el-icon) {
  color: rgba(255, 255, 255, 0.92);
  font-size: 18px;
}

/* 激活状态：更醒目的高亮 */
.sidebar-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 600;
}

.sidebar-menu .el-menu-item.is-active :deep(.el-icon) {
  color: #fff;
}

/* hover 状态 */
.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background-color: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.sidebar-menu .el-menu-item:hover :deep(.el-icon),
.sidebar-menu .el-sub-menu__title:hover :deep(.el-icon) {
  color: #fff;
}

/* 子菜单展开时，父级标题保持醒目 */
.sidebar-menu :deep(.el-sub-menu.is-opened > .el-sub-menu__title) {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.sidebar-menu :deep(.el-sub-menu.is-opened > .el-sub-menu__title .el-icon) {
  color: #fff;
}

/* 子菜单容器：保持深色背景 */
.sidebar-menu :deep(.el-sub-menu .el-menu) {
  background-color: rgba(0, 0, 0, 0.2) !important;
}

/* 子菜单项：默认状态，白字清晰可读 */
.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  min-width: unset;
  background-color: transparent !important;
  color: rgba(255, 255, 255, 0.95) !important;
  height: 44px;
  line-height: 44px;
  padding-left: 48px !important;
}

/* 子菜单 hover：明显的浅色高亮 */
.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: #fff !important;
}

/* 子菜单激活状态：与主菜单一致的高亮 */
.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.25) !important;
  color: #fff !important;
  font-weight: 600;
}

/* 子菜单展开箭头：消除视觉异常，统一白色 */
.sidebar-menu :deep(.el-sub-menu__icon-arrow) {
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
}

/* 消除菜单项可能的边框/轮廓造成的视觉异常 */
.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  border: none !important;
  outline: none;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--sims-card-bg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0 $spacing-large;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  color: var(--sims-header-text);
}

.header-left .el-icon {
  font-size: 20px;
  margin-right: $spacing-small;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.header-left .el-icon:hover {
  transform: scale(1.1);
}

.header-left span {
  font-size: $font-size-large;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: $spacing-small $spacing-medium;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.user-info:hover {
  background-color: $border-color-lighter;
}

.user-info .el-avatar {
  margin-right: $spacing-small;
  background-color: $primary-light-color;
  color: #fff;
}

.el-main {
  background-color: var(--sims-page-bg);
  padding: $spacing-medium;
}
</style>