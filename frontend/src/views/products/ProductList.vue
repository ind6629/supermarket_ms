<template>
  <div class="product-list-container">
    <div class="table-header">
      <h2>商品管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddProduct" :icon="Plus">新增商品</el-button>
        <el-button @click="handleExport" :icon="Download">导出</el-button>
      </div>
    </div>

    <div class="filter-container">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="商品名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入商品名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="商品编码">
          <el-input
            v-model="filterForm.code"
            placeholder="请输入商品编码"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="filterForm.category"
            placeholder="请选择分类"
            clearable
            @clear="handleSearch"
            style="width: 150px"
          >
            <el-option
              v-for="category in categoryOptions"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            @clear="handleSearch"
            style="width: 120px"
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
      :data="productList"
      v-loading="loading"
      :border="true"
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa', textAlign: 'center' }"
    >
      <el-table-column prop="id" label="ID" width="80" :align="'center'" />
      <el-table-column prop="code" label="商品编码" width="120" />
      <el-table-column prop="name" label="商品名称" min-width="150" />
      <el-table-column prop="category" label="分类" width="100">
        <template #default="{ row }">
          <el-tag :type="getCategoryTagType(row.categoryName)">{{
            getCategoryText(row.categoryName)
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="brand" label="品牌" width="120" />
      <el-table-column prop="unit" label="单位" width="80" :align="'center'" />
      <el-table-column prop="purchasePrice" label="采购价(元)" width="100" :align="'center'">
        <template #default="{ row }">¥{{ row.purchasePrice }}</template>
      </el-table-column>
      <el-table-column prop="salePrice" label="销售价(元)" width="100" :align="'center'">
        <template #default="{ row }">¥{{ row.salePrice }}</template>
      </el-table-column>
      <el-table-column prop="currentStock" label="库存" width="100" :align="'center'" />
      <el-table-column prop="status" label="状态" width="80" :align="'center'">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '正常' : '停用' }}
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

    <!-- 商品对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="680px"
      :close-on-click-modal="true"
    >
      <el-form ref="productFormRef" :model="productForm" :rules="productRules" label-width="100px">
        <el-form-item label="商品编码" prop="code">
          <el-input
            v-model="productForm.code"
            placeholder="请输入商品编码"
            :disabled="!!productForm.id"
          />
        </el-form-item>
        <el-form-item label="条形码" prop="barcode">
          <el-input v-model="productForm.barcode" placeholder="请输入条形码" />
        </el-form-item>
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="productForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="category in categoryOptions"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌" prop="brand">
          <el-input v-model="productForm.brand" placeholder="请输入品牌" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-select v-model="productForm.unit" placeholder="请选择单位" style="width: 150px">
            <el-option
              v-for="item in unitOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="规格" prop="specification">
          <el-input v-model="productForm.specification" placeholder="请输入规格，如500g/袋" />
        </el-form-item>
        <el-form-item label="采购价" prop="purchasePrice">
          <el-input
            v-model="productForm.purchasePrice"
            placeholder="请输入采购价"
            type="number"
            min="0"
            step="0.01"
            style="width: 200px"
          >
            <template #prepend>¥</template>
          </el-input>
        </el-form-item>
        <el-form-item label="销售价" prop="salePrice">
          <el-input
            v-model="productForm.salePrice"
            placeholder="请输入销售价"
            type="number"
            min="0"
            step="0.01"
            style="width: 200px"
          >
            <template #prepend>¥</template>
          </el-input>
        </el-form-item>
        <el-form-item label="最小库存" prop="minStock">
          <el-input
            v-model="productForm.minStock"
            placeholder="请输入最小库存"
            type="number"
            min="0"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="最大库存" prop="maxStock">
          <el-input
            v-model="productForm.maxStock"
            placeholder="请输入最大库存"
            type="number"
            min="0"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="productForm.status"
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
  </div>
</template>
  
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Search, Refresh, Edit, Remove, Check } from '@element-plus/icons-vue'
import productApi from '@/api/product'
import { getResults, mapProductToView } from '@/utils/adapters'

const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const productFormRef = ref()
const productList = ref([])
const categoryOptions = ref([])
const unitOptions = [
  { label: '件', value: 'piece' },
  { label: '箱', value: 'box' },
  { label: '袋', value: 'bag' },
  { label: '瓶', value: 'bottle' },
  { label: '千克', value: 'kg' },
  { label: '克', value: 'g' },
  { label: '升', value: 'L' },
  { label: '毫升', value: 'ml' },
]

// 过滤表单
const filterForm = reactive({
  name: '',
  code: '',
  category: '',
  status: '',
})

// 分页配置
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
})

// 商品表单
const productForm = reactive({
  id: '',
  code: '',
  barcode: '',
  name: '',
  category: '',
  brand: '',
  unit: 'piece',
  specification: '',
  purchasePrice: 0,
  salePrice: 0,
  minStock: 0,
  maxStock: 0,
  status: 1,
})

