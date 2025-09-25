// middleware/auth.global.js
export default defineNuxtRouteMiddleware((to) => {
  // usa cookie, così funziona anche in SSR
  const tokenCookie = useCookie('token', { sameSite: 'lax', path: '/', watch: true })
  const token = tokenCookie.value || undefined

  const protectedRoutes = ['/dashboard', '/profile', '/packs', '/smokes']
  if (protectedRoutes.includes(to.path) && !token) {
    return navigateTo('/login')
  }
})
