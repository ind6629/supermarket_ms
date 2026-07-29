export const ROLE = {
  SUPER_ADMIN: 0,
  ADMIN: 1,
  INVENTORY_MANAGER: 2,
  FINANCE: 3,
  CASHIER: 4,
}

export const normalizeRole = (role) => {
  if (role === '' || role == null) return null
  const parsed = Number(role)
  return Number.isNaN(parsed) ? null : parsed
}

export const hasRouteAccess = (role, allowedRoles) => {
  if (!Array.isArray(allowedRoles) || allowedRoles.length === 0) {
    return true
  }

  const normalizedRole = normalizeRole(role)
  return normalizedRole != null && allowedRoles.includes(normalizedRole)
}

export const getStoredUserRole = () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    return normalizeRole(user?.role)
  } catch (error) {
    return null
  }
}

export const getDefaultRouteByRole = (role) => {
  const normalizedRole = normalizeRole(role)

  switch (normalizedRole) {
    case ROLE.FINANCE:
      return '/sales-analysis'
    case ROLE.INVENTORY_MANAGER:
      return '/inventory'
    case ROLE.CASHIER:
      return '/dashboard'
    case ROLE.SUPER_ADMIN:
    case ROLE.ADMIN:
    default:
      return '/dashboard'
  }
}
