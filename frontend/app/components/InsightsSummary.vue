<!-- components/InsightsSummary.vue -->
<template>
  <div class="p-5 bg-white rounded-2xl shadow space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="font-semibold text-lg">Riepilogo & Insights</h3>
      <span class="text-xs text-gray-500">Ultimi {{ days }} giorni</span>
    </div>

    <!-- stato -->
    <div v-if="loading" class="text-sm text-gray-500">Sto preparando il sommario…</div>
    <div v-else class="space-y-3">
      <!-- riga headline -->
      <p class="text-sm leading-relaxed">
        Negli ultimi <b>{{ days }}</b> giorni hai registrato
        <b>{{ fmt(summary?.counts_by_type?.smoked || 0) }}</b> fumate,
        <span v-if="summary?.counts_by_type?.wasted"> {{ fmt(summary.counts_by_type.wasted) }} rotte</span>
        <span v-if="summary?.counts_by_type?.gifted"> e {{ fmt(summary.counts_by_type.gifted) }} offerte</span>.
        Media giornaliera: <b>{{ summary?.avg_per_day?.toFixed(2) || '0.00' }}</b> •
        Media settimanale: <b>{{ summary?.avg_per_week?.toFixed(2) || '0.00' }}</b>
      </p>

      <!-- spesa e pacchetti -->
      <div class="flex flex-wrap gap-2 text-sm">
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100">
          💶 Spesa: <b>€ {{ (packsOverview?.total_spent || 0).toFixed(2) }}</b>
        </span>
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100">
          🗃️ Pacchetti: <b>{{ fmt(packsOverview?.total_packs || 0) }}</b>
        </span>
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100" v-if="packDur?.avg_days">
          ⏳ Durata media pack: <b>{{ packDur.avg_days.toFixed(1) }} giorni</b>
        </span>
      </div>

      <!-- picchi & orari -->
      <div class="text-sm leading-relaxed">
        <div v-if="busiestDate">
          📅 Giorno più “intenso”:
          <b>{{ fmtDate(busiestDate.date) }}</b> ({{ busiestDate.count }} fumate).
        </div>
        <div v-if="hourlyPeak">
          ⏰ Fascia oraria più attiva ({{ hourlyDays }}gg): <b>{{ hourlyPeak.hour }}:00–{{ hourlyPeak.hour }}:59</b>
          ({{ hourlyPeak.count }}), <span class="text-gray-500">{{ timezone }}</span>.
        </div>
        <div v-if="intervals.sample" class="mt-1">
          🧭 Intervallo medio: <b>{{ intervals.mean_minutes.toFixed(1) }} min</b>
          (≈ {{ minutesToHM(intervals.mean_minutes) }}), mediana:
          <b>{{ intervals.median_minutes.toFixed(1) }} min</b>
          (≈ {{ minutesToHM(intervals.median_minutes) }}). <span class="text-gray-500">Campione: {{ intervals.sample }}</span>
        </div>
      </div>

      <!-- preferenze brand -->
      <div class="text-sm leading-relaxed" v-if="brandTop?.length">
        🏷️ Preferenze brand (top {{ brandTop.length }} / {{ days }}gg):
        <span v-for="(b, i) in brandTop" :key="b.brand" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 mr-1">
          {{ i+1 }}. {{ b.brand || '—' }} ({{ b.count }})
        </span>
      </div>

      <!-- “spiegone” salutare soft -->
      <div class="p-3 bg-amber-50 text-amber-900 rounded-lg text-sm leading-relaxed">
        <div class="font-medium mb-1">👀 Uno sguardo al ritmo</div>
        <p class="mb-1">
          Con una media di <b>{{ summary?.avg_per_day?.toFixed(2) || '0.00' }}</b> al giorno,
          il ritmo attuale è <b>{{ qualitativePace }}</b>.
          Ridurre i picchi nelle ore “calde” (es. <span v-if="hourlyPeak"><b>{{ hourlyPeak.hour }}:00</b></span><span v-else>fasce mattina/pomeriggio</span>)
          può aiutare a diluire le fumate nella giornata.
        </p>
        <p class="text-xs text-amber-900/80">
          Nota: questi sono indicatori informativi, non consigli medici. Per supporto personalizzato rivolgiti a un professionista.
        </p>
      </div>

      <!-- micro-note -->
      <div class="text-xs text-gray-500">
        Ultimo aggiornamento: {{ fmtDateTime(new Date()) }} · Fuso: {{ timezone }}
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  days: { type: Number, default: 30 },   // finestra per il riassunto
  hourlyDays: { type: Number, default: 7 } // finestra per trend orario
})

