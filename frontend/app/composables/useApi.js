// composable/useApi.js
export const useApi = () => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase
  // usa cookie per avere disponibilità anche in SSR
  const tokenCookie = useCookie('token', { sameSite: 'lax', path: '/', watch: true })

  const headers = () => (tokenCookie.value ? { Authorization: `Bearer ${tokenCookie.value}` } : {})

  const get = (url) => $fetch(url, { baseURL: base, headers: headers() })
  const post = (url, body) => $fetch(url, { method: 'POST', body, baseURL: base, headers: headers() })
  const patch = (url, body) => $fetch(url, { method: 'PATCH', body, baseURL: base, headers: headers() })
  const del = (url) => $fetch(url, { method: 'DELETE', baseURL: base, headers: headers() })

  return { get, post, patch, del, tokenCookie }
}
