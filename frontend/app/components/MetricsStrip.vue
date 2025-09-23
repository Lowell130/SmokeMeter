<template>
  <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-xs text-gray-500">Media giornaliera</div>
      <div class="text-2xl font-bold">{{ fmt(avg_per_day) }}</div>
      <div class="text-xs text-gray-400">ultimi {{ days }} giorni</div>
    </div>
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-xs text-gray-500">Media settimanale</div>
      <div class="text-2xl font-bold">{{ fmt(avg_per_week) }}</div>
      <div class="text-xs text-gray-400">ultimi {{ days }} giorni</div>
    </div>
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-xs text-gray-500">Sprechi (wasted)</div>
      <div class="text-2xl font-bold">{{ wastedCount }}</div>
      <div class="text-xs text-gray-400">{{ wastedPct }}% degli eventi</div>
    </div>
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-xs text-gray-500">Durata media pacchetto</div>
      <div class="text-2xl font-bold">{{ packDaysAvg }} gg</div>
      <div class="text-xs text-gray-400">mediana: {{ packDaysMedian }} gg</div>
    </div>
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-xs text-gray-500">Spesa mensile (proiez.)</div>
      <div class="text-2xl font-bold">€ {{ Number(projectedMonthly || 0).toFixed(2) }}</div>
      <div class="text-xs text-gray-400">stima da ultimi {{ days }} gg</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  data: { type: Object, default: () => ({}) }
})
const days = computed(() => props.data.days || 30)
const avg_per_day = computed(() => props.data.avg_per_day || 0)
const avg_per_week = computed(() => props.data.avg_per_week || 0)
const wastedCount = computed(() => props.data.counts_by_type?.wasted || 0)
const wastedPct = computed(() => {
  const total = props.data.total_all || 0
  return total ? Math.round((wastedCount.value / total) * 100) : 0
})
const packDaysAvg = computed(() => props.data.pack_days_avg ?? 0)
const packDaysMedian = computed(() => props.data.pack_days_median ?? 0)
const projectedMonthly = computed(() => props.data.projected_monthly || 0)
const fmt = (n) => Number(n || 0).toFixed(2)
</script>
