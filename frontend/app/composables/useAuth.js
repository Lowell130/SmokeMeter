// composable/useAuth.js
export const useAuth = () => {
  const { post, get, token } = useApi()
  const user = useState('user', () => null)

  const saveToken = (t) => {
    token.value = t
    if (process.client) localStorage.setItem('token', t)
  }

  const loadToken = () => {
    if (process.client) {
      const t = localStorage.getItem('token')
      if (t) token.value = t
    }
  }

  const register = async (email, password) => {
    await post('/auth/register', { email, password })
    return login(email, password)
  }

  const login = async (email, password) => {
    const res = await post('/auth/login', { email, password })
    saveToken(res.access_token)
    await fetchMe()
  }

  const logout = () => {
    token.value = undefined
    user.value = null
    if (process.client) localStorage.removeItem('token')
  }

  const fetchMe = async () => {
    user.value = await get('/users/me')
  }

  return { user, token, register, login, logout, fetchMe, loadToken }
}
