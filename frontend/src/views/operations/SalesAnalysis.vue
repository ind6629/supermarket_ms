<template>
  <div class="sales-analysis-container">
    <div class="header">
      <h2>销售分析</h2>
      <div class="date-range-picker">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :shortcuts="shortcuts"
          @change="handleDateChange"
        />
      </div>
    </div>

    <div class="stat-cards">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6">
          <div class="stat-card card-sales">
            <div class="card-icon"><el-icon><Money /></el-icon></div>
            <div class="card-content">
              <div class="card-title">本月销售额</div>
              <div class="card-value">¥{{ formatCurrency(statistics.totalSales) }}</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card card-orders">
            <div class="card-icon"><el-icon><ShoppingCart /></el-icon></div>
            <div class="card-content">
              <div class="card-title">总订单数</div>
              <div class="card-value">{{ statistics.totalOrders }}</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card card-avg">
            <div class="card-icon"><el-icon><TrendCharts /></el-icon></div>
            <div class="card-content">
              <div class="card-title">平均订单额</div>
              <div class="card-value">¥{{ formatCurrency(statistics.avgOrderAmount) }}</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card card-profit">
            <div class="card-icon"><el-icon><Wallet /></el-icon></div>
            <div class="card-content">
              <div class="card-title">毛利润</div>
              <div class="card-value">¥{{ formatCurrency(statistics.grossProfit) }}</div>
              <div class="card-subtitle">毛利率 {{ statistics.grossMargin.toFixed(2) }}%</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="bottom-section">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="chart-header">
              <h3>销售趋势</h3>
            </div>
            <el-table :data="salesTrend" style="width: 100%">
              <el-table-column prop="label" label="日期" min-width="120" />
              <el-table-column prop="orderCount" label="订单数" width="90" align="center" />
              <el-table-column prop="amount" label="销售额(元)" width="130" align="center">
                <template #default="{ row }">¥{{ formatCurrency(row.amount) }}</template>
              </el-table-column>
              <el-table-column prop="avgAmount" label="均单价(元)" width="130" align="center">
                <template #default="{ row }">¥{{ formatCurrency(row.avgAmount) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>

        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="chart-header">
              <h3>支付方式分布</h3>
            </div>
            <el-table :data="paymentStats" style="width: 100%">
              <el-table-column prop="method" label="支付方式" width="120" align="center">
                <template #default="{ row }">{{ getPaymentMethodText(row.method) }}</template>
              </el-table-column>
              <el-table-column prop="count" label="订单数" width="90" align="center" />
              <el-table-column prop="amount" label="金额(元)" width="120" align="center">
                <template #default="{ row }">¥{{ formatCurrency(row.amount) }}</template>
              </el-table-column>
              <el-table-column prop="percentage" label="占比" min-width="120" align="center">
                <template #default="{ row }">{{ row.percentage.toFixed(1) }}%</template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="bottom-section">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="chart-header">
              <h3>热销商品</h3>
            </div>
            <el-table :data="topProducts" style="width: 100%">
              <el-table-column prop="name" label="商品名称" min-width="150" />
              <el-table-column prop="quantity" label="销量" width="80" align="center" />
              <el-table-column prop="amount" label="金额(元)" width="120" align="center">
                <template #default="{ row }">¥{{ formatCurrency(row.amount) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>

        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="chart-header">
              <h3>收银数据导入</h3>
            </div>
            <div class="import-panel">
              <el-upload
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :show-file-list="true"
                accept=".csv,.xls,.xlsx"
              >
                <el-button type="primary">选择文件</el-button>
              </el-upload>
              <el-button
                class="import-btn"
                type="success"
                :disabled="!selectedFile"
                :loading="importing"
                @click="handleImport"
              >
                上传并导入
              </el-button>
              <p class="import-tip">支持固定模板的 CSV / Excel 文件，导入后自动生成销售记录并更新库存。</p>
            </div>

            <el-table :data="cashImports" style="width: 100%; margin-top: 16px">
              <el-table-column prop="fileName" label="文件名" min-width="140" />
              <el-table-column prop="status" label="状态" width="100" align="center" />
              <el-table-column prop="successCount" label="成功" width="80" align="center" />
              <el-table-column prop="failCount" label="失败" width="80" align="center" />
              <el-table-column prop="importTime" label="导入时间" width="180" />
            </el-table>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
  
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Money, ShoppingCart, TrendCharts, Wallet } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import operationApi from '@/api/operation'
import { getResults } from '@/utils/adapters'

