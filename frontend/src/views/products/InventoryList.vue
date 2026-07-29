<template>
  <div class="inventory-list-container">
    <div class="table-header">
      <h2>库存管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleInventoryIn" :icon="Plus">入库</el-button>
        <el-button type="warning" @click="handleInventoryOut" :icon="Minus">出库</el-button>
        <el-button @click="handleExport" :icon="Download">导出</el-button>
      </div>
    </div>

    <div class="filter-container">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="商品名称">
          <el-input
            v-model="filterForm.productName"
            placeholder="请输入商品名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="仓库">
          <el-select
            v-model="filterForm.warehouse"
            placeholder="请选择仓库"
            clearable
            @clear="handleSearch"
            style="width: 150px"
          >
            <el-option
              v-for="warehouse in warehouseOptions"
              :key="warehouse.id"
              :label="warehouse.name"
              :value="warehouse.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="库存状态">
          <el-select
            v-model="filterForm.stockStatus"
            placeholder="请选择库存状态"
            clearable
            @clear="handleSearch"
            style="width: 120px"
          >
            <el-option label="库存充足" value="enough" />
            <el-option label="库存不足" value="low" />
            <el-option label="库存超量" value="over" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="alert-overview">
      <el-alert
        :title="`低库存 ${alertSummary.lowStockCount} 项，超储 ${alertSummary.overstockCount} 项`"
        type="warning"
        :closable="false"
        show-icon
      />
      <div v-if="alertSummary.lowStockList.length" class="alert-tags">
        <el-tag
          v-for="item in alertSummary.lowStockList"
          :key="`${item.product_id}-${item.warehouse_name}`"
          type="danger"
        >
          {{ item.product_name }} / {{ item.warehouse_name }} / 当前 {{ item.current_stock }}
        </el-tag>
      </div>
    </div>

    <el-table
      :data="inventoryList"
      v-loading="loading"
      border
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa', textAlign: 'center' }"
    >
      <el-table-column prop="productCode" label="商品编码" width="120" />
      <el-table-column prop="productName" label="商品名称" min-width="150" />
      <el-table-column prop="warehouse" label="仓库" width="100">
        <template #default="{ row }">{{ row.warehouse }}</template>
      </el-table-column>
      <el-table-column prop="currentStock" label="当前库存" width="100" :align="'center'" />
      <el-table-column prop="availableStock" label="可用库存" width="100" :align="'center'" />
      <el-table-column prop="lockedStock" label="锁定库存" width="100" :align="'center'" />
      <el-table-column prop="minStock" label="最小库存" width="100" :align="'center'" />
      <el-table-column prop="maxStock" label="最大库存" width="100" :align="'center'" />
      <el-table-column prop="stockStatus" label="库存状态" width="120" :align="'center'">
        <template #default="{ row }">
          <el-tag :type="getStockStatusTagType(row.stockStatus)">
            {{ getStockStatusText(row.stockStatus) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="最后更新时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right" :align="'center'">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleAdjustStock(row)" :icon="Edit"
            >调整库存</el-button
          >
          <el-button type="info" link size="small" @click="handleViewLog(row)" :icon="Document"
            >查看记录</el-button
          >
        </template>
      </el-table-column>
    </el-table>

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

    <!-- 入库对话框 -->
    <el-dialog
      v-model="inDialogVisible"
      title="商品入库"
      width="500px"
      :close-on-click-modal="true"
    >
      <el-form ref="inFormRef" :model="inForm" :rules="inRules" label-width="100px">
        <el-form-item label="商品" prop="productId">
          <el-select
            v-model="inForm.productId"
            placeholder="请选择商品"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="product in productOptions"
              :key="product.id"
              :label="`${product.name} (${product.code})`"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库" prop="warehouseId">
          <el-select v-model="inForm.warehouseId" placeholder="请选择仓库" style="width: 100%">
            <el-option
              v-for="warehouse in warehouseOptions"
              :key="warehouse.id"
              :label="warehouse.name"
              :value="warehouse.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="供货商" prop="relatedSupplierId">
          <el-select
            v-model="inForm.relatedSupplierId"
            placeholder="请选择供货商"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="supplier in supplierOptions"
              :key="supplier.id"
              :label="supplier.name"
              :value="supplier.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="入库数量" prop="quantity">
          <el-input-number
            v-model="inForm.quantity"
            :min="1"
            :max="9999"
            controls-position="right"
            placeholder="请输入入库数量"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="入库单价" prop="unitPrice">
          <el-input-number
            v-model="inForm.unitPrice"
            :min="0.01"
            :step="0.01"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="入库原因" prop="reason">
          <el-input
            v-model="inForm.reason"
            type="textarea"
            placeholder="请输入入库原因"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="inForm.operator" placeholder="请输入操作人姓名" style="width: 200px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="inDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleInSubmit" :loading="inSubmitting">
            确认入库
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 出库对话框 -->
    <el-dialog
      v-model="outDialogVisible"
      title="商品出库"
      width="500px"
      :close-on-click-modal="true"
    >
      <el-form ref="outFormRef" :model="outForm" :rules="outRules" label-width="100px">
        <el-form-item label="商品" prop="productId">
          <el-select
            v-model="outForm.productId"
            placeholder="请选择商品"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="product in productOptions"
              :key="product.id"
              :label="`${product.name} (${product.code})`"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库" prop="warehouseId">
          <el-select v-model="outForm.warehouseId" placeholder="请选择仓库" style="width: 100%">
            <el-option
              v-for="warehouse in warehouseOptions"
              :key="warehouse.id"
              :label="warehouse.name"
              :value="warehouse.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="出库数量" prop="quantity">
          <el-input-number
            v-model="outForm.quantity"
            :min="1"
            :max="9999"
            controls-position="right"
            placeholder="请输入出库数量"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="出库单价" prop="unitPrice">
          <el-input-number
            v-model="outForm.unitPrice"
            :min="0.01"
            :step="0.01"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="出库原因" prop="reason">
          <el-select v-model="outForm.reason" placeholder="请选择出库原因" style="width: 100%">
            <el-option label="销售出库" value="sales" />
            <el-option label="退货出库" value="return" />
            <el-option label="损耗出库" value="loss" />
            <el-option label="调拨出库" value="transfer" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作人" prop="operator">
          <el-input
            v-model="outForm.operator"
            placeholder="请输入操作人姓名"
            style="width: 200px"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="outDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleOutSubmit" :loading="outSubmitting">
            确认出库
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 调整库存对话框 -->
    <el-dialog
      v-model="adjustDialogVisible"
      title="调整库存"
      width="500px"
      :close-on-click-modal="true"
    >
      <el-form ref="adjustFormRef" :model="adjustForm" :rules="adjustRules" label-width="100px">
        <el-form-item label="商品">
          <el-input v-model="adjustForm.productName" readonly style="width: 100%" />
        </el-form-item>
        <el-form-item label="仓库">
          <el-input v-model="adjustForm.warehouse" readonly style="width: 100%" />
        </el-form-item>
        <el-form-item label="当前库存">
          <el-input v-model="adjustForm.currentStock" readonly style="width: 100%" />
        </el-form-item>
        <el-form-item label="调整数量" prop="quantity">
          <el-input-number
            v-model="adjustForm.quantity"
            :min="-9999"
            :max="9999"
            controls-position="right"
            placeholder="请输入调整数量（正数增加，负数减少）"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="调整单价" prop="unitPrice">
          <el-input-number
            v-model="adjustForm.unitPrice"
            :min="0.01"
            :step="0.01"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="调整后库存">
          <el-input v-model="adjustForm.newStock" readonly style="width: 100%" />
        </el-form-item>
        <el-form-item label="调整原因" prop="reason">
          <el-input
            v-model="adjustForm.reason"
            type="textarea"
            placeholder="请输入调整原因"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="adjustDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAdjustSubmit" :loading="adjustSubmitting">
            确认调整
          </el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="transactionDialogVisible" title="库存变动记录" width="760px">
      <el-table v-loading="transactionLoading" :data="transactionLogs" border style="width: 100%">
        <el-table-column prop="transactionTime" label="时间" width="180" />
        <el-table-column prop="transactionTypeDisplay" label="类型" width="120" align="center" />
        <el-table-column prop="quantity" label="数量" width="90" align="center" />
        <el-table-column prop="unitPrice" label="单价" width="100" align="center" />
        <el-table-column prop="totalAmount" label="金额" width="120" align="center" />
        <el-table-column prop="remark" label="备注" min-width="180" />
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="transactionDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
  
<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Minus, Download, Search, Refresh, Edit, Document } from '@element-plus/icons-vue'
import productApi from '@/api/product'
import operationApi from '@/api/operation'
import {
  getResults,
  mapInventoryToView,
  mapProductToView,
  mapSupplierToView,
} from '@/utils/adapters'

const loading = ref(false)
const inDialogVisible = ref(false)
const outDialogVisible = ref(false)
const adjustDialogVisible = ref(false)
const inSubmitting = ref(false)
const outSubmitting = ref(false)
const adjustSubmitting = ref(false)
const inFormRef = ref()
const outFormRef = ref()
const adjustFormRef = ref()
const inventoryList = ref([])
const warehouseOptions = ref([])
const productOptions = ref([])
const supplierOptions = ref([])
const transactionDialogVisible = ref(false)
const transactionLoading = ref(false)
const transactionLogs = ref([])
const alertSummary = reactive({
  lowStockCount: 0,
  overstockCount: 0,
  lowStockList: [],
})

// 过滤表单
const filterForm = reactive({
  productName: '',
  warehouse: '',
  stockStatus: '',
})

// 分页配置
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
})

