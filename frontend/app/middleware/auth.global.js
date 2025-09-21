// middleware/AuthenticatorAssertionResponse.global.js

export default defineNuxtRouteMiddleware((to) => {
  const token = useState('token')         // nessun useAuth qui

  if (process.client && !token.value) {
    const t = localStorage.getItem('token')
    if (t) token.value = t
  }

  const protectedRoutes = ['/dashboard', '/profile']
  if (protectedRoutes.includes(to.path) && !token.value) {
    return navigateTo('/login')
  }
})