const { get } = useApi()
const loading = ref(true)

// dati remoti
const summary = ref(null)          // /smokes/stats/summary?days=...
const intervals = ref({})          // /smokes/stats/intervallo?limit=...
const brandTop = ref([])           // /smokes/stats/brand-top?limit=5&days=...
const packsOverview = ref(null)    // /packs/stats/overview
const packDur = ref(null)          // /packs/stats/durata?days_window=180
const byHour = ref(null)           // /smokes/stats/by-hour?days=...
const timezone = ref('Europe/Rome')

// calcoli locali
const busiestDate = ref(null)      // { date: 'YYYY-MM-DD', count: n }
const qualitativePace = computed(() => {
  const d = Number(summary.value?.avg_per_day || 0)
  if (d >= 20) return 'molto elevato'
  if (d >= 10) return 'elevato'
  if (d >= 5)  return 'moderato'
  if (d > 0)   return 'basso'
  return '—'
})

// utils
const pad2 = (n) => (n < 10 ? '0' + n : '' + n)
const ymd = (d) => `${d.getFullYear()}-${pad2(d.getMonth()+1)}-${pad2(d.getDate())}`
const fmt = (n) => new Intl.NumberFormat('it-IT').format(Number(n||0))
const fmtDate = (s) => {
  const d = new Date(s)
  return d.toLocaleDateString('it-IT', { weekday:'short', day:'2-digit', month:'2-digit' })
}
const fmtDateTime = (d) => d.toLocaleString('it-IT',{ year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' })
const minutesToHM = (m) => {
  const total = Math.max(0, Math.round(m))
  const h = Math.floor(total / 60)
  const mm = total % 60
  return h ? `${h}h ${mm}m` : `${mm}m`
}

const hourlyDays = computed(() => props.hourlyDays)
const hourlyPeak = computed(() => {
  if (!byHour.value?.hours?.length || !Array.isArray(byHour.value.data)) return null
  let max = -1, idx = -1
  byHour.value.data.forEach((v,i) => { if (v > max) { max = v; idx = i }})
  if (idx < 0) return null
  return { hour: byHour.value.hours[idx], count: max }
})

const load = async () => {
  loading.value = true
  try {
    // 1) riassunto ultimi N giorni
    summary.value  = await get(`/smokes/stats/summary?days=${props.days}`)

    // 2) intervalli
    intervals.value = await get('/smokes/stats/intervallo?limit=400')

    // 3) top brand
    brandTop.value = await get(`/smokes/stats/brand-top?limit=5&days=${props.days}`)

    // 4) pacchetti: overview + durata media/mediana
    packsOverview.value = await get('/packs/stats/overview')
    packDur.value = await get('/packs/stats/durata?days_window=180')

    // 5) trend orario ultimi X giorni
    const hr = await get(`/smokes/stats/by-hour?days=${hourlyDays.value}`)
    byHour.value = hr
    timezone.value = hr?.timezone || 'Europe/Rome'

    // 6) “giorno più intenso” negli ultimi N giorni
    //    → prendiamo /smokes e bucket by YYYY-MM-DD (solo type='smoked')
    const all = await get('/smokes')
    const now = Date.now()/1000
    const from = now - props.days * 24 * 3600
    const byDay = new Map()
    all.forEach(s => {
      if (s.type !== 'smoked') return
      if (!s.ts || s.ts < from) return
      const key = ymd(new Date(s.ts * 1000))
      byDay.set(key, (byDay.get(key) || 0) + 1)
    })
    let topKey = null, topVal = -1
    byDay.forEach((v,k) => { if (v > topVal) { topVal = v; topKey = k } })
    busiestDate.value = topKey ? { date: topKey, count: topVal } : null

  } catch (e) {
    console.error('[InsightsSummary] load error', e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
