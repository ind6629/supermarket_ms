<template>
  <div class="category-list-container">
    <div class="table-header">
      <h2>商品分类管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddCategory" :icon="Plus">新增分类</el-button>
      </div>
    </div>

    <div class="search-container">
      <el-input
        v-model="searchKeyword"
        placeholder="请输入分类名称或编码"
        :prefix-icon="Search"
        clearable
        style="width: 300px; margin-bottom: 20px"
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      />
    </div>

    <el-table
      :data="categoryList"
      v-loading="loading"
      :border="true"
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa', textAlign: 'center' }"
      :row-key="(row) => row.id"
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      default-expand-all
    >
      <el-table-column prop="code" label="分类编码" width="120" />
      <el-table-column prop="name" label="分类名称" min-width="200">
        <template #default="{ row }">
          <span :style="{ paddingLeft: (row.level - 1) * 20 + 'px' }">
            <el-icon v-if="row.level > 1" style="margin-right: 5px">
              <ArrowRight />
            </el-icon>
            {{ row.name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="sortOrder" label="排序" width="80" :align="'center'" />
      <el-table-column prop="productCount" label="商品数量" width="100" :align="'center'" />
      <el-table-column prop="status" label="状态" width="80" :align="'center'">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" width="180" />
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

    <!-- 分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="true"
    >
      <el-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="categoryRules"
        label-width="100px"
      >
        <el-form-item label="上级分类" prop="parentId">
          <el-tree-select
            v-model="categoryForm.parentId"
            :data="categoryOptions"
            :props="categoryTreeProps"
            check-strictly
            placeholder="请选择上级分类（不选则为顶级分类）"
            style="width: 100%"
            clearable
          />
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input
            v-model="categoryForm.code"
            placeholder="请输入分类编码"
            :disabled="!!categoryForm.id"
          />
        </el-form-item>
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number
            v-model="categoryForm.sortOrder"
            :min="1"
            :max="999"
            controls-position="right"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="categoryForm.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input
            v-model="categoryForm.description"
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Edit, Remove, Check, ArrowRight } from '@element-plus/icons-vue'

// 状态变量
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const categoryFormRef = ref()

// 商品分类数据
const categoryList = ref([
  {
    id: 1,
    code: 'CAT001',
    name: '食品饮料',
    level: 1,
    parentId: null,
    sortOrder: 1,
    productCount: 256,
    status: 1,
    description: '食品和饮料类商品',
    createTime: '2024-01-15 10:00:00',
    children: [
      {
        id: 2,
        code: 'CAT002',
        name: '方便食品',
        level: 2,
        parentId: 1,
        sortOrder: 1,
        productCount: 45,
        status: 1,
        description: '方便面、速食等',
        createTime: '2024-01-15 10:00:00',
        children: [],
      },
      {
        id: 3,
        code: 'CAT003',
        name: '饮料',
        level: 2,
        parentId: 1,
        sortOrder: 2,
        productCount: 89,
        status: 1,
        description: '各类饮品',
        createTime: '2024-01-15 10:00:00',
        children: [],
      },
    ],
  },
  {
    id: 4,
    code: 'CAT004',
    name: '粮油副食',
    level: 1,
    parentId: null,
    sortOrder: 2,
    productCount: 123,
    status: 1,
    description: '粮油、调味品等',
    createTime: '2024-01-15 10:00:00',
    children: [
      {
        id: 5,
        code: 'CAT005',
        name: '食用油',
        level: 2,
        parentId: 4,
        sortOrder: 1,
        productCount: 23,
        status: 1,
        description: '各类食用油',
        createTime: '2024-01-15 10:00:00',
        children: [],
      },
      {
        id: 6,
        code: 'CAT006',
        name: '调味品',
        level: 2,
        parentId: 4,
        sortOrder: 2,
        productCount: 45,
        status: 1,
        description: '酱油、醋等调味品',
        createTime: '2024-01-15 10:00:00',
        children: [],
      },
    ],
  },
  {
    id: 7,
    code: 'CAT007',
    name: '日用品',
    level: 1,
    parentId: null,
    sortOrder: 3,
    productCount: 189,
    status: 1,
    description: '日常用品类',
    createTime: '2024-01-15 10:00:00',
    children: [
      {
        id: 8,
        code: 'CAT008',
        name: '清洁用品',
        level: 2,
        parentId: 7,
        sortOrder: 1,
        productCount: 67,
        status: 1,
        description: '洗洁精、洗衣液等',
        createTime: '2024-01-15 10:00:00',
        children: [],
      },
      {
        id: 9,
        code: 'CAT009',
        name: '纸制品',
        level: 2,
        parentId: 7,
        sortOrder: 2,
        productCount: 89,
        status: 1,
        description: '纸巾、卫生纸等',
        createTime: '2024-01-15 10:00:00',
        children: [],
      },
    ],
  },
])

// 分类表单
const categoryForm = reactive({
  id: '',
  code: '',
  name: '',
  parentId: null,
  sortOrder: 1,
  status: 1,
  description: '',
})

// 表单验证规则
const categoryRules = {
  code: [
    { required: true, message: '请输入分类编码', trigger: 'blur' },
    { min: 3, message: '分类编码长度至少3个字符', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, message: '分类名称长度至少2个字符', trigger: 'blur' },
  ],
  sortOrder: [
    { required: true, message: '请输入排序', trigger: 'blur' },
    { type: 'number', min: 1, message: '排序必须大于0', trigger: 'blur' },
  ],
}

// 分类选项（用于树形选择器）
const categoryOptions = computed(() => {
  const flattenCategories = (categories, result = []) => {
    categories.forEach((category) => {
      result.push({
        id: category.id,
        label: category.name,
        children: category.children || [],
      })
      if (category.children && category.children.length > 0) {
        flattenCategories(category.children, result)
      }
    })
    return result
  }
  return flattenCategories(categoryList.value)
})

// 树形选择器配置
const categoryTreeProps = {
  value: 'id',
  label: 'label',
  children: 'children',
}

// 计算属性
const dialogTitle = ref('新增分类')

// 事件处理函数
const handleSearch = () => {
  ElMessage.info('搜索功能开发中')
}

const handleAddCategory = () => {
  dialogTitle.value = '新增分类'
  Object.assign(categoryForm, {
    id: '',
    code: '',
    name: '',
    parentId: null,
    sortOrder: categoryList.value.length + 1,
    status: 1,
    description: '',
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑分类'
  Object.assign(categoryForm, row)
  dialogVisible.value = true
}

const handleDisable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要停用该分类吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // 递归停用子分类
    const disableCategory = (category) => {
      category.status = 0
      if (category.children && category.children.length > 0) {
        category.children.forEach((child) => disableCategory(child))
      }
    }

    disableCategory(row)
    ElMessage.success('分类已停用')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停用分类失败:', error)
    }
  }
}

