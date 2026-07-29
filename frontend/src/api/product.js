// 商品管理API
import request from './index'

export default {
  // 商品分类
  getCategories(params) {
    return request.get('/products/categories/', { params })
  },
  
  createCategory(data) {
    return request.post('/products/categories/', data)
  },
  
  updateCategory(id, data) {
    return request.put(`/products/categories/${id}/`, data)
  },
  
  deleteCategory(id) {
    return request.delete(`/products/categories/${id}/`)
  },

  getCategoryTree() {
    return request.get('/products/categories/tree/')
  },

  // 供货商管理
  getSuppliers(params) {
    return request.get('/products/suppliers/', { params })
  },

  createSupplier(data) {
    return request.post('/products/suppliers/', data)
  },

  updateSupplier(id, data) {
    return request.put(`/products/suppliers/${id}/`, data)
  },

  deleteSupplier(id) {
    return request.delete(`/products/suppliers/${id}/`)
  },

  // 仓库管理
  getWarehouses(params) {
    return request.get('/products/warehouses/', { params })
  },

  createWarehouse(data) {
    return request.post('/products/warehouses/', data)
  },

  updateWarehouse(id, data) {
    return request.put(`/products/warehouses/${id}/`, data)
  },

  deleteWarehouse(id) {
    return request.delete(`/products/warehouses/${id}/`)
  },
  
  // 商品管理
  getProducts(params) {
    return request.get('/products/products/', { params })
  },
  
  getProduct(id) {
    return request.get(`/products/products/${id}/`)
  },
  
  createProduct(data) {
    return request.post('/products/products/', data)
  },
  
  updateProduct(id, data) {
    return request.put(`/products/products/${id}/`, data)
  },
  
  deleteProduct(id) {
    return request.delete(`/products/products/${id}/`)
  },

  getProductStatistics() {
    return request.get('/products/products/statistics/')
  },
  
  // 库存管理
  getInventories(params) {
    return request.get('/products/inventories/', { params })
  },
  
  updateInventory(id, data) {
    return request.put(`/products/inventories/${id}/`, data)
  },

  getInventorySummary() {
    return request.get('/products/inventories/summary/')
  },

  getInventoryAlerts() {
    return request.get('/products/inventories/stock-alerts/')
  },
  
  // 入库/出库
  inventoryInOut(data) {
    return request.post('/operations/inventory-transactions/in-out/', data)
  }
}
