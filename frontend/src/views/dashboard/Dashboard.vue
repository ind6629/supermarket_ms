<template>
  <div class="dashboard-container">
    <div class="welcome-section">
      <h1>欢迎使用超市库存管理系统</h1>
      <p class="welcome-text">超市管理系统，让库存管理更简单、更高效！</p>
    </div>

    <!-- 快捷操作卡片 -->
    <div class="quick-actions">
      <h3>快捷操作</h3>
      <el-row :gutter="20">
        <el-col
          v-for="action in visibleQuickActions"
          :key="action.path"
          :xs="12"
          :sm="6"
          :md="6"
          :lg="6"
          :xl="6"
        >
          <el-card shadow="hover" class="quick-card" @click="goToPage(action.path)">
            <div class="card-icon-wrap">
              <el-icon :size="32"><component :is="action.icon" /></el-icon>
            </div>
            <div class="card-content">
              <h4>{{ action.title }}</h4>
              <p>{{ action.description }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 系统统计 -->
    <div class="system-stats">
      <h3>系统概览</h3>
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
          <div class="stat-card stat-total">
            <div class="stat-content">
              <div class="stat-title">商品总数</div>
              <div class="stat-value">{{ stats.totalProducts }}</div>
              <div class="stat-trend">已启用商品档案数量</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
          <div class="stat-card stat-active">
            <div class="stat-content">
              <div class="stat-title">库存总数</div>
              <div class="stat-value">{{ stats.totalInventory }}</div>
              <div class="stat-trend">低库存预警 {{ stats.lowStockWarnings }} 项</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
          <div class="stat-card stat-warning">
            <div class="stat-content">
              <div class="stat-title">供货商数</div>
              <div class="stat-value">{{ stats.totalSuppliers }}</div>
              <div class="stat-trend">系统已接入真实数据</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
          <div class="stat-card stat-success">
            <div class="stat-content">
              <div class="stat-title">销售额(月)</div>
              <div class="stat-value">¥{{ formatCurrency(stats.monthlySales) }}</div>
              <div class="stat-trend">按销售记录自动统计</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 最近操作 -->
    <div class="recent-actions">
      <h3>最近操作</h3>
      <el-card>
        <el-table :data="recentActions" style="width: 100%">
          <el-table-column prop="time" label="时间" width="180" />
          <el-table-column prop="operator" label="操作人" width="120" />
          <el-table-column prop="action" label="操作" min-width="200" />
          <el-table-column prop="module" label="模块" width="120" />
          <template #empty>
            <el-empty description="暂无最近操作记录" :image-size="80" />
          </template>
        </el-table>
      </el-card>
    </div>
  </div>
</template>
  
<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Goods, Box, Van, TrendCharts } from '@element-plus/icons-vue'
import productApi from '@/api/product'
import operationApi from '@/api/operation'
import { getResults } from '@/utils/adapters'
import { ROLE, hasRouteAccess } from '@/utils/permissions'

const router = useRouter()
const storedUser = JSON.parse(localStorage.getItem('user') || 'null')
const currentRole = storedUser?.role

const stats = reactive({
  totalProducts: 0,
  totalInventory: 0,
  totalSuppliers: 0,
  monthlySales: 0,
  lowStockWarnings: 0,
})

const recentActions = ref([])
const quickActions = [
  {
    path: '/products',
    title: '商品管理',
    description: '管理商品信息',
    icon: Goods,
    allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
  },
  {
    path: '/inventory',
    title: '库存管理',
    description: '查看库存状态',
    icon: Box,
    allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
  },
  {
    path: '/suppliers',
    title: '供货商',
    description: '管理供货商信息',
    icon: Van,
    allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
  },
  {
    path: '/sales-analysis',
    title: '销售分析',
    description: '查看销售数据',
    icon: TrendCharts,
    allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.FINANCE],
  },
]

const visibleQuickActions = computed(() =>
  quickActions.filter((item) => hasRouteAccess(currentRole, item.allowedRoles))
)

