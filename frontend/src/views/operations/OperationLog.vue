<template>
  <div class="operation-log-container">
    <div class="table-header">
      <h2>操作日志</h2>
      <div class="header-actions">
        <el-button @click="handleExport" :icon="Download">导出日志</el-button>
        <el-button @click="handleClearLog" :icon="Delete" type="danger">清空日志</el-button>
      </div>
    </div>

    <div class="filter-container">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="操作类型">
          <el-select
            v-model="filterForm.actionType"
            placeholder="请选择操作类型"
            clearable
            @clear="handleSearch"
            style="width: 150px"
          >
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="入库" value="inventory_in" />
            <el-option label="出库" value="inventory_out" />
            <el-option label="销售" value="sale" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作用户">
          <el-input
            v-model="filterForm.username"
            placeholder="请输入用户名"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="操作模块">
          <el-select
            v-model="filterForm.modelName"
            placeholder="请选择操作模块"
            clearable
            @clear="handleSearch"
            style="width: 150px"
          >
            <el-option label="用户管理" value="User" />
            <el-option label="商品管理" value="Product" />
            <el-option label="库存管理" value="Inventory" />
            <el-option label="销售记录" value="SalesRecord" />
            <el-option label="供货商" value="Supplier" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作时间">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      :data="logList"
      v-loading="loading"
      :border="true"
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa', textAlign: 'center' }"
    >
      <el-table-column prop="id" label="ID" width="80" :align="'center'" />
      <el-table-column prop="username" label="操作用户" width="120" />
      <el-table-column prop="actionType" label="操作类型" width="100" :align="'center'">
        <template #default="{ row }">
          <el-tag :type="getActionTypeTagType(row.actionType)">
            {{ getActionTypeText(row.actionType) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="modelName" label="操作模块" width="120" :align="'center'">
        <template #default="{ row }">
          <el-tag type="info">{{ row.modelName }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="objectRepr" label="操作对象" min-width="200">
        <template #default="{ row }">
          <div class="object-cell">
            <div class="object-name">{{ row.objectRepr }}</div>
            <div v-if="row.actionDetail" class="object-detail">{{ row.actionDetail }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="ipAddress" label="IP地址" width="140" />
      <el-table-column prop="createTime" label="操作时间" width="180" />
      <el-table-column label="详情" width="80" :align="'center'">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleViewDetail(row)" :icon="View"
            >详情</el-button
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

    <!-- 日志详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="操作日志详情" width="600px">
      <el-descriptions :column="1" :border="true" title="">
        <el-descriptions-item label="ID">{{ detailData.id }}</el-descriptions-item>
        <el-descriptions-item label="操作用户">{{ detailData.username }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionTypeTagType(detailData.actionType)">
            {{ getActionTypeText(detailData.actionType) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作模块">{{ detailData.modelName }}</el-descriptions-item>
        <el-descriptions-item label="操作对象">{{ detailData.objectRepr }}</el-descriptions-item>
        <el-descriptions-item label="操作详情" v-if="detailData.actionDetail">
          {{ detailData.actionDetail }}
        </el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ detailData.ipAddress }}</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ detailData.createTime }}</el-descriptions-item>
        <el-descriptions-item label="请求参数" v-if="detailData.requestData">
          <pre class="request-data">{{ detailData.requestData }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="响应数据" v-if="detailData.responseData">
          <pre class="response-data">{{ detailData.responseData }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
  
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete, Search, Refresh, View } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import operationApi from '@/api/operation'
import { getResults } from '@/utils/adapters'

const loading = ref(false)
const detailDialogVisible = ref(false)
const detailData = ref({})
const logList = ref([])

// 过滤表单
const filterForm = reactive({
  actionType: '',
  username: '',
  modelName: '',
  dateRange: [],
})

// 分页配置
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
})

const mapLogToView = (log) => ({
  id: log.id,
  username: log.user_name || '系统',
  actionType: log.action_type,
  modelName: log.model_name,
  objectRepr: log.object_repr,
  actionDetail: log.action_detail,
  ipAddress: log.ip_address,
  userAgent: log.user_agent,
  createTime: log.create_time,
})

// 工具函数
const getActionTypeText = (actionType) => {
  const actionMap = {
    create: '创建',
    update: '更新',
    delete: '删除',
    login: '登录',
    logout: '登出',
    inventory_in: '入库',
    inventory_out: '出库',
    sale: '销售',
  }
  return actionMap[actionType] || '未知'
}

const getActionTypeTagType = (actionType) => {
  const typeMap = {
    create: 'success',
    update: 'primary',
    delete: 'danger',
    login: 'info',
    logout: 'info',
    inventory_in: 'warning',
    inventory_out: 'warning',
    sale: 'success',
  }
  return typeMap[actionType] || 'info'
}

// 事件处理函数
const handleSearch = () => {
  pagination.page = 1
  fetchLogList()
}

const handleReset = () => {
  filterForm.actionType = ''
  filterForm.username = ''
  filterForm.modelName = ''
  filterForm.dateRange = []
  pagination.page = 1
  fetchLogList()
}

const handleDateChange = () => {
  pagination.page = 1
  fetchLogList()
}

const handleExport = () => {
  ElMessage.success('导出功能开发中')
}

const handleClearLog = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有操作日志吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error',
    })
    ElMessage.warning('毕业设计版本暂不提供清空日志接口')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空日志失败')
    }
  }
}

const handleViewDetail = (row) => {
  detailData.value = row
  detailDialogVisible.value = true
}

const handleSizeChange = (size) => {
  pagination.size = size
  fetchLogList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchLogList()
}

const fetchLogList = async () => {
  loading.value = true

  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      action_type: filterForm.actionType || undefined,
      model_name: filterForm.modelName || undefined,
      search: filterForm.username || undefined,
      start_date:
        filterForm.dateRange?.length === 2 ? dayjs(filterForm.dateRange[0]).format('YYYY-MM-DD') : undefined,
      end_date:
        filterForm.dateRange?.length === 2 ? dayjs(filterForm.dateRange[1]).format('YYYY-MM-DD') : undefined,
    }

    const response = await operationApi.getOperationLogs(params)
    const { list, total } = getResults(response)
    logList.value = list.map(mapLogToView)
    pagination.total = total
  } catch (error) {
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogList()
})
</script>
  
  <style lang="scss" scoped>
.operation-log-container {
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

  .object-cell {
    .object-name {
      font-weight: 500;
      margin-bottom: $spacing-extra-small; /* 统一间距 */
      color: $text-color-primary;
    }

    .object-detail {
      font-size: $font-size-small;
      color: $text-color-secondary;
    }
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

  .request-data,
  .response-data {
    background-color: var(--sims-page-bg); /* 使用全局背景色 */
    padding: $spacing-small; /* 统一内边距 */
    border-radius: 4px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: $font-size-small;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid $border-color-light; /* 增加边框 */
  }
}
</style>