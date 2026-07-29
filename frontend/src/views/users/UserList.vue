<template>
  <div class="user-list-container">
    <div class="table-header">
      <h2>用户管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddUser" :icon="Plus">新增用户</el-button>
        <el-button @click="handleExport" :icon="Download">导出</el-button>
      </div>
    </div>

    <div class="filter-container">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="用户名">
          <el-input
            v-model="filterForm.username"
            placeholder="请输入用户名"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="filterForm.role"
            placeholder="请选择角色"
            clearable
            @clear="handleSearch"
          >
            <el-option
              v-for="role in roleOptions"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            @clear="handleSearch"
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select
            v-model="filterForm.approvalStatus"
            placeholder="请选择审核状态"
            clearable
            @clear="handleSearch"
          >
            <el-option
              v-for="item in approvalStatusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      :data="userList"
      v-loading="loading"
      :border="true"
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa' }"
    >
      <el-table-column prop="id" label="ID" width="80" header-align="center" :align="'center'" />
      <el-table-column prop="username" label="用户名" min-width="120" header-align="center" />
      <el-table-column prop="email" label="邮箱" min-width="180" header-align="center" />
      <el-table-column prop="phone" label="手机号" width="120" header-align="center" />
      <el-table-column prop="role" label="角色" width="120" header-align="center">
        <template #default="{ row }">
          <el-tag :type="row.approvalStatus === 0 ? 'info' : getRoleTagType(row.role)">
            {{ row.approvalStatus === 0 ? '待分配' : getRoleText(row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80" header-align="center" :align="'center'">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="approvalStatus" label="审核状态" width="100" header-align="center" :align="'center'">
        <template #default="{ row }">
          <el-tag :type="getApprovalTagType(row.approvalStatus)">
            {{ row.approvalStatusDisplay || getApprovalText(row.approvalStatus) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" width="180" header-align="center" />
      <el-table-column label="操作" width="320" fixed="right" header-align="center" :align="'center'">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleEdit(row)" :icon="Edit"
            >编辑</el-button
          >
          <el-button
            v-if="row.approvalStatus === 0"
            type="success"
            link
            size="small"
            @click="handleOpenReview(row)"
          >
            审核
          </el-button>
          <el-button type="warning" link size="small" @click="handleOpenResetPassword(row)">重置密码</el-button>
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

    <!-- 用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="true"
    >
      <el-form ref="userFormRef" :model="userForm" :rules="userRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
            :disabled="!!userForm.id"
          />
        </el-form-item>
        <el-form-item label="工号" prop="employeeId">
          <el-input
            v-model="userForm.employeeId"
            placeholder="请输入工号"
            :disabled="!!userForm.id"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!userForm.id">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" type="email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option
              v-for="role in roleOptions"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="userForm.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="停用"
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

    <el-dialog v-model="resetPasswordVisible" title="重置密码" width="420px" :close-on-click-modal="true">
      <el-form
        ref="resetPasswordFormRef"
        :model="resetPasswordForm"
        :rules="resetPasswordRules"
        label-width="90px"
      >
        <el-form-item label="目标用户">
          <el-input :model-value="resetPasswordForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="resetPasswordForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="resetPasswordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resetPasswordVisible = false">取消</el-button>
          <el-button type="primary" @click="handleResetPasswordSubmit" :loading="resetPasswordSubmitting">
            确认重置
          </el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="reviewDialogVisible" title="审核注册申请" width="460px" :close-on-click-modal="true">
      <el-form ref="reviewFormRef" :model="reviewForm" :rules="reviewRules" label-width="90px">
        <el-form-item label="申请账号">
          <el-input :model-value="reviewForm.username" disabled />
        </el-form-item>
        <el-form-item label="处理结果" prop="action">
          <el-radio-group v-model="reviewForm.action">
            <el-radio label="approve">通过</el-radio>
            <el-radio label="reject">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="reviewForm.action === 'approve'" label="分配角色" prop="role">
          <el-select v-model="reviewForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option v-for="role in roleOptions" :key="role.value" :label="role.label" :value="role.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核备注" prop="reviewRemark">
          <el-input
            v-model="reviewForm.reviewRemark"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="请输入审核备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="reviewDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleReviewSubmit" :loading="reviewSubmitting">提交审核</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
  
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Search, Refresh, Edit, Remove, Check } from '@element-plus/icons-vue'
import userApi from '@/api/user'
import { getResults, mapUserToView, roleOptions } from '@/utils/adapters'

const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const resetPasswordVisible = ref(false)
const resetPasswordSubmitting = ref(false)
const reviewDialogVisible = ref(false)
const reviewSubmitting = ref(false)
const userFormRef = ref()
const resetPasswordFormRef = ref()
const reviewFormRef = ref()
const userList = ref([])

const approvalStatusOptions = [
  { label: '待审核', value: 0 },
  { label: '已通过', value: 1 },
  { label: '已驳回', value: 2 },
]

// 过滤表单
const filterForm = reactive({
  username: '',
  role: '',
  status: '',
  approvalStatus: '',
})

// 分页配置
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
})

// 用户表单
const userForm = reactive({
  id: '',
  username: '',
  employeeId: '',
  password: '',
  email: '',
  phone: '',
  role: 4,
  status: 1,
})

const resetPasswordForm = reactive({
  id: '',
  username: '',
  newPassword: '',
  confirmPassword: '',
})

const reviewForm = reactive({
  id: '',
  username: '',
  action: 'approve',
  role: 4,
  reviewRemark: '',
})

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度至少3个字符', trigger: 'blur' },
  ],
  employeeId: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const resetPasswordRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (value !== resetPasswordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
}

const reviewRules = {
  action: [{ required: true, message: '请选择处理结果', trigger: 'change' }],
  role: [
    {
      validator: (_, value, callback) => {
        if (reviewForm.action === 'approve' && (value === '' || value === null || value === undefined)) {
          callback(new Error('审核通过时必须分配角色'))
          return
        }
        callback()
      },
      trigger: 'change',
    },
  ],
}

// 计算属性
const dialogTitle = ref('新增用户')

const getRoleText = (role) => {
  return roleOptions.find((item) => item.value === role)?.label || '未知'
}

const getRoleTagType = (role) => {
  const typeMap = {
    0: 'danger',
    1: 'warning',
    2: 'success',
    3: 'warning',
    4: 'primary',
  }
  return typeMap[role] || 'info'
}

const getApprovalText = (approvalStatus) => {
  return approvalStatusOptions.find((item) => item.value === approvalStatus)?.label || '未知'
}

const getApprovalTagType = (approvalStatus) => {
  const typeMap = {
    0: 'warning',
    1: 'success',
    2: 'danger',
  }
  return typeMap[approvalStatus] || 'info'
}

const handleSearch = () => {
  pagination.page = 1
  fetchUserList()
}

const handleReset = () => {
  filterForm.username = ''
  filterForm.role = ''
  filterForm.status = ''
  filterForm.approvalStatus = ''
  pagination.page = 1
  fetchUserList()
}

const handleAddUser = () => {
  dialogTitle.value = '新增用户'
  Object.assign(userForm, {
    id: '',
    username: '',
    employeeId: '',
    password: '',
    email: '',
    phone: '',
    role: 4,
    status: 1,
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑用户'
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    employeeId: row.employeeId,
    password: '',
    email: row.email,
    phone: row.phone,
    role: row.role,
    status: row.status,
  })
  dialogVisible.value = true
}

const handleDisable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要停用该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await userApi.deactivateUser(row.id)
    ElMessage.success('用户已停用')
    fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.error || '停用用户失败')
    }
  }
}