const formatCurrency = (value) => {
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

const goToPage = (path) => {
  router.push(path)
}

const fetchDashboardData = async () => {
  try {
    const [productStats, inventorySummary, supplierResponse, salesStats, activities] =
      await Promise.all([
        productApi.getProductStatistics(),
        productApi.getInventorySummary(),
        productApi.getSuppliers({ page: 1, page_size: 1 }),
        operationApi.getSalesStatistics(),
        operationApi.getRecentActivities({ limit: 5 }),
      ])

    stats.totalProducts = Number(productStats.total_products || 0)
    stats.totalInventory = Number(inventorySummary.total_inventory_records || 0)
    stats.totalSuppliers = Number(supplierResponse.count || 0)
    stats.monthlySales = Number(salesStats.month_sales || 0)
    stats.lowStockWarnings = Number(inventorySummary.low_stock_warnings || 0)

    const activityList = Array.isArray(activities) ? activities : getResults(activities).list
    recentActions.value = activityList.map((item) => ({
      time: item.create_time,
      operator: item.user_name || '系统',
      action: item.action_detail || item.object_repr,
      module: item.model_name || '系统',
    }))
  } catch (error) {
    ElMessage.error('获取仪表板数据失败')
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>
  
<style lang="scss" scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: $spacing-large;
  padding: $spacing-medium;
  background-color: var(--sims-page-bg);
}

.welcome-section {
  background: linear-gradient(135deg, $primary-color 0%, $primary-light-color 100%);
  color: white;
  padding: $spacing-extra-large;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.welcome-section h1 {
  margin: 0 0 $spacing-medium 0;
  font-size: 22px;
  font-weight: 600;
}

.welcome-text {
  margin: 0;
  font-size: $font-size-medium;
  opacity: 0.9;
}

.quick-actions h3,
.system-stats h3,
.recent-actions h3 {
  margin: 0 0 $spacing-medium 0;
  font-size: $font-size-large;
  font-weight: 600;
  color: $text-color-primary;
}

.quick-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  background-color: var(--sims-card-bg);
  border-radius: 8px;
  box-shadow: var(--sims-card-shadow);
  overflow: hidden;
}

.quick-card :deep(.el-card__body) {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  overflow: hidden;
}

.quick-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--sims-card-shadow-hover);
}

.card-icon-wrap {
  width: 56px;
  height: 56px;
  min-width: 56px;
  min-height: 56px;
  background-color: $primary-light-color;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: $spacing-small;
  color: white;
  flex-shrink: 0;
}

.card-content h4 {
  margin: 0 0 $spacing-extra-small 0;
  font-size: $font-size-medium;
  font-weight: 600;
  color: $text-color-primary;
}

.card-content p {
  margin: 0;
  font-size: $font-size-small;
  color: $text-color-secondary;
}

.system-stats .el-row {
  margin-left: -$spacing-small !important;
  margin-right: -$spacing-small !important;
}

.system-stats .el-col {
  padding-left: $spacing-small !important;
  padding-right: $spacing-small !important;
  margin-bottom: $spacing-medium;
}

.stat-card {
  padding: $spacing-medium;
  border-radius: 8px;
  color: white;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
}

.stat-total {
  background: linear-gradient(135deg, #42a5f5, #2196f3); /* 蓝色系 */
}

.stat-active {
  background: linear-gradient(135deg, #66bb6a, #43a047); /* 绿色系 */
}

.stat-warning {
  background: linear-gradient(135deg, #ffa726, #fb8c00); /* 橙色系 */
}

.stat-success {
  background: linear-gradient(135deg, #ab47bc, #8e24aa); /* 紫色系 */
}

.stat-content {
  text-align: center;
}

.stat-title {
  font-size: $font-size-small;
  margin-bottom: $spacing-small;
  opacity: 0.9;
}

.stat-value {
  font-size: $font-size-large + 10px;
  font-weight: 600;
  margin-bottom: $spacing-extra-small;
}

.stat-trend {
  font-size: $font-size-extra-small;
  opacity: 0.8;
}

.recent-actions .el-card {
  box-shadow: var(--sims-card-shadow);
  border-radius: 8px;
}
</style>