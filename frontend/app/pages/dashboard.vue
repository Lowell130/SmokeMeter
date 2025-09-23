<!-- pages/dashboard.vue -->
<template>
  <div class="space-y-6">
    <StatsCards :stats="stats" :packs="packs" />

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <AddSmokeCard :packs="packs" @added="refresh" />
      <AddPackCard @added="refresh" />
      
    </div>

      <div class="space-y-6">
    <!-- …tuo contenuto… -->
    <InsightsSummary :days="30" :hourly-days="7" />
    <!-- …tuo contenuto… -->
  </div>

    <!-- <PacksTable :packs="packs" @deleted="refresh" @updated="refresh" />

    <SmokesTable :limit="20" :refresh-key="refreshTick" @deleted="refresh" />  -->

    <!-- RIGA METRICHE -->
    <div class="grid grid-cols-1 gap-4">
      <MetricsStrip :data="summary" />
    </div>

    <!-- RIGA BRAND / PACING -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <BrandBreakdown :data="brandTop" :days="90" />
      <!-- QUI: passa i dati veri e forza re-render quando fai refresh -->
      <PacingCard :key="refreshTick" :data="pacing" />
    </div>

    <!-- HEATMAP -->
    <div class="grid grid-cols-1 gap-4">
      <WeeklyHeatmap
        v-if="heatmap?.matrix"
        :matrix="heatmap.matrix"
        :rows="heatmap.rows"
        :cols="heatmap.cols"
        :days="heatmap.days"
      />
    </div>

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
            <div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            <span class="ms-3 text-sm font-medium text-gray-900">
              {{ isWeekly ? 'Settimanale' : 'Giornaliero' }}
            </span>
          </label>
        </div>

        <ClientOnly>
          <ChartArea
            :key="dailyKey"
            :series="[{ name: 'Sigarette', data: chartData }]"
            :categories="categories"
          />
        </ClientOnly>
      </div>

      <!-- Trend orario -->
      <div class="p-4 bg-white rounded-2xl shadow">
        <HourlyTrendCard :refresh-key="refreshTick" />
      </div>
    </div>
  </div>
</template>

<script setup>
import PacksTable from '~/components/PacksTable.vue'
import HourlyTrendCard from '~/components/HourlyTrendCard.vue'
import SmokesTable from '~/components/SmokesTable.vue'
import MetricsStrip from '~/components/MetricsStrip.vue'
import BrandBreakdown from '~/components/BrandBreakdown.vue'
import PacingCard from '~/components/PacingCard.vue'
import WeeklyHeatmap from '~/components/WeeklyHeatmap.vue'



const { get } = useApi()

const stats = ref({ total_smokes: 0, total_spent: 0 })
const packs = ref([])

const smokesRaw = ref([])
const isWeekly = ref(false)

const categories = ref([])
const chartData = ref([])

const refreshTick = ref(0)
const dailyKey = ref(0)

// nuove metriche
const summary = ref({})       // /smokes/stats/summary
const packDur = ref({})       // /packs/stats/durata
const brandTop = ref([])      // /smokes/stats/brand-top
const heatmap = ref({})       // /smokes/stats/heatmap
const pacing = ref({})        // /smokes/stats/intervallo  <-- IMPORTANTE

// ---------- utilità ----------
const pad2 = (n) => (n < 10 ? '0' + n : '' + n)
const ymd = (d) => `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`

const mondayStartOfWeek = (d) => {
  const x = new Date(d.getTime())
  const day = x.getDay() === 0 ? 7 : x.getDay()
  x.setHours(0, 0, 0, 0)
  x.setDate(x.getDate() - (day - 1))
  return x
}

// ---------- aggregazioni grafico daily/weekly ----------
const buildDaily = (smokes) => {
  const map = new Map()
  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 24 * 3600 * 1000)
    map.set(ymd(d), 0)
  }
  smokes.forEach((s) => {
    if (s.type && s.type !== 'smoked') return
    const key = ymd(new Date(s.ts * 1000))
    if (map.has(key)) map.set(key, (map.get(key) || 0) + 1)
  })
  return { categories: Array.from(map.keys()), data: Array.from(map.values()) }
}

const buildWeekly = (smokes) => {
  const weeks = []
  const now = new Date()
  let cursor = mondayStartOfWeek(now)
  for (let i = 11; i >= 0; i--) {
    const d = new Date(cursor.getTime() - i * 7 * 24 * 3600 * 1000)
    weeks.push(mondayStartOfWeek(d))
  }
  const labels = weeks.map((w) => `${pad2(w.getDate())}/${pad2(w.getMonth() + 1)}`)
  const counts = new Array(weeks.length).fill(0)

  smokes.forEach((s) => {
    if (s.type && s.type !== 'smoked') return
    const wkStart = mondayStartOfWeek(new Date(s.ts * 1000)).getTime()
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
  dailyKey.value++
}

const refresh = async () => {
  // base
  packs.value = await get('/packs')

  // overview spesa/sigarette
  const byPacks  = await get('/packs/stats/overview')  // se non esiste questo endpoint, torna a /smokes/stats/overview per la spesa
  const bySmokes = await get('/smokes/stats/overview')

  stats.value = {
    total_smokes: Number(bySmokes?.total_smokes || 0),
    total_spent : Number(byPacks?.total_spent  || 0)
  }

  // pacing (Ritmo fumate)
  // se vuoi anche gli intervalli per sparkline: aggiungi ?include_intervals=true al tuo endpoint
  pacing.value = await get('/smokes/stats/intervallo?limit=200')

  // nuove metriche
  summary.value  = await get('/smokes/stats/summary?days=30')
  packDur.value  = await get('/packs/stats/durata?days_window=180')
  brandTop.value = await get('/smokes/stats/brand-top?limit=5&days=90')
  heatmap.value  = await get('/smokes/stats/heatmap?days=30')

  // proiezione mensile semplice
  const pm = Number(byPacks?.total_spent || 0)
  summary.value = {
    ...summary.value,
    pack_days_avg: packDur.value?.avg_days ?? 0,
    pack_days_median: packDur.value?.median_days ?? 0,
    projected_monthly: pm
  }

  // grafico daily/weekly
  smokesRaw.value = await get('/smokes')
  recompute()

  // tick figli (HourlyTrendCard, SmokesTable, PacingCard)
  refreshTick.value++
}

watch(isWeekly, () => recompute())
onMounted(refresh)
</script>
