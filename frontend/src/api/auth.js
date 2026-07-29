// 认证相关API
import request from './index'

export default {
  // 登录
  login(data) {
    return request.post('/auth/login/', data)
  },
  
  // 登出
  logout() {
    return request.post('/auth/logout/')
  },
  
  // 注册
  register(data) {
    return request.post('/auth/register/', data)
  },
  
  // 获取用户信息
  getUserInfo() {
    return request.get('/auth/profile/')
  },

  // 更新个人资料
  updateProfile(data) {
    return request.put('/auth/profile/', data)
  },

  // 修改密码
  changePassword(data) {
    return request.post('/auth/change-password/', data)
  },

  // 刷新token
  refreshToken(token) {
    return request.post('/auth/refresh/', { refresh: token })
  }
}
