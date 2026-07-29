export const getResults = (response) => {
  if (Array.isArray(response)) {
    return {
      list: response,
      total: response.length,
    }
  }

  return {
    list: response?.results || [],
    total: response?.count || 0,
  }
}

export const roleOptions = [
  { label: '超级管理员', value: 0 },
  { label: '管理员', value: 1 },
  { label: '库存管理员', value: 2 },
  { label: '财务', value: 3 },
  { label: '收银员', value: 4 },
]

export const mapUserToView = (user) => ({
  id: user.id,
  username: user.username,
  employeeId: user.employee_id,
  email: user.email || '',
  phone: user.phone || '',
  role: user.role,
  roleDisplay: user.role_display || '',
  status: user.status,
  approvalStatus: user.approval_status,
  approvalStatusDisplay: user.approval_status_display || '',
  reviewRemark: user.review_remark || '',
  reviewTime: user.review_time || '',
  department: user.department || '',
  position: user.position || '',
  createTime: user.create_time || user.date_joined || '',
})

export const mapProductToView = (product) => ({
  id: product.id,
  code: product.code,
  name: product.name,
  barcode: product.barcode,
  category: product.category,
  categoryName: product.category_name || '',
  brand: product.brand || '',
  unit: product.unit,
  unitDisplay: product.unit_display || product.unit,
  specification: product.specification || '',
  purchasePrice: Number(product.purchase_price || 0),
  salePrice: Number(product.sale_price || 0),
  currentStock: Number(product.total_stock || 0),
  minStock: Number(product.min_stock || 0),
  maxStock: product.max_stock == null ? null : Number(product.max_stock),
  supplier: product.supplier,
  supplierName: product.supplier_name || '',
  status: product.status,
  createTime: product.create_time || '',
})

export const mapInventoryToView = (inventory) => {
  const maxStock = inventory.product_max_stock ?? inventory.max_stock ?? 0
  const minStock = inventory.product_min_stock ?? inventory.min_stock ?? 0
  const availableStock = Number(inventory.available_stock || 0)

  let stockStatus = 'enough'
  if (availableStock < minStock) {
    stockStatus = 'low'
  } else if (maxStock && availableStock > maxStock) {
    stockStatus = 'over'
  }

  return {
    id: inventory.id,
    productId: inventory.product,
    productCode: inventory.product_code || '',
    productName: inventory.product_name || '',
    warehouseId: inventory.warehouse,
    warehouse: inventory.warehouse_name || '',
    currentStock: Number(inventory.current_stock || 0),
    availableStock,
    lockedStock: Number(inventory.locked_stock || 0),
    minStock,
    maxStock,
    stockStatus,
    lastUpdateTime: inventory.update_time || '',
  }
}

export const mapSupplierToView = (supplier) => ({
  id: supplier.id,
  code: supplier.code,
  name: supplier.name,
  contactPerson: supplier.contact_person || '',
  phone: supplier.phone || '',
  email: supplier.email || '',
  address: supplier.address || '',
  creditRating: Number(supplier.credit_rating || 0),
  bankName: supplier.bank_name || '',
  bankAccount: supplier.bank_account || '',
  taxNumber: supplier.tax_number || '',
  productCount: Number(supplier.products_count || 0),
  status: supplier.status,
  description: supplier.remark || '',
  lastSupplyTime: supplier.update_time || supplier.create_time || '',
})
