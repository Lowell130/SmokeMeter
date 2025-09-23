<template>
  <div class="p-4 bg-white rounded-2xl shadow">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold">Heatmap settimanale</h3>
      <div class="text-xs text-gray-500">Ultimi {{ days }} giorni</div>
    </div>
    <ClientOnly>
      <div ref="el" class="w-full h-80"></div>
    </ClientOnly>
  </div>
</template>

<script setup>
const props = defineProps({
  matrix: { type: Array, default: () => [] }, // 7x24
  rows:   { type: Array, default: () => ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"] },
  cols:   { type: Array, default: () => Array.from({length:24}, (_,h)=>h.toString().padStart(2,'0')) },
  days:   { type: Number, default: 30 }
})
const el = ref(null)
let chart, ApexCharts

const buildOptions = () => {
  const series = props.rows.map((label, rIdx) => ({
    name: label,
    data: (props.matrix[rIdx] || []).map((v, cIdx) => ({ x: props.cols[cIdx], y: Number(v || 0) }))
  }))
  return {
    chart: { type: 'heatmap' },
    dataLabels: { enabled: false },
    xaxis: { type: 'category', categories: props.cols },
    series
  }
}

onMounted(async () => {
  ApexCharts = (await import('apexcharts')).default
  if (el.value) {
    chart = new ApexCharts(el.value, buildOptions())
    await chart.render()
  }
})

watch(() => [props.matrix, props.rows, props.cols], async () => {
  if (chart) await chart.updateOptions(buildOptions(), false, true)
}, { deep: true })

onBeforeUnmount(() => chart && chart.destroy())
</script>
