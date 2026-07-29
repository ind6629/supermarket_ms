<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapsed"
      :collapse-transition="false"
      class="sidebar-menu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <!-- Logo -->
      <div class="logo-container" :class="{ 'logo-collapse': isCollapsed }">
        <h1 v-if="!isCollapsed">超市库存管理</h1>
        <h2 v-else>SIMS</h2>
      </div>

      <!-- 菜单项 -->
      <el-menu-item index="/dashboard">
        <el-icon><DataLine /></el-icon>
        <span>仪表板</span>
      </el-menu-item>

      <el-sub-menu index="2">
        <template #title>
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </template>
        <el-menu-item index="/users">
          <el-icon><UserFilled /></el-icon>
          <span>用户列表</span>
        </el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="3">
        <template #title>
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </template>
        <el-menu-item index="/products">
          <el-icon><GoodsFilled /></el-icon>
          <span>商品列表</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/inventory">
          <el-icon><Box /></el-icon>
          <span>库存管理</span>
        </el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="4">
        <template #title>
          <el-icon><Operation /></el-icon>
          <span>运营管理</span>
        </template>
        <el-menu-item index="/suppliers">
          <el-icon><Truck /></el-icon>
          <span>供货商</span>
        </el-menu-item>
        <el-menu-item index="/sales-analysis">
          <el-icon><TrendCharts /></el-icon>
          <span>销售分析</span>
        </el-menu-item>
        <el-menu-item index="/operation-logs">
          <el-icon><Document /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>

    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <div class="navbar">
        <div class="left-container">
          <el-icon class="collapse-icon" @click="toggleSidebar">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item v-for="item in breadcrumb" :key="item.path">
              <router-link v-if="item.path" :to="item.path">{{ item.meta.title }}</router-link>
              <span v-else>{{ item.meta.title }}</span>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="right-container">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="userInfo.avatar || ''" class="avatar">
                {{ userInfo.username?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username">{{ userInfo.username || '管理员' }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 页面内容 -->
      <div class="content-container">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>
  
  <script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataLine,
  User,
  UserFilled,
  Goods,
  GoodsFilled,
  Folder,
  Box,
  Operation,
  Truck,
  TrendCharts,
  Document,
  Fold,
  Expand,
  ArrowDown,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 用户信息
const userInfo = computed(() => authStore.user || {})

// 面包屑导航
const breadcrumb = computed(() => {
  const matched = route.matched.filter((item) => item.meta && item.meta.title)
  return matched
})

// 切换侧边栏折叠
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  appStore.setSidebarCollapsed(isCollapsed.value)
}

// 处理用户操作
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      await handleLogout()
      break
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await authStore.logout()
    router.push('/login')
    ElMessage.success('退出登录成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退出登录失败:', error)
    }
  }
}

// 初始化侧边栏状态
isCollapsed.value = appStore.sidebarCollapsed
</script>
  
  <style lang="scss" scoped>
.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;

  .sidebar-menu {
    width: 256px;
    height: 100%;
    border-right: none;
    transition: width 0.3s;

    &:not(.el-menu--collapse) {
      width: 256px;
    }

    &.el-menu--collapse {
      width: 64px;
    }

    .logo-container {
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      background-color: #2b2f3a;
      overflow: hidden;
      transition: all 0.3s;

      &.logo-collapse {
        padding: 0 10px;
      }

      h1,
      h2 {
        margin: 0;
        font-weight: 600;
        line-height: 1;
        white-space: nowrap;
      }

      h1 {
        font-size: 18px;
      }

      h2 {
        font-size: 16px;
      }
    }

    .el-menu-item,
    .el-sub-menu {
      transition: background-color 0.3s;

      &:hover {
        background-color: #263445 !important;
      }

      &.is-active {
        background-color: #1f2d3d !important;
      }
    }

    .el-menu-item.is-active {
      position: relative;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background-color: #409eff;
      }
    }
  }

  .main-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .navbar {
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      background-color: white;
      border-bottom: 1px solid #e6e6e6;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);

      .left-container {
        display: flex;
        align-items: center;

        .collapse-icon {
          font-size: 20px;
          cursor: pointer;
          color: #5a5e66;
          margin-right: 20px;
          transition: color 0.3s;

          &:hover {
            color: #409eff;
          }
        }

        .breadcrumb {
          font-size: 14px;
        }
      }

      .right-container {
        .user-info {
          display: flex;
          align-items: center;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 4px;
          transition: background-color 0.3s;

          &:hover {
            background-color: #f5f7fa;
          }

          .avatar {
            margin-right: 8px;
            background-color: #409eff;
            color: white;
            font-weight: bold;
          }

          .username {
            font-size: 14px;
            color: #606266;
            margin-right: 4px;
          }
        }
      }
    }

    .content-container {
      flex: 1;
      padding: 20px;
      overflow: auto;
      background-color: #f0f2f5;

      & > * {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      }
    }
  }
}

// 页面切换动画
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>