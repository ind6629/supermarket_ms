<template>
  <div class="personal-center-container">
    <div class="table-header">
      <h2>个人中心</h2>
    </div>

    <div class="profile-card">
      <div class="avatar-section">
        <div class="avatar-wrap">
          <el-avatar :size="100" :src="avatarUrl">
            <el-icon :size="50"><User /></el-icon>
          </el-avatar>
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :http-request="customAvatarUpload"
          >
            <el-button type="primary" link size="small" class="change-avatar-btn">更换头像</el-button>
          </el-upload>
        </div>
      </div>

      <el-form
        ref="profileFormRef"
        :model="profileForm"
        :rules="profileRules"
        label-width="90px"
        class="profile-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="profileForm.username" placeholder="用户名" disabled />
        </el-form-item>
        <el-form-item label="工号" prop="employeeId">
          <el-input v-model="profileForm.employeeId" placeholder="工号" disabled />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="profileForm.gender" placeholder="请选择性别" style="width: 100%">
            <el-option label="男" :value="0" />
            <el-option label="女" :value="1" />
            <el-option label="未知" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-input :model-value="roleDisplay" disabled />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSaveProfile" :loading="saving">保存修改</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="password-card">
      <h3>修改密码</h3>
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
        class="password-form"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            placeholder="请输入原密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/index'
import authApi from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { getAvatarUrl } from '@/utils/avatar'

const authStore = useAuthStore()
const profileFormRef = ref()
const passwordFormRef = ref()
const saving = ref(false)
const changingPassword = ref(false)

const profileForm = reactive({
  username: '',
  employeeId: '',
  email: '',
  phone: '',
  gender: 2,
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const profileRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
}

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

const avatarUrl = computed(() => {
  const u = authStore.user
  return u?.avatar ? getAvatarUrl(u.avatar) : ''
})

const roleDisplay = computed(() => {
  const u = authStore.user
  return u?.role_display || '-'
})

const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

const customAvatarUpload = async ({ file }) => {
  const formData = new FormData()
  formData.append('avatar', file)
  try {
    await request.put('/auth/profile/', formData)
    await handleAvatarSuccess()
  } catch {
    handleAvatarError()
  }
}

const handleAvatarSuccess = async () => {
  ElMessage.success('头像更新成功')
  await authStore.getUserInfo()
}

const handleAvatarError = () => {
  ElMessage.error('头像上传失败')
}

const fetchProfile = async () => {
  try {
    const data = await authStore.getUserInfo()
    Object.assign(profileForm, {
      username: data?.username || '',
      employeeId: data?.employee_id || '',
      email: data?.email || '',
      phone: data?.phone || '',
      gender: data?.gender ?? 2,
    })
  } catch {
    ElMessage.error('获取个人资料失败')
  }
}

const handleSaveProfile = async () => {
  if (!profileFormRef.value) return
  try {
    await profileFormRef.value.validate()
    saving.value = true
    await authApi.updateProfile({
      email: profileForm.email,
      phone: profileForm.phone,
      gender: profileForm.gender,
    })
    await authStore.getUserInfo()
    ElMessage.success('资料已保存')
  } catch (error) {
    const err = error?.response?.data?.error || error?.response?.data
    const msg = err && typeof err === 'object' ? Object.values(err).flat()[0] : err || '保存失败'
    if (error !== 'cancel') ElMessage.error(msg)
  } finally {
    saving.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    await authApi.changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
      confirm_password: passwordForm.confirmPassword,
    })
    ElMessage.success('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    const err = error?.response?.data?.error || error?.response?.data
    const msg = err && typeof err === 'object' ? Object.values(err).flat()[0] : err || '修改失败'
    if (error !== 'cancel') ElMessage.error(msg)
  } finally {
    changingPassword.value = false
  }
}

onMounted(fetchProfile)
</script>

<style lang="scss" scoped>
.personal-center-container {
  padding: $spacing-large;
  background-color: var(--sims-card-bg);
  border-radius: 8px;
  box-shadow: var(--sims-card-shadow);

  .table-header {
    margin-bottom: $spacing-large;

    h2 {
      margin: 0;
      font-size: $font-size-large + 2px;
      font-weight: 600;
      color: var(--sims-text-primary);
    }
  }

  .profile-card {
    display: flex;
    gap: $spacing-extra-large;
    margin-bottom: $spacing-extra-large;
    padding-bottom: $spacing-extra-large;
    border-bottom: 1px solid var(--sims-card-border);
  }

  .avatar-section {
    flex-shrink: 0;
  }

  .avatar-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $spacing-small;

    .change-avatar-btn {
      margin-top: $spacing-small;
    }
  }

  .profile-form {
    flex: 1;
    max-width: 400px;
  }

  .password-card {
    h3 {
      margin: 0 0 $spacing-medium 0;
      font-size: $font-size-medium;
      font-weight: 600;
      color: var(--sims-text-primary);
    }
  }

  .password-form {
    max-width: 400px;
  }
}
</style>
