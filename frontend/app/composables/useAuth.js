// composable/useAuth.js
export const useAuth = () => {
  const { post, get, tokenCookie } = useApi()
  const user = useState('user', () => null)
  // opzionale: mantenere anche uno state locale per reattività
  const tokenState = useState('token', () => tokenCookie.value || undefined)

  const saveToken = (t) => {
    tokenState.value = t
    tokenCookie.value = t
    // backward compat: conserva in localStorage per eventuali logiche client-only
    if (process.client) localStorage.setItem('token', t)
  }

  const loadToken = () => {
    if (process.server) {
      // lato server: cookie è già disponibile tramite useCookie -> tokenCookie.value
      tokenState.value = tokenCookie.value || undefined
      return
    }
    // lato client: preferisci cookie, fallback su localStorage
    const fromCookie = tokenCookie.value
    if (fromCookie) {
      tokenState.value = fromCookie
      return
    }
    const t = localStorage.getItem('token')
    if (t) {
      tokenState.value = t
      tokenCookie.value = t
    }
  }

  const register = async (email, password) => {
    await post('/auth/register', { email, password })
    return login(email, password)
  }

  const login = async (email, password) => {
    const res = await post('/auth/login', { email, password })
    const t = res.access_token
    saveToken(t)
    await fetchMe()
  }

  const logout = () => {
    tokenState.value = undefined
    user.value = null
    tokenCookie.value = null
    if (process.client) localStorage.removeItem('token')
  }

  const fetchMe = async () => {
    // usa useApi.get che prende headers dal cookie
    user.value = await get('/users/me')
  }

  return { user, token: tokenState, register, login, logout, fetchMe, loadToken }
}
