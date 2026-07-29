<template>
  <div class="warehouse-list-container">
    <div class="table-header">
      <h2>仓库管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddWarehouse">新增仓库</el-button>
      </div>
    </div>

    <div class="filter-container">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="仓库名称">
          <el-input
            v-model="filterForm.keyword"
            placeholder="请输入仓库名称或编码"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            @clear="handleSearch"
          >
            <el-option label="启用" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      :data="warehouseList"
      v-loading="loading"
      border
      style="width: 100%"
      :header-cell-style="{ textAlign: 'center' }"
    >
      <el-table-column prop="code" label="仓库编码" width="130" />
      <el-table-column prop="name" label="仓库名称" min-width="140" />
      <el-table-column prop="address" label="地址" min-width="220" />
      <el-table-column prop="managerName" label="负责人" width="120" align="center" />
      <el-table-column prop="contactPhone" label="联系电话" width="140" align="center" />
      <el-table-column prop="capacity" label="容量(m3)" width="120" align="center" />
      <el-table-column prop="inventoryCount" label="库存记录数" width="110" align="center" />
      <el-table-column prop="status" label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button
            v-if="row.status === 1"
            type="danger"
            link
            size="small"
            @click="handleToggleStatus(row, 0)"
          >
            停用
          </el-button>
          <el-button v-else type="success" link size="small" @click="handleToggleStatus(row, 1)">
            启用
          </el-button>
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

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="560px"
      :close-on-click-modal="true"
    >
      <el-form
        ref="warehouseFormRef"
        :model="warehouseForm"
        :rules="warehouseRules"
        label-width="90px"
      >
        <el-form-item label="仓库编码" prop="code">
          <el-input
            v-model="warehouseForm.code"
            placeholder="请输入仓库编码"
            :disabled="!!warehouseForm.id"
          />
        </el-form-item>
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="仓库地址" prop="address">
          <el-input
            v-model="warehouseForm.address"
            type="textarea"
            :rows="3"
            placeholder="请输入仓库地址"
          />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select
            v-model="warehouseForm.manager"
            placeholder="请选择负责人"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="item in managerOptions"
              :key="item.id"
              :label="`${item.username}${item.roleDisplay ? ` / ${item.roleDisplay}` : ''}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="warehouseForm.contactPhone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="仓库容量">
          <el-input-number
            v-model="warehouseForm.capacity"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="warehouseForm.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="warehouseForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import productApi from '@/api/product'
import userApi from '@/api/user'
import { getResults, mapUserToView } from '@/utils/adapters'

const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const warehouseFormRef = ref()
const warehouseList = ref([])
const managerOptions = ref([])
const dialogTitle = ref('新增仓库')

const filterForm = reactive({
  keyword: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
})

const warehouseForm = reactive({
  id: '',
  code: '',
  name: '',
  address: '',
  manager: null,
  contactPhone: '',
  capacity: 0,
  status: 1,
  remark: '',
})

const warehouseRules = {
  code: [
    { required: true, message: '请输入仓库编码', trigger: 'blur' },
    { min: 2, message: '仓库编码至少2个字符', trigger: 'blur' },
  ],
  name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }],
  address: [{ required: true, message: '请输入仓库地址', trigger: 'blur' }],
}

const mapWarehouseToView = (item) => ({
  id: item.id,
  code: item.code,
  name: item.name,
  address: item.address || '',
  manager: item.manager ?? null,
  managerName: item.manager_name || '',
  contactPhone: item.contact_phone || '',
  capacity: item.capacity == null ? '' : Number(item.capacity),
  inventoryCount: Number(item.inventory_count || 0),
  status: item.status,
  remark: item.remark || '',
})

const fetchWarehouseList = async () => {
  loading.value = true
  try {
    const response = await productApi.getWarehouses({
      page: pagination.page,
      page_size: pagination.size,
      search: filterForm.keyword || undefined,
      status: filterForm.status !== '' ? filterForm.status : undefined,
    })
    const { list, total } = getResults(response)
    warehouseList.value = list.map(mapWarehouseToView)
    pagination.total = total
  } catch (error) {
    ElMessage.error('获取仓库列表失败')
  } finally {
    loading.value = false
  }
}

