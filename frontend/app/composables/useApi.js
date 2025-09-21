// composable/useApi.js

export const useApi = () => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase
  const token = useState('token')

  const headers = () => (token.value ? { Authorization: `Bearer ${token.value}` } : {})

  const get = (url) => $fetch(url, { baseURL: base, headers: headers() })
  const post = (url, body) => $fetch(url, { method: 'POST', body, baseURL: base, headers: headers() })
  const patch = (url, body) => $fetch(url, { method: 'PATCH', body, baseURL: base, headers: headers() })
  const del = (url) => $fetch(url, { method: 'DELETE', baseURL: base, headers: headers() })

  return { get, post, patch, del, token }
}
