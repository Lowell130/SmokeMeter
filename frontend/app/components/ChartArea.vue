<template>
  <div class="max-w-full w-full bg-white rounded-lg shadow-sm dark:bg-gray-800 p-4 md:p-6">
    <div class="flex justify-between">
      <div>
        <h5 class="leading-none text-3xl font-bold text-gray-900 dark:text-white pb-2">
          <slot name="headline">32.4k</slot>
        </h5>
        <p class="text-base font-normal text-gray-500 dark:text-gray-400">
          <slot name="subtitle">Users this week</slot>
        </p>
      </div>
      <div class="flex items-center px-2.5 py-0.5 text-base font-semibold text-green-500 dark:text-green-500 text-center">
        <slot name="delta">12%</slot>
        <svg class="w-3 h-3 ms-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 14">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13V1m0 0L1 5m4-4 4 4"/>
        </svg>
      </div>
    </div>

    <div ref="el" :id="chartId" class="w-full"></div>

    <div class="grid grid-cols-1 items-center border-gray-200 border-t dark:border-gray-700 justify-between">
      <div class="flex justify-between items-center pt-5">
        <slot name="controls" />
        <a
          href="#"
          class="uppercase text-sm font-semibold inline-flex items-center rounded-lg text-blue-600 hover:text-blue-700 dark:hover:text-blue-500 hover:bg-gray-100 dark:hover:bg-gray-700 px-3 py-2">
          Users Report
          <svg class="w-2.5 h-2.5 ms-1.5 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 6 10">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 9 4-4-4-4"/>
          </svg>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps(['series', 'categories'])
const el = ref(null)
let chart

// id univoco per evitare collisioni se il componente è multiplo
const chartId = `area-chart-${Math.random().toString(36).slice(2)}`

const buildOptions = () => ({
  chart: {
    height: '100%',
    width: '100%',
    type: 'area',
    fontFamily: 'Inter, sans-serif',
    dropShadow: { enabled: false },
    toolbar: { show: false }
  },
  tooltip: { enabled: true, x: { show: false } },
  fill: { type: 'gradient', gradient: { opacityFrom: 0.55, opacityTo: 0, shade: '#1C64F2', gradientToColors: ['#1C64F2'] } },
  dataLabels: { enabled: false },
  stroke: { width: 6 },
  grid: { show: false, strokeDashArray: 4, padding: { left: 2, right: 2, top: 0 } },
  series: props.series || [],
  xaxis: { categories: props.categories || [], labels: { show: false }, axisBorder: { show: false }, axisTicks: { show: false } },
  yaxis: { show: false }
})

let ApexCharts
const onResize = () => { if (chart) chart.resize() }

onMounted(async () => {
  ApexCharts = (await import('apexcharts')).default
  if (el.value) {
    chart = new ApexCharts(el.value, buildOptions())
    await chart.render()
    window.addEventListener('resize', onResize)
  }
})

watch(() => [props.series, props.categories], async () => {
  if (chart) {
    await chart.updateOptions(
      { series: props.series || [], xaxis: { categories: props.categories || [] } },
      false,
      true
    )
  }
}, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  if (chart) chart.destroy()
})
</script>
