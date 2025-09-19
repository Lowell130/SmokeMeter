export function useApi () {
const config = useRuntimeConfig()
const token = useState('token', () => null)


const headers = () => token.value ? { Authorization: `Bearer ${token.value}` } : {}


return {
setToken: (t) => { token.value = t },
get: (url, opts = {}) => $fetch(`${config.public.apiBase}${url}`, { ...opts, headers: { ...headers(), ...(opts.headers||{}) } }),
post: (url, body, opts = {}) => $fetch(`${config.public.apiBase}${url}`, { method: 'POST', body, ...opts, headers: { 'Content-Type':'application/json', ...headers(), ...(opts.headers||{}) } }),
patch: (url, body, opts = {}) => $fetch(`${config.public.apiBase}${url}`, { method: 'PATCH', body, ...opts, headers: { 'Content-Type':'application/json', ...headers(), ...(opts.headers||{}) } }),
}
}