import { defineStore } from 'pinia'
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
