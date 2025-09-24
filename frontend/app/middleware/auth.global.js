// middleware/AuthenticatorAssertionResponse.global.js
export default defineNuxtRouteMiddleware((to) => {
  const token = useState('token')

  if (process.client && !token.value) {
    const t = localStorage.getItem('token')
    if (t) token.value = t
  }

  // aggiunte /packs e /smokes
  const protectedRoutes = ['/dashboard', '/profile', '/packs', '/smokes']
  if (protectedRoutes.includes(to.path) && !token.value) {
    return navigateTo('/login')
  }
})
