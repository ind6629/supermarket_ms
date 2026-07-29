<template>
  <div class="supplier-list-container">
    <div class="table-header">
      <h2>供货商管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddSupplier" :icon="Plus">新增供货商</el-button>
        <el-button @click="handleExport" :icon="Download">导出</el-button>
      </div>
    </div>

    <div class="filter-container">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="供货商名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入供货商名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input
            v-model="filterForm.phone"
            placeholder="请输入联系电话"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="信用等级">
          <el-select
            v-model="filterForm.creditRating"
            placeholder="请选择信用等级"
            clearable
            @clear="handleSearch"
            style="width: 120px"
          >
            <el-option label="A级" :value="5" />
            <el-option label="B级" :value="4" />
            <el-option label="C级" :value="3" />
            <el-option label="D级" :value="2" />
            <el-option label="E级" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            @clear="handleSearch"
            style="width: 100px"
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      :data="supplierList"
      v-loading="loading"
      :border="true"
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa', textAlign: 'center' }"
    >
      <el-table-column prop="id" label="ID" width="80" :align="'center'" />
      <el-table-column prop="code" label="供货商编码" width="120" />
      <el-table-column prop="name" label="供货商名称" min-width="150" />
      <el-table-column prop="contactPerson" label="联系人" width="100" />
      <el-table-column prop="phone" label="联系电话" width="120" />
      <el-table-column prop="email" label="邮箱" min-width="150" />
      <el-table-column prop="address" label="地址" min-width="200" />
      <el-table-column prop="creditRating" label="信用等级" width="100" :align="'center'">
        <template #default="{ row }">
          <el-tag :type="getCreditRatingTagType(row.creditRating)">
            {{ getCreditRatingText(row.creditRating) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="productCount" label="供应商品数" width="100" :align="'center'" />
      <el-table-column prop="status" label="状态" width="80" :align="'center'">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastSupplyTime" label="最后供货时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right" :align="'center'">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleEdit(row)" :icon="Edit"
            >编辑</el-button
          >
          <el-button
            v-if="row.status === 1"
            type="danger"
            link
            size="small"
            @click="handleDisable(row)"
            :icon="Remove"
            >停用</el-button
          >
          <el-button
            v-if="row.status === 0"
            type="success"
            link
            size="small"
            @click="handleEnable(row)"
            :icon="Check"
            >启用</el-button
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

    <!-- 供货商对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="true"
    >
      <el-form
        ref="supplierFormRef"
        :model="supplierForm"
        :rules="supplierRules"
        label-width="100px"
      >
        <el-form-item label="供货商编码" prop="code">
          <el-input
            v-model="supplierForm.code"
            placeholder="请输入供货商编码"
            :disabled="!!supplierForm.id"
          />
        </el-form-item>
        <el-form-item label="供货商名称" prop="name">
          <el-input v-model="supplierForm.name" placeholder="请输入供货商名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contactPerson">
          <el-input v-model="supplierForm.contactPerson" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="supplierForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="supplierForm.email" placeholder="请输入邮箱" type="email" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input
            v-model="supplierForm.address"
            placeholder="请输入详细地址"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="信用等级" prop="creditRating">
          <el-select
            v-model="supplierForm.creditRating"
            placeholder="请选择信用等级"
            style="width: 100%"
          >
            <el-option label="A级" :value="5" />
            <el-option label="B级" :value="4" />
            <el-option label="C级" :value="3" />
            <el-option label="D级" :value="2" />
            <el-option label="E级" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="开户银行" prop="bankName">
          <el-input v-model="supplierForm.bankName" placeholder="请输入开户银行名称" />
        </el-form-item>
        <el-form-item label="银行账号" prop="bankAccount">
          <el-input v-model="supplierForm.bankAccount" placeholder="请输入银行账号" />
        </el-form-item>
        <el-form-item label="税号" prop="taxNumber">
          <el-input v-model="supplierForm.taxNumber" placeholder="请输入纳税人识别号" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="supplierForm.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input
            v-model="supplierForm.description"
            type="textarea"
            placeholder="请输入备注"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting"> 确认 </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
  
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Search, Refresh, Edit, Remove, Check } from '@element-plus/icons-vue'
import productApi from '@/api/product'
import { getResults, mapSupplierToView } from '@/utils/adapters'

const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const supplierFormRef = ref()
const supplierList = ref([])

// 过滤表单
const filterForm = reactive({
  name: '',
  phone: '',
  creditRating: '',
  status: '',
})

// 分页配置
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
})

// 供货商表单
const supplierForm = reactive({
  id: '',
  code: '',
  name: '',
  contactPerson: '',
  phone: '',
  email: '',
  address: '',
  creditRating: 3,
  bankName: '',
  bankAccount: '',
  taxNumber: '',
  status: 1,
  description: '',
})