const fetchManagerOptions = async () => {
  try {
    const response = await userApi.getUsers({
      page_size: 100,
      status: 1,
    })
    const { list } = getResults(response)
    managerOptions.value = list.map(mapUserToView).filter((item) => [0, 1, 2].includes(item.role))
  } catch (error) {
    ElMessage.error('获取负责人列表失败')
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchWarehouseList()
}

const handleReset = () => {
  filterForm.keyword = ''
  filterForm.status = ''
  pagination.page = 1
  fetchWarehouseList()
}

const resetWarehouseForm = () => {
  Object.assign(warehouseForm, {
    id: '',
    code: '',
    name: '',
    address: '',
    manager: null,
    contactPhone: '',
    capacity: 0,
    status: 1,
    remark: '',
  })
}

const handleAddWarehouse = () => {
  dialogTitle.value = '新增仓库'
  resetWarehouseForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑仓库'
  Object.assign(warehouseForm, {
    id: row.id,
    code: row.code,
    name: row.name,
    address: row.address,
    manager: row.manager,
    contactPhone: row.contactPhone,
    capacity: row.capacity === '' ? 0 : row.capacity,
    status: row.status,
    remark: row.remark,
  })
  dialogVisible.value = true
}

const buildPayload = () => ({
  code: warehouseForm.code,
  name: warehouseForm.name,
  address: warehouseForm.address,
  manager: warehouseForm.manager || null,
  contact_phone: warehouseForm.contactPhone || '',
  capacity: warehouseForm.capacity || 0,
  status: warehouseForm.status,
  remark: warehouseForm.remark || '',
})

const handleSubmit = async () => {
  if (!warehouseFormRef.value) return

  try {
    await warehouseFormRef.value.validate()
    submitting.value = true
    const payload = buildPayload()
    if (warehouseForm.id) {
      await productApi.updateWarehouse(warehouseForm.id, payload)
      ElMessage.success('仓库更新成功')
    } else {
      await productApi.createWarehouse(payload)
      ElMessage.success('仓库新增成功')
    }
    dialogVisible.value = false
    fetchWarehouseList()
  } catch (error) {
    const errorData = error?.response?.data || {}
    const firstError = Object.values(errorData)[0]
    ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError || '保存仓库失败')
  } finally {
    submitting.value = false
  }
}

const handleToggleStatus = async (row, status) => {
  try {
    await ElMessageBox.confirm(`确定要${status === 1 ? '启用' : '停用'}该仓库吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await productApi.updateWarehouse(row.id, {
      code: row.code,
      name: row.name,
      address: row.address,
      manager: row.manager || null,
      contact_phone: row.contactPhone || '',
      capacity: row.capacity || 0,
      status,
      remark: row.remark || '',
    })
    ElMessage.success(`仓库已${status === 1 ? '启用' : '停用'}`)
    fetchWarehouseList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('更新仓库状态失败')
    }
  }
}

const handleSizeChange = (size) => {
  pagination.size = size
  fetchWarehouseList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchWarehouseList()
}

onMounted(async () => {
  await Promise.all([fetchWarehouseList(), fetchManagerOptions()])
})
</script>

<style lang="scss" scoped>
.warehouse-list-container {
  padding: $spacing-large;
  background-color: var(--sims-card-bg);
  border-radius: 8px;
  box-shadow: var(--sims-card-shadow);

  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-large;

    h2 {
      margin: 0;
      color: var(--sims-text-primary);
      font-size: $font-size-large + 2px;
      font-weight: 600;
    }

    .header-actions {
      display: flex;
      gap: $spacing-small;
    }
  }

  .filter-container {
    margin-bottom: $spacing-large;
    padding: $spacing-medium;
    background-color: var(--sims-page-bg);
    border-radius: 8px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03);
  }

  :deep(.el-table) {
    border-radius: 8px;
    overflow: hidden;
  }

  :deep(.el-table__header-wrapper .el-table__header th) {
    background-color: var(--sims-page-bg);
    color: var(--sims-text-primary);
    font-weight: 600;
    padding: 12px 0;
  }

  :deep(.el-table__cell) {
    padding: 10px 0;
    border-color: var(--sims-card-border);
  }

  .pagination-container {
    margin-top: $spacing-large;
    display: flex;
    justify-content: flex-end;
  }

  :deep(.el-dialog__body) {
    padding: $spacing-medium $spacing-large;
  }

  :deep(.el-dialog__footer) {
    border-top: 1px solid var(--sims-card-border);
    padding: $spacing-medium $spacing-large;
  }

  :deep(.el-form-item__label) {
    color: var(--sims-text-regular);
    font-weight: 500;
  }
}
</style>