const dateRange = ref([dayjs().subtract(7, 'day').toDate(), new Date()])
const selectedFile = ref(null)
const importing = ref(false)

const statistics = reactive({
  totalSales: 0,
  totalOrders: 0,
  avgOrderAmount: 0,
  grossProfit: 0,
  grossMargin: 0,
})

const paymentStats = ref([])
const topProducts = ref([])
const salesTrend = ref([])
const cashImports = ref([])

const shortcuts = [
  {
    text: '最近一周',
    value: () => [dayjs().subtract(7, 'day').toDate(), new Date()],
  },
  {
    text: '最近一个月',
    value: () => [dayjs().subtract(30, 'day').toDate(), new Date()],
  },
  {
    text: '最近三个月',
    value: () => [dayjs().subtract(90, 'day').toDate(), new Date()],
  },
]

const formatCurrency = (value) =>
  new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0))

const getPaymentMethodText = (method) => {
  const methodMap = {
    wechat: '微信支付',
    alipay: '支付宝',
    cash: '现金',
    card: '银行卡',
    unionpay: '云闪付',
  }
  return methodMap[method] || method || '未知'
}

const getDateParams = () => ({
  start_date: dayjs(dateRange.value[0]).format('YYYY-MM-DD'),
  end_date: dayjs(dateRange.value[1]).format('YYYY-MM-DD'),
})

const fetchSummary = async () => {
  const response = await operationApi.getSalesStatistics()
  statistics.totalSales = Number(response.month_sales || 0)
  statistics.totalOrders = Number(response.total_orders || 0)
  statistics.avgOrderAmount = Number(response.avg_order_amount || 0)
  statistics.grossProfit = Number(response.gross_profit || 0)
  statistics.grossMargin = Number(response.gross_margin || 0)

  const totalPaymentAmount = (response.payment_stats || []).reduce(
    (sum, item) => sum + Number(item.total_amount || 0),
    0
  )
  paymentStats.value = (response.payment_stats || []).map((item) => ({
    method: item.payment_method,
    count: Number(item.count || 0),
    amount: Number(item.total_amount || 0),
    percentage: totalPaymentAmount ? (Number(item.total_amount || 0) / totalPaymentAmount) * 100 : 0,
  }))

  topProducts.value = (response.hot_products || []).map((item) => ({
    name: item.product__name,
    quantity: Number(item.total_quantity || 0),
    amount: Number(item.total_amount || 0),
  }))
}

const fetchTrend = async () => {
  const response = await operationApi.searchSales({
    ...getDateParams(),
    group_by: 'day',
  })

  salesTrend.value = (response.statistics || []).map((item) => ({
    label: item.sales_time__date,
    orderCount: Number(item.order_count || 0),
    amount: Number(item.total_sales || 0),
    avgAmount: Number(item.avg_amount || 0),
  }))
}

const fetchCashImports = async () => {
  const response = await operationApi.getCashImports({ page_size: 5 })
  const { list } = getResults(response)
  cashImports.value = list.map((item) => ({
    id: item.id,
    fileName: item.file_name,
    status: item.status_display,
    successCount: item.success_count,
    failCount: item.fail_count,
    importTime: item.import_time,
  }))
}

const fetchSalesData = async () => {
  try {
    await Promise.all([fetchSummary(), fetchTrend(), fetchCashImports()])
  } catch (error) {
    ElMessage.error('获取销售分析数据失败')
  }
}

