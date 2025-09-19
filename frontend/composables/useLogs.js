export function useLogs () {
const api = useApi()
const state = useState('logs', () => ({ today: 0, series: [], hourly: [] }))


async function refresh () {
const t = await api.get('/log/today')
const s = await api.get('/metrics/summary?range=7d')
const h = await api.get('/metrics/hourly?range=30d')
state.value.today = t.cigs_today
state.value.series = s.daily_series
state.value.hourly = h.hist
}


async function addCig () { await api.post('/log/cigarette', {}); await refresh() }


return { ...toRefs(state.value), refresh, addCig }
}