const handleEnable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要启用该分类吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    row.status = 1
    ElMessage.success('分类已启用')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('启用分类失败:', error)
    }
  }
}

const handleSubmit = async () => {
  if (!categoryFormRef.value) return

  try {
    await categoryFormRef.value.validate()

    submitting.value = true

    // 模拟API调用
    setTimeout(() => {
      if (categoryForm.id) {
        // 更新分类
        const updateCategory = (categories, id, newData) => {
          for (let i = 0; i < categories.length; i++) {
            if (categories[i].id === id) {
              Object.assign(categories[i], newData)
              return true
            }
            if (categories[i].children && categories[i].children.length > 0) {
              if (updateCategory(categories[i].children, id, newData)) {
                return true
              }
            }
          }
          return false
        }

        updateCategory(categoryList.value, categoryForm.id, categoryForm)
        ElMessage.success('分类更新成功')
      } else {
        // 新增分类
        const newCategory = {
          id: Date.now(),
          ...categoryForm,
          level: categoryForm.parentId ? 2 : 1,
          productCount: 0,
          children: [],
          createTime: new Date().toLocaleString(),
        }

        if (categoryForm.parentId) {
          const addToParent = (categories, parentId, newCategory) => {
            for (let i = 0; i < categories.length; i++) {
              if (categories[i].id === parentId) {
                categories[i].children.push(newCategory)
                return true
              }
              if (categories[i].children && categories[i].children.length > 0) {
                if (addToParent(categories[i].children, parentId, newCategory)) {
                  return true
                }
              }
            }
            return false
          }

          if (!addToParent(categoryList.value, categoryForm.parentId, newCategory)) {
            // 如果找不到父分类，添加到根级
            categoryList.value.push(newCategory)
          }
        } else {
          categoryList.value.push(newCategory)
        }

        ElMessage.success('分类添加成功')
      }

      dialogVisible.value = false
      submitting.value = false
    }, 1000)
  } catch (error) {
    submitting.value = false
  }
}

// 获取分类列表
const fetchCategoryList = async () => {
  loading.value = true

  try {
    // 模拟API调用
    setTimeout(() => {
      loading.value = false
    }, 500)
  } catch (error) {
    console.error('获取分类列表失败:', error)
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  fetchCategoryList()
})
</script>
  
  <style lang="scss" scoped>
.category-list-container {
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

  .search-container {
    margin-bottom: $spacing-large; /* 统一间距 */
    padding: $spacing-medium; /* 统一内边距 */
    background-color: var(--sims-page-bg); /* 使用全局页面背景色 */
    border-radius: 8px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03); /* 内部阴影 */

    .el-input {
      width: 300px; /* 保持宽度 */
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