const inForm = reactive({
  productId: '',
  warehouseId: '',
  relatedSupplierId: '',
  quantity: 1,
  reason: '',
  operator: 'admin',
  unitPrice: 0.01,
})

const inRules = {
  productId: [{ required: true, message: '请选择商品', trigger: 'change' }],
  warehouseId: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  relatedSupplierId: [{ required: true, message: '请选择供货商', trigger: 'change' }],
  quantity: [
    { required: true, message: '请输入入库数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '入库数量必须大于0', trigger: 'blur' },
  ],
  unitPrice: [{ required: true, message: '请输入单价', trigger: 'blur' }],
}

const outForm = reactive({
  productId: '',
  warehouseId: '',
  quantity: 1,
  reason: 'sales',
  operator: 'admin',
  unitPrice: 0.01,
})

const outRules = {
  productId: [{ required: true, message: '请选择商品', trigger: 'change' }],
  warehouseId: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  quantity: [
    { required: true, message: '请输入出库数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '出库数量必须大于0', trigger: 'blur' },
  ],
  unitPrice: [{ required: true, message: '请输入单价', trigger: 'blur' }],
}

const adjustForm = reactive({
  inventoryId: '',
  productId: '',
  productName: '',
  warehouseId: '',
  warehouse: '',
  currentStock: 0,
  quantity: 0,
  newStock: 0,
  reason: '',
  unitPrice: 0.01,
})

const adjustRules = {
  quantity: [{ required: true, message: '请输入调整数量', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入调整原因', trigger: 'blur' }],
  unitPrice: [{ required: true, message: '请输入单价', trigger: 'blur' }],
}

watch(
  () => adjustForm.quantity,
  (newQuantity) => {
    adjustForm.newStock = adjustForm.currentStock + (newQuantity || 0)
  }
)

const getStockStatusText = (status) => {
  const statusMap = {
    enough: '库存充足',
    low: '库存不足',
    over: '库存超量',
  }
  return statusMap[status] || '未知'
}

const getStockStatusTagType = (status) => {
  const typeMap = {
    enough: 'success',
    low: 'danger',
    over: 'warning',
  }
  return typeMap[status] || 'info'
}

const handleSearch = () => {
  pagination.page = 1
  fetchInventoryList()
}

const handleReset = () => {
  filterForm.productName = ''
  filterForm.warehouse = ''
  filterForm.stockStatus = ''
  pagination.page = 1
  fetchInventoryList()
}

const handleInventoryIn = () => {
  Object.assign(inForm, {
    productId: '',
    warehouseId: warehouseOptions.value[0]?.id || '',
    relatedSupplierId: '',
    quantity: 1,
    reason: '',
    operator: 'admin',
    unitPrice: 0.01,
  })
  inDialogVisible.value = true
}

const handleInventoryOut = () => {
  Object.assign(outForm, {
    productId: '',
    warehouseId: warehouseOptions.value[0]?.id || '',
    quantity: 1,
    reason: 'sales',
    operator: 'admin',
    unitPrice: 0.01,
  })
  outDialogVisible.value = true
}

const handleExport = () => {
  ElMessage.success('导出功能开发中')
}

const handleAdjustStock = (row) => {
  adjustForm.inventoryId = row.id
  adjustForm.productId = row.productId
  adjustForm.productName = row.productName
  adjustForm.warehouseId = row.warehouseId
  adjustForm.warehouse = row.warehouse
  adjustForm.currentStock = row.currentStock
  adjustForm.quantity = 0
  adjustForm.newStock = row.currentStock
  adjustForm.reason = ''
  adjustForm.unitPrice = 0.01
  adjustDialogVisible.value = true
}

const handleViewLog = (row) => {
  fetchInventoryTransactions(row)
}

const handleSizeChange = (size) => {
  pagination.size = size
  fetchInventoryList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchInventoryList()
}

const handleInSubmit = async () => {
  if (!inFormRef.value) return

  try {
    await inFormRef.value.validate()
    inSubmitting.value = true
    await productApi.inventoryInOut({
      transaction_type: 'purchase_in',
      product_id: inForm.productId,
      warehouse_id: inForm.warehouseId,
      related_supplier_id: inForm.relatedSupplierId,
      quantity: inForm.quantity,
      unit_price: Number(inForm.unitPrice),
      remark: inForm.reason,
    })
    ElMessage.success('入库成功')
    inDialogVisible.value = false
    await Promise.all([fetchInventoryList(), fetchInventoryAlerts()])
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '入库失败')
  } finally {
    inSubmitting.value = false
  }
}

const handleOutSubmit = async () => {
  if (!outFormRef.value) return

  try {
    await outFormRef.value.validate()
    outSubmitting.value = true
    await productApi.inventoryInOut({
      transaction_type: 'sale_out',
      product_id: outForm.productId,
      warehouse_id: outForm.warehouseId,
      quantity: outForm.quantity,
      unit_price: Number(outForm.unitPrice),
      remark: outForm.reason,
    })
    ElMessage.success('出库成功')
    outDialogVisible.value = false
    await Promise.all([fetchInventoryList(), fetchInventoryAlerts()])
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '出库失败')
  } finally {
    outSubmitting.value = false
  }
}

const handleAdjustSubmit = async () => {
  if (!adjustFormRef.value) return

  try {
    await adjustFormRef.value.validate()
    adjustSubmitting.value = true
    if (adjustForm.quantity === 0) {
      ElMessage.warning('调整数量不能为 0')
      return
    }

    await productApi.inventoryInOut({
      transaction_type: adjustForm.quantity > 0 ? 'adjust_in' : 'adjust_out',
      product_id: adjustForm.productId,
      warehouse_id: adjustForm.warehouseId,
      quantity: Math.abs(adjustForm.quantity),
      unit_price: Number(adjustForm.unitPrice),
      remark: `库存调整：${adjustForm.reason}`,
    })
    ElMessage.success('库存调整成功')
    adjustDialogVisible.value = false
    await Promise.all([fetchInventoryList(), fetchInventoryAlerts()])
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '库存调整失败')
  } finally {
    adjustSubmitting.value = false
  }
}

const fetchInventoryList = async () => {
  loading.value = true

  try {
    const response = await productApi.getInventories({
      page: pagination.page,
      page_size: pagination.size,
      product_name: filterForm.productName || undefined,
      warehouse: filterForm.warehouse || undefined,
      stock_status:
        filterForm.stockStatus === 'enough'
          ? 'normal'
          : filterForm.stockStatus === 'over'
          ? 'overstock'
          : filterForm.stockStatus || undefined,
    })
    const { list, total } = getResults(response)
    inventoryList.value = list.map(mapInventoryToView)
    pagination.total = total
  } catch (error) {
    ElMessage.error('获取库存列表失败')
  } finally {
    loading.value = false
  }
}

const fetchInventoryAlerts = async () => {
  try {
    const response = await productApi.getInventoryAlerts()
    const lowStockList = response.low_stock_alerts || []
    alertSummary.lowStockCount = lowStockList.length
    alertSummary.overstockCount = (response.overstock_alerts || []).length
    alertSummary.lowStockList = lowStockList.slice(0, 6)
  } catch (error) {
    ElMessage.error('获取库存预警失败')
  }
}

const fetchInventoryTransactions = async (row) => {
  transactionDialogVisible.value = true
  transactionLoading.value = true
  try {
    const response = await operationApi.getInventoryTransactions({
      product: row.productId,
      warehouse: row.warehouseId,
      page_size: 20,
    })
    const { list } = getResults(response)
    transactionLogs.value = list.map((item) => ({
      id: item.id,
      transactionTime: item.transaction_time,
      transactionTypeDisplay: item.transaction_type_display,
      quantity: item.quantity,
      unitPrice: item.unit_price,
      totalAmount: item.total_amount,
      remark: item.remark || item.related_order || '-',
    }))
  } catch (error) {
    transactionDialogVisible.value = false
    ElMessage.error('获取库存记录失败')
  } finally {
    transactionLoading.value = false
  }
}

const fetchProductOptions = async () => {
  const response = await productApi.getProducts({ page_size: 100, status: 1 })
  const { list } = getResults(response)
  productOptions.value = list.map(mapProductToView)
}

const fetchWarehouseOptions = async () => {
  const response = await productApi.getWarehouses({ page_size: 100, status: 1 })
  const { list } = getResults(response)
  warehouseOptions.value = list
}

const fetchSupplierOptions = async () => {
  const response = await productApi.getSuppliers({ page_size: 100, status: 1 })
  const { list } = getResults(response)
  supplierOptions.value = list.map(mapSupplierToView)
}

onMounted(async () => {
  try {
    await Promise.all([fetchProductOptions(), fetchWarehouseOptions(), fetchSupplierOptions()])
    if (!inForm.warehouseId) {
      inForm.warehouseId = warehouseOptions.value[0]?.id || ''
      outForm.warehouseId = warehouseOptions.value[0]?.id || ''
    }
    await Promise.all([fetchInventoryList(), fetchInventoryAlerts()])
  } catch (error) {
    ElMessage.error('初始化库存页面失败')
  }
})
</script>
  
  <style lang="scss" scoped>
@use 'sass:color';
.inventory-list-container {
  padding: $spacing-large; /* 使用全局间距变量 */
  background-color: var(--sims-card-bg); /* 使用全局卡片背景色 */
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05); /* 统一卡片阴影 */

  .table-header {
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

    .header-actions {
      display: flex;
      gap: $spacing-small; /* 统一间距 */
    }
  }

  .filter-container {
    margin-bottom: $spacing-large; /* 统一间距 */
    padding: $spacing-medium; /* 统一内边距 */
    background-color: var(--sims-page-bg); /* 使用全局页面背景色 */
    border-radius: 8px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03); /* 内部阴影 */
  }

  .alert-overview {
    margin-bottom: $spacing-large; /* 统一间距 */
    padding: $spacing-medium; /* 统一内边距 */
    background-color: color.adjust($warning-color, $lightness: 45%);
    border: 1px solid color.adjust($warning-color, $lightness: 30%);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: $spacing-small;

    :deep(.el-alert__title) {
      font-size: $font-size-medium;
      font-weight: 500;
      color: $text-color-primary;
    }

    :deep(.el-alert__icon) {
      font-size: 20px;
      width: 20px;
    }

    .alert-tags {
      margin-top: 0; /* 调整间距 */
      display: flex;
      flex-wrap: wrap;
      gap: $spacing-extra-small; /* 统一间距 */
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

  .pagination-container {
    margin-top: $spacing-large; /* 统一间距 */
    display: flex;
    justify-content: flex-end;
  }

  /* 对话框内表单的样式微调 */
  :deep(.el-dialog__body) {
    padding: $spacing-medium $spacing-large;
  }
  :deep(.el-dialog__footer) {
    border-top: 1px solid $border-color-lighter;
    padding: $spacing-medium $spacing-large;
  }
  :deep(.el-form-item__label) {
    color: $text-color-regular;
    font-weight: 500;
  }
}
</style>