const handleEnable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要启用该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await userApi.activateUser(row.id)
    ElMessage.success('用户已启用')
    fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.error || '启用用户失败')
    }
  }
}

const handleOpenResetPassword = (row) => {
  Object.assign(resetPasswordForm, {
    id: row.id,
    username: row.username,
    newPassword: '',
    confirmPassword: '',
  })
  resetPasswordVisible.value = true
}

const handleOpenReview = (row) => {
  Object.assign(reviewForm, {
    id: row.id,
    username: row.username,
    action: 'approve',
    role: row.role ?? 4,
    reviewRemark: row.reviewRemark || '',
  })
  reviewDialogVisible.value = true
}

const handleReviewSubmit = async () => {
  if (!reviewFormRef.value) return

  try {
    await reviewFormRef.value.validate()
    reviewSubmitting.value = true
    await userApi.reviewRegistration(reviewForm.id, {
      action: reviewForm.action,
      role: reviewForm.action === 'approve' ? reviewForm.role : undefined,
      review_remark: reviewForm.reviewRemark,
    })
    ElMessage.success(reviewForm.action === 'approve' ? '审核通过成功' : '驳回申请成功')
    reviewDialogVisible.value = false
    fetchUserList()
  } catch (error) {
    const errorData = error?.response?.data?.error || error?.response?.data || {}
    const firstError = Object.values(errorData)[0]
    ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError || '提交审核失败')
  } finally {
    reviewSubmitting.value = false
  }
}

