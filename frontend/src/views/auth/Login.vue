<template>
  <div class="login-container">
    <!-- 左侧：品牌 + 功能特色 -->
    <div class="login-left">
      <div class="brand-header">
        <div class="brand-logo">
          <el-icon :size="48"><Box /></el-icon>
        </div>
        <h1>超市库存管理系统</h1>
        <p class="slogan">Smart Inventory · Enterprise-Grade Management</p>
      </div>
      <div class="system-features">
        <h3>核心能力</h3>
        <div class="features-grid">
          <div class="feature-item">
            <div class="feature-icon">
              <el-icon :size="24"><Goods /></el-icon>
            </div>
            <div class="feature-text">
              <h4>商品管理</h4>
              <p>建档、分类、入库出库全流程</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <el-icon :size="24"><Box /></el-icon>
            </div>
            <div class="feature-text">
              <h4>库存管理</h4>
              <p>实时监控、预警、多仓支持</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <el-icon :size="24"><Van /></el-icon>
            </div>
            <div class="feature-text">
              <h4>供货商管理</h4>
              <p>资质维护、供货记录追溯</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <el-icon :size="24"><TrendCharts /></el-icon>
            </div>
            <div class="feature-text">
              <h4>销售分析</h4>
              <p>收益统计、趋势与毛利分析</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：登录卡片 -->
    <div class="login-right">
      <div class="login-card">
        <div class="login-title">
          <h2>账户登录</h2>
          <p>请输入您的账号密码以登录系统</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          :validate-on-rule-change="false"
          label-width="0"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="loginForm.remember">记住密码</el-checkbox>
            <el-link type="primary" :underline="false" @click="handleForgetPassword">
              忘记密码？
            </el-link>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
              size="large"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <p>
            还没有账号？<el-link type="primary" :underline="false" @click="handleRegister"
              >立即注册</el-link
            >
          </p>
        </div>
      </div>

      <div class="copyright-footer">
        <p>© 2025 超市库存管理系统 · 企业级库存与进销存解决方案</p>
      </div>
    </div>

    <el-dialog
      v-model="registerDialogVisible"
      title="注册申请"
      width="460px"
      :close-on-click-modal="true"
      class="sims-dialog-light"
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="90px"
        class="register-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="registerForm.username" placeholder="请输入用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="registerForm.gender" placeholder="请选择性别" style="width: 100%">
                <el-option label="男" :value="0" />
                <el-option label="女" :value="1" />
                <el-option label="未知" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="登录密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            show-password
            placeholder="请输入密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入密码"
          />
        </el-form-item>
        <el-form-item label="申请说明">
          <el-input
            v-model="registerForm.remark"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="可填写申请说明，便于管理员审核"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="registerDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="registering" @click="submitRegister">
            提交申请
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 登录提示对话框 -->
    <el-dialog
      v-model="showNotice"
      title="登录提示"
      width="500px"
      :close-on-click-modal="true"
      class="sims-dialog-light"
    >
      <div class="notice-content">
        <p>欢迎使用超市库存管理系统！</p>
        <p>首次登录请使用以下测试账户：</p>
        <p><strong>用户名：</strong>admin</p>
        <p><strong>密码：</strong>123456</p>
        <p class="notice-tip">登录成功后您可以体验完整的库存管理功能。</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showNotice = false" type="primary">知道了</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
  
  <script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock, Goods, Box, Van, TrendCharts } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import authApi from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

// 状态管理
const loading = ref(false)
const showNotice = ref(true)
const loginFormRef = ref()
const registerDialogVisible = ref(false)
const registering = ref(false)
const registerFormRef = ref()

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: '',
  remember: false,
})

const registerForm = reactive({
  username: '',
  email: '',
  phone: '',
  gender: 2,
  password: '',
  confirmPassword: '',
  remark: '',
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度至少3个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' },
  ],
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度至少3个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
}

// 登录处理函数
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    await authStore.login({
      username: loginForm.username,
      password: loginForm.password,
    })

    if (loginForm.remember) {
      localStorage.setItem('rememberedUser', loginForm.username)
    } else {
      localStorage.removeItem('rememberedUser')
    }

    ElMessage.success('登录成功！')
    router.push('/dashboard')
  } catch (error) {
    const errorMessage =
      error?.response?.data?.error?.non_field_errors?.[0] ||
      error?.response?.data?.error?.detail ||
      error?.response?.data?.detail ||
      '用户名或密码错误'
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 忘记密码处理
const handleForgetPassword = () => {
  ElMessageBox.alert('忘记密码功能正在开发中，请联系系统管理员重置密码。', '功能提示', {
    confirmButtonText: '确定',
    type: 'info',
  })
}

// 注册处理
const handleRegister = () => {
  Object.assign(registerForm, {
    username: '',
    email: '',
    phone: '',
    gender: 2,
    password: '',
    confirmPassword: '',
    remark: '',
  })
  registerDialogVisible.value = true
}

const submitRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
    registering.value = true
    await authApi.register({
      username: registerForm.username,
      email: registerForm.email,
      phone: registerForm.phone,
      gender: registerForm.gender,
      password: registerForm.password,
      confirm_password: registerForm.confirmPassword,
      remark: registerForm.remark,
    })
    ElMessage.success('注册申请已提交，请等待管理员审核')
    registerDialogVisible.value = false
  } catch (error) {
    const errorData = error?.response?.data?.error || error?.response?.data || {}
    const firstError = Object.values(errorData)[0]
    ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError || '提交注册申请失败')
  } finally {
    registering.value = false
  }
}

