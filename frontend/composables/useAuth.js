export function useAuth () {
const api = useApi()
const token = useState('token', () => null)
const email = useState('email', () => '')


function setToken (t) {
token.value = t
api.setToken(t)
if (process.client) {
if (t) localStorage.setItem('token', t)
else localStorage.removeItem('token')
}
}


function load () {
if (process.client) {
const t = localStorage.getItem('token')
if (t) setToken(t)
}
}


const isAuthenticated = computed(() => !!token.value)


return { token, email, setToken, load, isAuthenticated }
}