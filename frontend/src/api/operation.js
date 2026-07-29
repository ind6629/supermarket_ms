// 运营管理API
import request from './index'

export default {
  // 操作日志
  getOperationLogs(params) {
    return request.get('/operations/operation-logs/', { params })
  },

  getRecentActivities(params) {
    return request.get('/operations/operation-logs/recent-activities/', { params })
  },

  getOperationStatistics(params) {
    return request.get('/operations/operation-logs/statistics/', { params })
  },
  
  // 库存交易
  getInventoryTransactions(params) {
    return request.get('/operations/inventory-transactions/', { params })
  },
  
  // 销售记录
  getSalesRecords(params) {
    return request.get('/operations/sales-records/', { params })
  },
  
  createSalesRecord(data) {
    return request.post('/operations/sales-records/', data)
  },

  createSalesWithItems(data) {
    return request.post('/operations/sales-records/create-with-items/', data)
  },

  getSalesStatistics() {
    return request.get('/operations/sales-records/statistics/')
  },

  searchSales(data) {
    return request.post('/operations/sales-records/search/', data)
  },
  
  // 销售分析
  getSalesAnalysis(params) {
    return request.get('/operations/sales-analyses/', { params })
  },

  getSalesOverview() {
    return request.get('/operations/sales-analyses/overview/')
  },

  getSalesReport(params) {
    return request.get('/operations/sales-analyses/report/', { params })
  },
  
  // 收银数据导入
  getCashImports(params) {
    return request.get('/operations/cash-imports/', { params })
  },

  uploadCashData(formData) {
    return request.post('/operations/cash-imports/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}
