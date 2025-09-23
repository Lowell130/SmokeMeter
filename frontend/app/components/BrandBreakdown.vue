<template>
  <div class="p-4 bg-white rounded-2xl shadow">
    <h3 class="font-semibold mb-4">Top brand (fumate)</h3>
    <ClientOnly>
      <div ref="el" class="w-full h-64"></div>
    </ClientOnly>
    <div class="mt-3 text-xs text-gray-500">Ultimi {{ days }} giorni</div>
  </div>
</template>

<script setup>
const props = defineProps({
  data: { type: Array, default: () => [] }, // [{brand,count}]
  days: { type: Number, default: 90 }
})
const el = ref(null)
let chart, ApexCharts

const buildOptions = () => {
  const labels = props.data.map(x => x.brand || '—')
  const series = props.data.map(x => Number(x.count || 0))
  return {
    chart: { type: 'donut' },
    labels,
    series,
    legend: { position: 'bottom' },
    dataLabels: { enabled: false },
  }
}

onMounted(async () => {
  ApexCharts = (await import('apexcharts')).default
  if (el.value) {
    chart = new ApexCharts(el.value, buildOptions())
    await chart.render()
  }
})

watch(() => props.data, async () => {
  if (chart) {
    await chart.updateOptions(buildOptions(), false, true)
  }
}, { deep: true })

onBeforeUnmount(() => { if (chart) chart.destroy() })
</script>
