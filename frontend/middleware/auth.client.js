// Esegue solo sul client (nessun problema con localStorage/SSR)
export default defineNuxtRouteMiddleware(() => {
  const auth = useAuth()
  auth.load() // recupera token da localStorage se presente
  if (!auth.isAuthenticated.value) {
    return navigateTo('/login')
  }
})
