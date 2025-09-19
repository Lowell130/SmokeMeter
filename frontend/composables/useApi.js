export function useApi () {
  const { public: { apiBase } } = useRuntimeConfig()
  const base = apiBase || 'http://127.0.0.1:8000'
  const token = useState('token', () => null)

  const headers = () => token.value ? { Authorization: `Bearer ${token.value}` } : {}

  async function request (method, url, { body, opts = {}, retry = true } = {}) {
    try {
      return await $fetch(`${base}${url}`, {
        method,
        body,
        ...opts,
        headers: { 'Content-Type': 'application/json', ...headers(), ...(opts.headers || {}) }
      })
    } catch (err) {
      const status = err?.status || err?.response?.status
      // tenta refresh se 401 e abbiamo un refresh_token
      if (status === 401 && retry) {
        const auth = useAuth()
        auth.load()
        const rt = auth.refreshToken.value
        if (rt) {
          try {
            const refreshed = await $fetch(`${base}/auth/refresh`, {
              method: 'POST',
              body: { refresh_token: rt },
              headers: { 'Content-Type': 'application/json' }
            })
            auth.setTokens(refreshed.access_token, refreshed.refresh_token) // se backend non ruota, verrà ignorato
            // ritenta una sola volta
            return await request(method, url, { body, opts, retry: false })
          } catch (e) {
            // refresh fallito → logout soft
            auth.setTokens(null, null)
            throw e
          }
        }
      }
      throw err
    }
  }

  return {
    setToken: (t) => { token.value = t },
    get:   (url, opts = {}) => request('GET', url, { opts }),
    post:  (url, body, opts = {}) => request('POST', url, { body, opts }),
    patch: (url, body, opts = {}) => request('PATCH', url, { body, opts }),
  }
}