const handleResetPasswordSubmit = async () => {
  if (!resetPasswordFormRef.value) return

  try {
    await resetPasswordFormRef.value.validate()
    resetPasswordSubmitting.value = true
    await userApi.resetPassword(resetPasswordForm.id, {
      new_password: resetPasswordForm.newPassword,
      confirm_password: resetPasswordForm.confirmPassword,
    })
    ElMessage.success('密码重置成功')
    resetPasswordVisible.value = false
  } catch (error) {
    const errorData = error?.response?.data || {}
    const firstError = Object.values(errorData)[0]
    ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError || '重置密码失败')
  } finally {
    resetPasswordSubmitting.value = false
  }
}

const handleExport = () => {
  ElMessage.success('导出功能开发中')
}

const handleSizeChange = (size) => {
  pagination.size = size
  fetchUserList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchUserList()
}

const handleSubmit = async () => {
  if (!userFormRef.value) return

  try {
    await userFormRef.value.validate()
    submitting.value = true
    if (userForm.id) {
      await userApi.updateUser(userForm.id, {
        username: userForm.username,
        email: userForm.email,
        phone: userForm.phone,
        role: userForm.role,
        status: userForm.status,
      })
      ElMessage.success('用户更新成功')
    } else {
      await userApi.createUser({
        username: userForm.username,
        employee_id: userForm.employeeId,
        password: userForm.password,
        confirm_password: userForm.password,
        email: userForm.email,
        phone: userForm.phone,
        role: userForm.role,
        status: userForm.status,
      })
      ElMessage.success('用户添加成功')
    }

    dialogVisible.value = false
    fetchUserList()
  } catch (error) {
    const errorData = error?.response?.data?.error || error?.response?.data || {}
    const firstError = Object.values(errorData)[0]
    ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError || '保存失败')
  } finally {
    submitting.value = false
  }
}

const fetchUserList = async () => {
  loading.value = true

  try {
    const response = await userApi.getUsers({
      page: pagination.page,
      page_size: pagination.size,
      search: filterForm.username || undefined,
      role: filterForm.role !== '' ? filterForm.role : undefined,
      status: filterForm.status !== '' ? filterForm.status : undefined,
      approval_status: filterForm.approvalStatus !== '' ? filterForm.approvalStatus : undefined,
    })
    const { list, total } = getResults(response)
    userList.value = list.map(mapUserToView)
    pagination.total = total
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUserList()
})
</script>
  
  <style lang="scss" scoped>
.user-list-container {
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