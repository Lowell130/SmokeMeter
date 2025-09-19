<!-- components/TrendChart.vue -->
<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed, unref } from 'vue'

const props = defineProps({
  series: { type: [Array, Object], default: () => [] },
  title: String
})

const el = ref(null)
let chart = null

const seriesArr = computed(() => {
  const s = unref(props.series) ?? []
  return Array.isArray(s) ? s : []
})

const labels = computed(() => seriesArr.value.map((_, i) => i + 1))

onMounted(async () => {
  const { default: ApexCharts } = await import('apexcharts')
  chart = new ApexCharts(el.value, {
    chart: { height: '100%', maxWidth: '100%', type: 'area', toolbar: { show: false } },
    tooltip: { enabled: true, x: { show: false } },
    fill: { type: 'gradient', gradient: { opacityFrom: 0.55, opacityTo: 0 } },
    dataLabels: { enabled: false },
    stroke: { width: 3, curve: 'smooth' },
    grid: { show: false, strokeDashArray: 4, padding: { left: 2, right: 2, top: 0 } },
    series: [{ name: 'Sigarette', data: seriesArr.value }],
    xaxis: { categories: labels.value },
    yaxis: { min: 0 }
  })
  await chart.render()
})

watch([seriesArr, labels], async () => {
  if (!chart) return
  await chart.updateOptions({ xaxis: { categories: labels.value } })
  await chart.updateSeries([{ name: 'Sigarette', data: seriesArr.value }])
})

onBeforeUnmount(() => { if (chart) { chart.destroy(); chart = null } })
</script>

<template>
  <div class="border p-4 rounded-xl">
    <div class="font-semibold mb-2">{{ title }}</div>
    <client-only>
      <div ref="el" class="w-full h-[300px]"></div>
    </client-only>
  </div>
</template>
