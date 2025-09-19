<!-- components/HourlyBar.vue -->
<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed, unref } from 'vue'

const props = defineProps({
  hist: { type: [Array, Object], default: () => [] },
  title: String
})

const el = ref(null)
let chart = null

// stato toggle: false = Totale, true = Percentuale
const percentMode = ref(false)

// accetta Array o Ref(Array)
const histArr = computed(() => {
  const h = unref(props.hist) ?? []
  return Array.isArray(h) ? h : []
})

const labels = Array.from({ length: 24 }, (_, i) => `${i}:00`)

const percentData = computed(() => {
  const sum = histArr.value.reduce((a, b) => a + (Number(b) || 0), 0)
  if (!sum) return Array(24).fill(0)
  // una cifra decimale
  return histArr.value.map(v => Math.round(((Number(v) || 0) / sum) * 1000) / 10)
})

const displayData = computed(() => percentMode.value ? percentData.value : histArr.value)
const seriesName  = computed(() => percentMode.value ? 'Distribuzione (%)' : 'Sigarette')

const makeOptions = () => ({
  chart: {
    height: '100%',
    maxWidth: '100%',
    type: 'bar',
    toolbar: { show: false },
    fontFamily: 'Inter, sans-serif'
  },
  dataLabels: { enabled: false },
  grid: { show: false, strokeDashArray: 4, padding: { left: 2, right: 2, top: 0 } },
  series: [{ name: seriesName.value, data: displayData.value }],
  xaxis: { categories: labels, labels: { show: true }, axisBorder: { show: false }, axisTicks: { show: false } },
  yaxis: percentMode.value
    ? { min: 0, max: 100, labels: { formatter: (val) => `${val}%` } }
    : { min: 0 }
})

onMounted(async () => {
  const { default: ApexCharts } = await import('apexcharts')
  chart = new ApexCharts(el.value, makeOptions())
  await chart.render()
})

watch([displayData, percentMode], async () => {
  if (!chart) return
  await chart.updateOptions(makeOptions(), false, true)
})

onBeforeUnmount(() => { if (chart) { chart.destroy(); chart = null } })
</script>

<template>
  <div class="border p-4 rounded-xl">
    <div class="flex items-center justify-between mb-2">
      <div class="font-semibold">{{ title }}</div>

      <!-- Toggle Totale ↔ % (template Flowbite adattato con v-model) -->
      <label class="inline-flex items-center cursor-pointer">
        <input type="checkbox" class="sr-only peer" v-model="percentMode">
        <div
          class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300
                 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700
                 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full
                 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px]
                 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all
                 dark:border-gray-600 peer-checked:bg-blue-600 dark:peer-checked:bg-blue-600">
        </div>
        <span class="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">
          {{ percentMode ? '% distribuzione' : 'Totale' }}
        </span>
      </label>
    </div>

    <client-only>
      <div ref="el" class="w-full h-[300px]"></div>
    </client-only>
  </div>
</template>
