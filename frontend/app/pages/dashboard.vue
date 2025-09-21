<template>
  <div class="space-y-6">
    <StatsCards :stats="stats" :packs="packs" />
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <AddPackCard @added="refresh" />
      <AddSmokeCard :packs="packs" @added="refresh" />
    </div>
    <div class="p-4 bg-white rounded-2xl shadow">
      <h3 class="font-semibold mb-4">Trend (ultimo mese)</h3>
      <ClientOnly>
        <ChartArea :series="[{ name: 'Sigarette', data: chartData }]" :categories="categories" />
      </ClientOnly>
    </div>
  </div>
</template>

<script setup>
const { get } = useApi()
const stats = ref({ total_smokes: 0, total_spent: 0 })
const packs = ref([])
const categories = ref([])
const chartData = ref([])

const refresh = async () => {
  packs.value = await get('/packs')
  stats.value = await get('/smokes/stats/overview')
  const smokes = await get('/smokes')
  const byDay = new Map()
  const now = Date.now()
  for (let i = 29; i >= 0; i--) {
    const d = new Date(now - i * 24 * 3600 * 1000)
    const key = d.toISOString().slice(0, 10)
    byDay.set(key, 0)
  }
  smokes.forEach((s) => {
    const key = new Date(s.ts * 1000).toISOString().slice(0, 10)
    if (byDay.has(key)) byDay.set(key, (byDay.get(key) || 0) + 1)
  })
  categories.value = Array.from(byDay.keys())
  chartData.value = Array.from(byDay.values())
}

onMounted(refresh)
</script>