// 页面加载时检查是否有记住的账户
onMounted(() => {
  const rememberedUser = localStorage.getItem('rememberedUser')
  if (rememberedUser) {
    loginForm.username = rememberedUser
    loginForm.remember = true
  }

  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  }
})
</script>
  
<style lang="scss" scoped>
/* 企业级登录页：沉稳背景与清晰层次 */
.login-container {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(160deg, #eef2f7 0%, #e4e9f2 40%, #d1d9e6 100%);
  overflow: auto;
}

.login-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 64px;
  min-width: 0;
}

.brand-header {
  margin-bottom: 48px;
  animation: fadeInDown 0.5s ease-out;
}

.brand-logo {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $primary-color;
  color: #fff;
  border-radius: 16px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba($primary-color, 0.35);
}

.brand-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: $text-color-primary;
  letter-spacing: -0.02em;
}

.slogan {
  font-size: 14px;
  color: $text-color-secondary;
  font-weight: 400;
  margin: 0;
}

.system-features {
  animation: fadeInUp 0.5s ease-out 0.1s both;
}

.system-features h3 {
  font-size: 15px;
  font-weight: 600;
  color: $text-color-secondary;
  margin-bottom: 20px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.features-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-medium;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  padding: $spacing-medium;
  background: #fff;
  border-radius: 10px;
  border: 1px solid $border-color-lighter;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.feature-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border-color: $border-color-base;
}

.feature-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba($primary-color, 0.08);
  color: $primary-color;
  border-radius: 10px;
  margin-right: $spacing-medium;
  flex-shrink: 0;
}

.feature-text h4 {
  font-size: 15px;
  font-weight: 600;
  color: $text-color-primary;
  margin: 0 0 4px 0;
}

.feature-text p {
  font-size: 13px;
  color: $text-color-secondary;
  margin: 0;
  line-height: 1.45;
}

/* 右侧登录区：白底卡片，专业简约 */
.login-right {
  width: 460px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: $spacing-extra-large;
  background: #fff;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.04);
}

.login-card {
  width: 100%;
  max-width: 360px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid $border-color-lighter;
  padding: 40px 32px;
  animation: fadeInUp 0.4s ease-out 0.05s both;
}

.login-title {
  text-align: center;
  margin-bottom: 32px;
}

.login-title h2 {
  font-size: 20px;
  font-weight: 600;
  color: $text-color-primary;
  margin: 0 0 8px 0;
}

.login-title p {
  font-size: 14px;
  color: $text-color-secondary;
  margin: 0;
}

.login-form .el-form-item {
  margin-bottom: $spacing-medium;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-large;
}

.form-options .el-checkbox {
  color: $text-color-regular;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
}

.login-footer {
  margin-top: $spacing-large;
  text-align: center;
  border-top: 1px solid $border-color-lighter;
  padding-top: $spacing-medium;
}

.login-footer p {
  margin: 0;
  font-size: 13px;
  color: $text-color-regular;
}

.copyright-footer {
  margin-top: $spacing-large;
  text-align: center;
  color: $text-color-placeholder;
  font-size: 12px;
}

.copyright-footer p {
  margin: 0;
}

.notice-content {
  padding: $spacing-medium 0;
  line-height: 1.6;
}

.notice-content p {
  margin-bottom: $spacing-small;
  color: $text-color-regular;
}

.notice-content strong {
  color: $text-color-primary;
  font-weight: 600;
}

.notice-tip {
  margin-top: $spacing-medium;
  padding: $spacing-small $spacing-medium;
  background: #f0f7ff;
  border-left: 4px solid $primary-color;
  border-radius: 0 4px 4px 0;
  color: $text-color-regular;
  font-size: 13px;
}

/* 登录页始终使用浅色输入框，避免暗色模式下文字过淡难以辨认 */
.login-container :deep(.el-input__wrapper) {
  background-color: #f5f7fa !important;
  box-shadow: 0 0 0 1px #dcdfe6 inset !important;
}

.login-container :deep(.el-input__wrapper .el-input__inner) {
  color: #303133 !important;
}

.login-container :deep(.el-input__wrapper .el-input__inner::placeholder) {
  color: #909399 !important;
}

.login-container :deep(.el-select .el-select__wrapper) {
  background-color: #f5f7fa !important;
  box-shadow: 0 0 0 1px #dcdfe6 inset !important;
}

.login-container :deep(.el-select .el-select__wrapper .el-input__inner),
.login-container :deep(.el-select .el-select__wrapper .el-input__inner::placeholder) {
  color: #303133 !important;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .login-container {
    flex-direction: column;
  }

  .login-left {
    padding: 32px 24px 24px;
  }

  .brand-header {
    margin-bottom: 32px;
    text-align: center;
  }

  .brand-logo {
    margin-left: auto;
    margin-right: auto;
  }

  .brand-header h1 {
    font-size: 24px;
  }

  .slogan {
    font-size: 13px;
  }

  .system-features h3 {
    text-align: center;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .login-right {
    width: 100%;
    padding: 24px 16px 32px;
    background: transparent;
    box-shadow: none;
  }

  .login-card {
    max-width: 100%;
    padding: 32px 24px;
  }

  .login-title h2 {
    font-size: 18px;
  }
}
</style>