// 表单验证规则
const productRules = {
  code: [
    { required: true, message: '请输入商品编码', trigger: 'blur' },
    { min: 3, message: '商品编码长度至少3个字符', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { min: 2, message: '商品名称长度至少2个字符', trigger: 'blur' },
  ],
  barcode: [{ required: true, message: '请输入条形码', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  purchasePrice: [{ required: true, message: '请输入采购价', trigger: 'blur' }],
  salePrice: [{ required: true, message: '请输入销售价', trigger: 'blur' }],
}

// 计算属性
const dialogTitle = ref('新增商品')

// 工具函数
const getCategoryText = (category) => {
  return category || '未分类'
}

const getCategoryTagType = (category) => {
  if (!category) return 'info'
  return ['success', 'primary', 'warning', 'danger'][category.length % 4]
}

// 事件处理函数
const handleSearch = () => {
  pagination.page = 1
  fetchProductList()
}

const handleReset = () => {
  filterForm.name = ''
  filterForm.code = ''
  filterForm.category = ''
  filterForm.status = ''
  pagination.page = 1
  fetchProductList()
}

const handleAddProduct = () => {
  dialogTitle.value = '新增商品'
  Object.assign(productForm, {
    id: '',
    code: '',
    barcode: '',
    name: '',
    category: categoryOptions.value[0]?.id || '',
    brand: '',
    unit: 'piece',
    specification: '',
    purchasePrice: 0,
    salePrice: 0,
    minStock: 0,
    maxStock: 0,
    status: 1,
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑商品'
  Object.assign(productForm, {
    id: row.id,
    code: row.code,
    barcode: row.barcode,
    name: row.name,
    category: row.category,
    brand: row.brand,
    unit: row.unit,
    specification: row.specification || '',
    purchasePrice: row.purchasePrice,
    salePrice: row.salePrice,
    minStock: row.minStock,
    maxStock: row.maxStock || 0,
    status: row.status,
  })
  dialogVisible.value = true
}

const handleDisable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要停用该商品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await productApi.updateProduct(row.id, {
      code: row.code,
      name: row.name,
      barcode: row.barcode,
      category: row.category,
      unit: row.unit,
      specification: row.specification || '',
      purchase_price: row.purchasePrice,
      sale_price: row.salePrice,
      min_stock: row.minStock,
      max_stock: row.maxStock,
      brand: row.brand || '',
      supplier: row.supplier || null,
      status: 0,
    })
    ElMessage.success('商品已停用')
    fetchProductList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停用商品失败')
    }
  }
}

const handleEnable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要启用该商品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await productApi.updateProduct(row.id, {
      code: row.code,
      name: row.name,
      barcode: row.barcode,
      category: row.category,
      unit: row.unit,
      specification: row.specification || '',
      purchase_price: row.purchasePrice,
      sale_price: row.salePrice,
      min_stock: row.minStock,
      max_stock: row.maxStock,
      brand: row.brand || '',
      supplier: row.supplier || null,
      status: 1,
    })
    ElMessage.success('商品已启用')
    fetchProductList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启用商品失败')
    }
  }
}

const handleExport = () => {
  ElMessage.success('导出功能开发中')
}

const handleSizeChange = (size) => {
  pagination.size = size
  fetchProductList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchProductList()
}

const handleSubmit = async () => {
  if (!productFormRef.value) return

  try {
    await productFormRef.value.validate()
    submitting.value = true
    const payload = {
      code: productForm.code,
      barcode: productForm.barcode,
      name: productForm.name,
      category: productForm.category,
      unit: productForm.unit,
      specification: productForm.specification,
      purchase_price: Number(productForm.purchasePrice),
      sale_price: Number(productForm.salePrice),
      min_stock: Number(productForm.minStock),
      max_stock: productForm.maxStock === '' ? null : Number(productForm.maxStock),
      brand: productForm.brand,
      status: productForm.status,
    }

    if (productForm.id) {
      await productApi.updateProduct(productForm.id, payload)
      ElMessage.success('商品更新成功')
    } else {
      await productApi.createProduct(payload)
      ElMessage.success('商品添加成功')
    }

    dialogVisible.value = false
    fetchProductList()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '保存商品失败')
  } finally {
    submitting.value = false
  }
}

const fetchProductList = async () => {
  loading.value = true

  try {
    const searchKeyword = filterForm.code || filterForm.name || undefined
    const response = await productApi.getProducts({
      page: pagination.page,
      page_size: pagination.size,
      search: searchKeyword,
      category: filterForm.category || undefined,
      status: filterForm.status !== '' ? filterForm.status : undefined,
    })
    const { list, total } = getResults(response)
    productList.value = list.map(mapProductToView)
    pagination.total = total
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCategoryOptions = async () => {
  try {
    const response = await productApi.getCategories({ page_size: 100 })
    const { list } = getResults(response)
    categoryOptions.value = list
    if (!productForm.category && list.length) {
      productForm.category = list[0].id
    }
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  }
}

onMounted(async () => {
  await fetchCategoryOptions()
  fetchProductList()
})
</script>
  
  <style lang="scss" scoped>
.product-list-container {
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