// 表单验证规则
const supplierRules = {
  code: [
    { required: true, message: '请输入供货商编码', trigger: 'blur' },
    { min: 3, message: '供货商编码长度至少3个字符', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '请输入供货商名称', trigger: 'blur' },
    { min: 2, message: '供货商名称长度至少2个字符', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  creditRating: [{ required: true, message: '请选择信用等级', trigger: 'change' }],
}

const dialogTitle = ref('新增供货商')

// 工具函数
const getCreditRatingText = (rating) => {
  const ratingMap = {
    5: 'A级',
    4: 'B级',
    3: 'C级',
    2: 'D级',
    1: 'E级',
  }
  return ratingMap[rating] || '未知'
}

const getCreditRatingTagType = (rating) => {
  if (rating >= 4) return 'success'
  if (rating >= 3) return 'primary'
  if (rating >= 2) return 'warning'
  return 'danger'
}

const handleSearch = () => {
  pagination.page = 1
  fetchSupplierList()
}

const handleReset = () => {
  filterForm.name = ''
  filterForm.phone = ''
  filterForm.creditRating = ''
  filterForm.status = ''
  pagination.page = 1
  fetchSupplierList()
}

const handleAddSupplier = () => {
  dialogTitle.value = '新增供货商'
  Object.assign(supplierForm, {
    id: '',
    code: '',
    name: '',
    contactPerson: '',
    phone: '',
    email: '',
    address: '',
    creditRating: 3,
    bankName: '',
    bankAccount: '',
    taxNumber: '',
    status: 1,
    description: '',
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑供货商'
  Object.assign(supplierForm, row)
  dialogVisible.value = true
}

const handleDisable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要停用该供货商吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await productApi.updateSupplier(row.id, {
      code: row.code,
      name: row.name,
      contact_person: row.contactPerson,
      phone: row.phone,
      address: row.address,
      email: row.email,
      credit_rating: row.creditRating,
      bank_name: row.bankName,
      bank_account: row.bankAccount,
      tax_number: row.taxNumber,
      status: 0,
      remark: row.description,
    })
    ElMessage.success('供货商已停用')
    fetchSupplierList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停用供货商失败')
    }
  }
}

const handleEnable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要启用该供货商吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await productApi.updateSupplier(row.id, {
      code: row.code,
      name: row.name,
      contact_person: row.contactPerson,
      phone: row.phone,
      address: row.address,
      email: row.email,
      credit_rating: row.creditRating,
      bank_name: row.bankName,
      bank_account: row.bankAccount,
      tax_number: row.taxNumber,
      status: 1,
      remark: row.description,
    })
    ElMessage.success('供货商已启用')
    fetchSupplierList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启用供货商失败')
    }
  }
}

const handleExport = () => {
  ElMessage.success('导出功能开发中')
}

const handleSizeChange = (size) => {
  pagination.size = size
  fetchSupplierList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchSupplierList()
}

const handleSubmit = async () => {
  if (!supplierFormRef.value) return

  try {
    await supplierFormRef.value.validate()
    submitting.value = true
    const payload = {
      code: supplierForm.code,
      name: supplierForm.name,
      contact_person: supplierForm.contactPerson,
      phone: supplierForm.phone,
      address: supplierForm.address,
      email: supplierForm.email,
      credit_rating: supplierForm.creditRating,
      bank_name: supplierForm.bankName,
      bank_account: supplierForm.bankAccount,
      tax_number: supplierForm.taxNumber,
      status: supplierForm.status,
      remark: supplierForm.description,
    }

    if (supplierForm.id) {
      await productApi.updateSupplier(supplierForm.id, payload)
      ElMessage.success('供货商更新成功')
    } else {
      await productApi.createSupplier(payload)
      ElMessage.success('供货商添加成功')
    }

    dialogVisible.value = false
    fetchSupplierList()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '保存供货商失败')
  } finally {
    submitting.value = false
  }
}

const fetchSupplierList = async () => {
  loading.value = true

  try {
    const response = await productApi.getSuppliers({
      page: pagination.page,
      page_size: pagination.size,
      search: filterForm.phone || filterForm.name || undefined,
      status: filterForm.status !== '' ? filterForm.status : undefined,
      min_rating: filterForm.creditRating || undefined,
    })
    const { list, total } = getResults(response)
    supplierList.value = list.map(mapSupplierToView)
    pagination.total = total
  } catch (error) {
    ElMessage.error('获取供货商列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSupplierList()
})
</script>
  
  <style lang="scss" scoped>
.supplier-list-container {
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