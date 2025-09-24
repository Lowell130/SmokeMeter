<script setup>
const props = defineProps({
  refreshKey: { type: Number, default: 0 }   // 👈 nuovo prop
})

const { get } = useApi()
const days = ref(7)
const hours = ref([])
const series = ref([])
const total = ref(0)
const timezone = ref('Europe/Rome')
const chartKey = ref(0)                      // 👈 per forzare re-render del ChartArea orario

const load = async () => {
  const res = await get(`/smokes/stats/by-hour?days=${days.value}`)
  hours.value = res.hours || []
  series.value = res.data || []
  total.value = res.total || 0
  timezone.value = res.timezone || 'Europe/Rome'
  chartKey.value++                            // 👈 ChartArea si re-instanzia coi nuovi dati
}

watch(() => props.refreshKey, () => {         // 👈 quando la dashboard fa refresh(), ricarica
  load()
})

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold">Trend orario (ultimi {{ days }} giorni)</h3>
      <select v-model.number="days" @change="load" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-fit p-2.5 pr-8 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
        <option :value="7">7 giorni</option>
        <option :value="14">14 giorni</option>
        <option :value="30">30 giorni</option>
      </select>
    </div>

    <ClientOnly>
      <ChartArea
        :key="chartKey"                     
        :series="[{ name: 'Sigarette', data: series }]"
        :categories="hours"
      >
        <template #headline>{{ total }}</template>
        <template #subtitle>Totale sigarette ({{ timezone }})</template>
      </ChartArea>
    </ClientOnly>
  </div>
</template>
