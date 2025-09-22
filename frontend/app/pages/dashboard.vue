<template>
  <div class="space-y-6">
    <StatsCards :stats="stats" :packs="packs" />

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <AddPackCard @added="refresh" />
      <AddSmokeCard :packs="packs" @added="refresh" />
    </div>

  <PacksTable
  :packs="packs"
  @deleted="refresh"
  @updated="refresh"
/>


    <!-- Due card grafiche con stesso stile -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Trend giornaliero/settimanale -->
      <div class="p-4 bg-white rounded-2xl shadow">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold">
            Trend
            <span v-if="!isWeekly">(ultimi 30 giorni)</span>
            <span v-else>(ultime 12 settimane)</span>
          </h3>

          <!-- TOGGLE: Giornaliero ↔ Settimanale -->
          <label class="inline-flex items-center cursor-pointer">
            <input type="checkbox" class="sr-only peer" v-model="isWeekly">
            <div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            <span class="ms-3 text-sm font-medium text-gray-900">
              {{ isWeekly ? 'Settimanale' : 'Giornaliero' }}
            </span>
          </label>
        </div>

        <ClientOnly>
          <ChartArea
            :series="[{ name: 'Sigarette', data: chartData }]"
            :categories="categories"
          />
        </ClientOnly>
      </div>

      <!-- Trend orario -->
      <div class="p-4 bg-white rounded-2xl shadow">
        <HourlyTrendCard />
      </div>
    </div>
  </div>
</template>

<script setup>
import PacksTable from '~/components/PacksTable.vue'
import HourlyTrendCard from '~/components/HourlyTrendCard.vue'

const { get } = useApi()
const stats = ref({ total_smokes: 0, total_spent: 0 })
const packs = ref([])

const smokesRaw = ref([])      // <- manteniamo i raw per ri-aggregare al toggle
const isWeekly = ref(false)    // <- toggle UI

const categories = ref([])
const chartData = ref([])

// utilità
const pad2 = (n) => (n < 10 ? '0' + n : '' + n)
const ymd = (d) => `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`

const mondayStartOfWeek = (d) => {
  const x = new Date(d.getTime())
  const day = x.getDay() === 0 ? 7 : x.getDay() // Mon=1..Sun=7
  x.setHours(0, 0, 0, 0)
  x.setDate(x.getDate() - (day - 1))
  return x
}

const buildDaily = (smokes) => {
  // ultimi 30 giorni, bucket per YYYY-MM-DD
  const map = new Map()
  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 24 * 3600 * 1000)
    map.set(ymd(d), 0)
  }
  smokes.forEach((s) => {
    if (s.type && s.type !== 'smoked') return // <-- conta solo fumate; rimuovi questa riga per includere tutto
    const key = ymd(new Date(s.ts * 1000))
    if (map.has(key)) map.set(key, (map.get(key) || 0) + 1)
  })
  return { categories: Array.from(map.keys()), data: Array.from(map.values()) }
}

const buildWeekly = (smokes) => {
  // ultime 12 settimane, bucket per inizio settimana (Lunedì)
  const weeks = []
  const now = new Date()
  let cursor = mondayStartOfWeek(now)
  // costruiamo 12 settimane retrocedendo
  for (let i = 11; i >= 0; i--) {
    const d = new Date(cursor.getTime() - i * 7 * 24 * 3600 * 1000)
    weeks.push(mondayStartOfWeek(d))
  }

  const labels = weeks.map((w) => {
    const dd = pad2(w.getDate())
    const mm = pad2(w.getMonth() + 1)
    return `${dd}/${mm}` // label compatta: data di inizio settimana
  })
  const counts = new Array(weeks.length).fill(0)

  smokes.forEach((s) => {
    if (s.type && s.type !== 'smoked') return // <-- solo fumate
    const d = new Date(s.ts * 1000)
    const wkStart = mondayStartOfWeek(d).getTime()
    // trova l'indice della settimana corrispondente
    for (let i = 0; i < weeks.length; i++) {
      if (weeks[i].getTime() === wkStart) {
        counts[i] += 1
        break
      }
    }
  })
  return { categories: labels, data: counts }
}

const recompute = () => {
  const source = smokesRaw.value || []
  const result = isWeekly.value ? buildWeekly(source) : buildDaily(source)
  categories.value = result.categories
  chartData.value = result.data
}

const refresh = async () => {
  packs.value = await get('/packs')
  stats.value = await get('/smokes/stats/overview')
  smokesRaw.value = await get('/smokes')
  recompute()
}

watch(isWeekly, () => recompute())

onMounted(refresh)
</script>
