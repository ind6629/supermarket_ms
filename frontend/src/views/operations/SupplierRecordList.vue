<template>
  <div class="supplier-record-list-container">
    <div class="table-header">
      <h2>供货记录管理</h2>
    </div>

    <div class="filter-container">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="供货商">
          <el-select
            v-model="filterForm.supplierId"
            placeholder="请选择供货商"
            clearable
            filterable
            style="width: 220px"
            @clear="handleSearch"
          >
            <el-option
              v-for="item in supplierOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select
            v-model="filterForm.warehouseId"
            placeholder="请选择仓库"
            clearable
            style="width: 180px"
            @clear="handleSearch"
          >
            <el-option
              v-for="item in warehouseOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关键字">
          <el-input
            v-model="filterForm.keyword"
            placeholder="商品名称/订单号/备注"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      :data="recordList"
      v-loading="loading"
      border
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa', textAlign: 'center' }"
    >
      <el-table-column prop="code" label="入库单号" width="160" />
      <el-table-column prop="supplierName" label="供货商" min-width="160" />
      <el-table-column prop="productName" label="商品名称" min-width="150" />
      <el-table-column prop="warehouseName" label="仓库" width="120" align="center" />
      <el-table-column prop="quantity" label="数量" width="90" align="center" />
      <el-table-column prop="unitPrice" label="单价(元)" width="100" align="center" />
      <el-table-column prop="totalAmount" label="金额(元)" width="120" align="center" />
      <el-table-column prop="relatedOrder" label="关联单号" width="150" />
      <el-table-column prop="transactionTime" label="入库时间" width="180" />
      <el-table-column prop="remark" label="备注" min-width="180" />
    </el-table>

    <div class="summary-bar">
      <span>当前筛选共 {{ summary.count }} 条记录</span>
      <span>当前页合计数量 {{ summary.quantity }}</span>
      <span>当前页合计金额 ¥{{ summary.amount.toFixed(2) }}</span>
    </div>

    <div class="pagination-container">
      <el-pagination
        :current-page="pagination.page"
        :page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import operationApi from '@/api/operation'
import productApi from '@/api/product'
import { getResults, mapSupplierToView } from '@/utils/adapters'

const loading = ref(false)
const recordList = ref([])
const supplierOptions = ref([])
const warehouseOptions = ref([])

const filterForm = reactive({
  supplierId: '',
  warehouseId: '',
  keyword: '',
  dateRange: [],
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
})

const summary = computed(() => ({
  count: pagination.total,
  quantity: recordList.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0),
  amount: recordList.value.reduce((sum, item) => sum + Number(item.totalAmount || 0), 0),
}))

const mapRecordToView = (item) => ({
  id: item.id,
  code: item.code,
  supplierName: item.supplier_name || '未关联供货商',
  productName: item.product_name || '',
  warehouseName: item.warehouse_name || '',
  quantity: Number(item.quantity || 0),
  unitPrice: Number(item.unit_price || 0).toFixed(2),
  totalAmount: Number(item.total_amount || 0).toFixed(2),
  relatedOrder: item.related_order || '-',
  transactionTime: item.transaction_time || '',
  remark: item.remark || '',
})

const fetchSupplierOptions = async () => {
  const response = await productApi.getSuppliers({ page_size: 100, status: 1 })
  const { list } = getResults(response)
  supplierOptions.value = list.map(mapSupplierToView)
}

const fetchWarehouseOptions = async () => {
  const response = await productApi.getWarehouses({ page_size: 100, status: 1 })
  const { list } = getResults(response)
  warehouseOptions.value = list
}

const fetchRecordList = async () => {
  loading.value = true
  try {
    const response = await operationApi.getInventoryTransactions({
      page: pagination.page,
      page_size: pagination.size,
      transaction_type: 'purchase_in',
      related_supplier: filterForm.supplierId || undefined,
      warehouse: filterForm.warehouseId || undefined,
      search: filterForm.keyword || undefined,
      start_date: filterForm.dateRange?.[0] || undefined,
      end_date: filterForm.dateRange?.[1] || undefined,
    })
    const { list, total } = getResults(response)
    recordList.value = list.map(mapRecordToView)
    pagination.total = total
  } catch (error) {
    ElMessage.error('获取供货记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchRecordList()
}

const handleReset = () => {
  filterForm.supplierId = ''
  filterForm.warehouseId = ''
  filterForm.keyword = ''
  filterForm.dateRange = []
  pagination.page = 1
  fetchRecordList()
}

const handleSizeChange = (size) => {
  pagination.size = size
  fetchRecordList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchRecordList()
}

onMounted(async () => {
  try {
    await Promise.all([fetchSupplierOptions(), fetchWarehouseOptions()])
    await fetchRecordList()
  } catch (error) {
    ElMessage.error('初始化供货记录页面失败')
  }
})
</script>

<style scoped>
.supplier-record-list-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.table-header {
  margin-bottom: 20px;
}

.table-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.filter-container {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 8px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03);
}

/* 表格整体与 Element Plus 内部样式需用 :deep 放在顶层 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header-wrapper .el-table__header th) {
  background-color: #f5f7fa;
  color: #303133;
  font-weight: 600;
  padding: 12px 0;
}

:deep(.el-table__cell) {
  padding: 10px 0;
  border-color: #ebeef5;
}

.summary-bar {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  color: #606266;
  font-size: 14px;
  background-color: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03);
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

:deep(.el-dialog__body) {
  padding: 16px 20px;
}
:deep(.el-dialog__footer) {
  border-top: 1px solid #ebeef5;
  padding: 16px 20px;
}
:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}
</style>