const handleDateChange = () => {
  fetchTrend()
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('import_type', 'sales')
    await operationApi.uploadCashData(formData)
    ElMessage.success('收银数据导入成功')
    selectedFile.value = null
    await fetchSalesData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  fetchSalesData()
})
</script>
  
  <style lang="scss" scoped>
.sales-analysis-container {
  padding: $spacing-large; /* 使用全局间距变量 */
  background-color: var(--sims-card-bg); /* 使用全局卡片背景色 */
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05); /* 统一卡片阴影 */

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-large; /* 统一间距 */

    h2 {
      margin: 0;
      color: $text-color-primary;
      font-size: $font-size-large + 2px; /* 增大字体 */
      font-weight: 600;
    }

    .date-range-picker {
      .el-date-editor {
        width: 280px; /* 调整日期选择器宽度 */
      }
    }
  }

  .stat-cards {
    margin-bottom: $spacing-large; /* 统一间距 */

    .el-col {
      margin-bottom: $spacing-medium; /* 增加列之间的垂直间距 */
    }

    .stat-card {
      background: var(--sims-card-bg);
      border-radius: 8px;
      padding: $spacing-large; /* 统一内边距 */
      display: flex;
      align-items: center;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); /* 统一卡片阴影 */
      height: 100%;
      transition: transform 0.2s ease, box-shadow 0.2s ease;

      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
      }

      .card-icon {
        width: 56px; /* 调整图标大小 */
        height: 56px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        margin-right: $spacing-medium; /* 统一间距 */

        .el-icon {
          font-size: 32px; /* 增大图标 */
        }
      }

      .card-content {
        flex: 1;

        .card-title {
          font-size: $font-size-small;
          color: $text-color-secondary;
          margin-bottom: $spacing-small; /* 统一间距 */
        }

        .card-value {
          font-size: $font-size-large + 10px; /* 增大数值字体 */
          font-weight: 600;
          color: $text-color-primary;
          line-height: 1;
        }

        .card-subtitle {
          font-size: $font-size-extra-small;
          color: $text-color-secondary;
          margin-top: $spacing-extra-small;
        }
      }

      /* 调整统计卡片的渐变颜色，使其更符合企业风格 */
      &.card-sales .card-icon {
        background: linear-gradient(135deg, #42a5f5, #2196f3); /* 蓝色系 */
      }

      &.card-orders .card-icon {
        background: linear-gradient(135deg, #66bb6a, #43a047); /* 绿色系 */
      }

      &.card-avg .card-icon {
        background: linear-gradient(135deg, #ffa726, #fb8c00); /* 橙色系 */
      }

      &.card-profit .card-icon {
        background: linear-gradient(135deg, #ab47bc, #8e24aa); /* 紫色系 */
      }
    }
  }

  .bottom-section {
    margin-bottom: $spacing-large; /* 统一间距 */

    .el-col {
      margin-bottom: $spacing-large; /* 增加列之间的垂直间距 */
    }

    .chart-card {
      background: var(--sims-card-bg);
      border-radius: 8px;
      padding: $spacing-large; /* 统一内边距 */
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      height: 100%;

      .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $spacing-medium; /* 统一间距 */

        h3 {
          margin: 0;
          font-size: $font-size-large;
          color: $text-color-primary;
          font-weight: 600;
        }
      }

      :deep(.el-table) {
        border-radius: 8px;
        overflow: hidden;
      }
      :deep(.el-table__header-wrapper .el-table__header th) {
        background-color: var(--sims-page-bg);
        color: $text-color-primary;
        font-weight: 600;
        padding: 12px 0;
      }
      :deep(.el-table__cell) {
        padding: 10px 0;
        border-color: $border-color-lighter;
      }

      .import-panel {
        display: flex;
        flex-direction: column;
        gap: $spacing-medium;
        padding: $spacing-medium;
        background-color: var(--sims-page-bg);
        border-radius: 8px;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03);
        margin-top: $spacing-medium;

        .import-btn {
          width: 120px;
        }

        .import-tip {
          font-size: $font-size-small;
          color: $text-color-secondary;
          margin: 0;
          line-height: 1.5;
        }
      }
    }
  }
}

</style>