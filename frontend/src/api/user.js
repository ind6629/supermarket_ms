// 用户管理API
import request from './index'

export default {
  // 获取用户列表
  getUsers(params) {
    return request.get('/users/', { params })
  },
  
  // 获取单个用户
  getUser(id) {
    return request.get(`/users/${id}/`)
  },
  
  // 创建用户
  createUser(data) {
    return request.post('/users/', data)
  },
  
  // 更新用户
  updateUser(id, data) {
    return request.put(`/users/${id}/`, data)
  },
  
  // 删除用户
  deleteUser(id) {
    return request.delete(`/users/${id}/`)
  },
  
  // 重置密码
  resetPassword(id, data) {
    return request.post(`/users/${id}/reset-password/`, data)
  },

  // 启用用户
  activateUser(id) {
    return request.post(`/users/${id}/activate/`)
  },

  // 停用用户
  deactivateUser(id) {
    return request.post(`/users/${id}/deactivate/`)
  },

  // 审核注册申请
  reviewRegistration(id, data) {
    return request.post(`/users/${id}/review/`, data)
  },
}
