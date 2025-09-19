// composables/useAuth.js
export function useAuth () {
  const api = useApi()
  const token = useState('token', () => null)
  const refreshToken = useState('refreshToken', () => null)
  const email = useState('email', () => '')

  function setToken (t) {
    token.value = t
    api.setToken(t)
    if (process.client) {
      if (t) localStorage.setItem('token', t)
      else localStorage.removeItem('token')
    }
  }

  function setRefreshToken (r) {
    refreshToken.value = r || null
    if (process.client) {
      if (r) localStorage.setItem('refresh_token', r)
      else localStorage.removeItem('refresh_token')
    }
  }

  function setTokens (access, refresh) {
    setToken(access)
    if (refresh !== undefined) setRefreshToken(refresh)
  }

  function load () {
    if (!process.client) return
    const t = localStorage.getItem('token')
    const r = localStorage.getItem('refresh_token')
    if (t) setToken(t)
    if (r) setRefreshToken(r)
  }

  const isAuthenticated = computed(() => !!token.value)

  return { token, refreshToken, email, isAuthenticated, setToken, setRefreshToken, setTokens, load }
}
