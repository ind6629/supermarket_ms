import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || '')
  const userName = computed(() => user.value?.username || '')
  
  // 登录
  async function login(loginData) {
    try {
      const response = await authApi.login(loginData)

      const access = response?.tokens?.access || ''
      const refresh = response?.tokens?.refresh || ''
      const userInfo = response?.user || null

      token.value = access
      refreshToken.value = refresh
      user.value = userInfo

      if (access) {
        localStorage.setItem('token', access)
      }
      if (refresh) {
        localStorage.setItem('refresh_token', refresh)
      }
      if (userInfo) {
        localStorage.setItem('user', JSON.stringify(userInfo))
      }

      return response
    } catch (error) {
      throw error
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
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('isLoggedIn')
  }
  
  // 获取用户信息
  async function getUserInfo() {
    try {
      const response = await authApi.getUserInfo()
      user.value = response
      localStorage.setItem('user', JSON.stringify(response))
      return response
    } catch (error) {
      throw error
    }
  }
  
  return {
    token,
    refreshToken,
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
