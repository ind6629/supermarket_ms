/**
 * 获取头像完整 URL
 * @param {string} path - 头像路径，如 avatars/xxx.jpg 或 /media/avatars/xxx.jpg
 * @returns {string} 完整 URL 或空字符串
 */
export function getAvatarUrl(path) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  // 后端可能返回 /media/avatars/xxx 或 media/avatars/xxx，避免重复拼接
  const normalized = path.replace(/^\/+/, '').replace(/^media\/+/, '')
  return `${window.location.origin}/media/${normalized}`
}
