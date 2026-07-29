import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/auth/Login.vue' // 新增：登录页
import Dashboard from '../views/dashboard/Dashboard.vue' // 仪表板页
import UserList from '../views/users/UserList.vue'
import ProductList from '../views/products/ProductList.vue'
import CategoryList from '../views/products/CategoryList.vue'
import InventoryList from '../views/products/InventoryList.vue'
import WarehouseList from '../views/products/WarehouseList.vue'
import SupplierList from '../views/operations/SupplierList.vue'
import SupplierRecordList from '../views/operations/SupplierRecordList.vue'
import SalesAnalysis from '../views/operations/SalesAnalysis.vue'
import OperationLog from '../views/operations/OperationLog.vue'
import PersonalCenter from '../views/users/PersonalCenter.vue'
import { ROLE, getDefaultRouteByRole, getStoredUserRole, hasRouteAccess } from '@/utils/permissions'

const routes = [
  {
    path: '/',
    redirect: '/login', // 根路径重定向到登录页
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '仪表板',
      requiresAuth: true,
      allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER, ROLE.FINANCE, ROLE.CASHIER],
    },
  },
  {
    path: '/users',
    name: 'UserList',
    component: UserList,
    meta: { title: '用户管理', requiresAuth: true, allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN] },
  },
  {
    path: '/products',
    name: 'ProductList',
    component: ProductList,
    meta: {
      title: '商品管理',
      requiresAuth: true,
      allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
    },
  },
  {
    path: '/categories',
    name: 'CategoryList',
    component: CategoryList,
    meta: {
      title: '分类管理',
      requiresAuth: true,
      allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
    },
  },
  {
    path: '/inventory',
    name: 'InventoryList',
    component: InventoryList,
    meta: {
      title: '库存管理',
      requiresAuth: true,
      allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
    },
  },
  {
    path: '/warehouses',
    name: 'WarehouseList',
    component: WarehouseList,
    meta: {
      title: '仓库管理',
      requiresAuth: true,
      allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
    },
  },
  {
    path: '/suppliers',
    name: 'SupplierList',
    component: SupplierList,
    meta: {
      title: '供货商管理',
      requiresAuth: true,
      allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
    },
  },
  {
    path: '/supplier-records',
    name: 'SupplierRecordList',
    component: SupplierRecordList,
    meta: {
      title: '供货记录',
      requiresAuth: true,
      allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.INVENTORY_MANAGER],
    },
  },
  {
    path: '/sales-analysis',
    name: 'SalesAnalysis',
    component: SalesAnalysis,
    meta: {
      title: '销售分析',
      requiresAuth: true,
      allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN, ROLE.FINANCE],
    },
  },
  {
    path: '/operation-log',
    name: 'OperationLog',
    component: OperationLog,
    meta: { title: '操作日志', requiresAuth: true, allowedRoles: [ROLE.SUPER_ADMIN, ROLE.ADMIN] },
  },
  {
    path: '/profile',
    name: 'PersonalCenter',
    component: PersonalCenter,
    meta: {
      title: '个人中心',
      requiresAuth: true,
      allowedRoles: [
        ROLE.SUPER_ADMIN,
        ROLE.ADMIN,
        ROLE.INVENTORY_MANAGER,
        ROLE.FINANCE,
        ROLE.CASHIER,
      ],
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：检查是否需要登录
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = getStoredUserRole()

  if (to.meta?.title) {
    document.title = `${to.meta.title} - 超市库存管理系统`
  }

  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  if (to.path === '/login' && token) {
    next(getDefaultRouteByRole(role))
    return
  }

  if (to.meta.requiresAuth && !hasRouteAccess(role, to.meta.allowedRoles)) {
    next(getDefaultRouteByRole(role))
    return
  }

  next()
})

export default router
