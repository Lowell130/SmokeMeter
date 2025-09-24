<!-- components/ChartArea.vue -->
<template>
  <div class="max-w-full w-full bg-white rounded-lg shadow-sm dark:bg-gray-800 p-4 md:p-6">
    <div class="flex justify-between">
      <!-- (se vuoi rimettere headline/subtitle, lascia gli slot qui) -->
    </div>

    <div ref="el" :id="chartId" class="w-full"></div>

    <div class="grid grid-cols-1 items-center border-gray-200 border-t dark:border-gray-700 justify-between">
      <div class="flex justify-between items-center pt-5">
        <slot name="controls" />
        <div class="flex items-center gap-2">
          <button
            v-if="downloadable"
            @click="downloadPNG"
            class="uppercase text-sm font-semibold inline-flex items-center rounded-lg text-blue-600 hover:text-blue-700 dark:hover:text-blue-500 hover:bg-gray-100 dark:hover:bg-gray-700 px-3 py-2"
          >
            Scarica PNG
          </button>
          <button
            v-if="downloadable"
            @click="downloadCSV"
            class="uppercase text-sm font-semibold inline-flex items-center rounded-lg text-blue-600 hover:text-blue-700 dark:hover:text-blue-500 hover:bg-gray-100 dark:hover:bg-gray-700 px-3 py-2"
          >
            Scarica CSV
          </button>
          <!-- se preferisci un link a una pagina report dedicata, puoi aggiungere:
          <NuxtLink to="/reports/trend"
            class="uppercase text-sm font-semibold inline-flex items-center rounded-lg text-blue-600 hover:text-blue-700 dark:hover:text-blue-500 hover:bg-gray-100 dark:hover:bg-gray-700 px-3 py-2">
            Apri report
          </NuxtLink>
          -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  series: { type: Array, default: () => [] },       // es: [{ name: 'Sigarette', data: [1,2,3] }]
  categories: { type: Array, default: () => [] },   // es: ['2025-09-01', ...]
  downloadable: { type: Boolean, default: true },   // mostra/nasconde i bottoni di export
})

const el = ref(null)
let chart
let ApexCharts
let ro // ResizeObserver

// id univoco per evitare collisioni se il componente è multiplo
const chartId = `area-chart-${Math.random().toString(36).slice(2)}`

const buildOptions = () => ({
  chart: {
    height: '100%',
    width: '100%',
    type: 'area',
    fontFamily: 'Inter, sans-serif',
    dropShadow: { enabled: false },
    toolbar: { show: false }, // abbiamo bottoni custom
  },
  tooltip: { enabled: true, x: { show: false } },
  fill: {
    type: 'gradient',
    gradient: { opacityFrom: 0.55, opacityTo: 0, shade: '#1C64F2', gradientToColors: ['#1C64F2'] },
  },
  dataLabels: { enabled: false },
  stroke: { width: 6 },
  grid: { show: false, strokeDashArray: 4, padding: { left: 2, right: 2, top: 0 } },
  series: props.series || [],
  xaxis: {
    categories: props.categories || [],
    labels: { show: false },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: { show: false },
})

onMounted(async () => {
  ApexCharts = (await import('apexcharts')).default
  if (el.value) {
    chart = new ApexCharts(el.value, buildOptions())
    await chart.render()

    // ResizeObserver → forza un leggero update quando cambia lo spazio disponibile
    ro = new ResizeObserver(() => {
      if (chart) chart.updateOptions({}, false, true)
    })
    ro.observe(el.value)
  }
})

watch(
  () => [props.series, props.categories],
  async () => {
    if (!chart) return
    await chart.updateOptions(
      {
        series: props.series || [],
        xaxis: { categories: props.categories || [] },
      },
      false,
      true
    )
  },
  { deep: true }
)

onBeforeUnmount(() => {
  if (ro && el.value) ro.unobserve(el.value)
  ro = undefined
  if (chart) chart.destroy()
  chart = undefined
})

// --------- Export helpers ---------
const safeFileName = (s) =>
  String(s || 'export')
    .toLowerCase()
    .replace(/[^a-z0-9-_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')

const nowStamp = () => {
  const d = new Date()
  const pad = (n) => (n < 10 ? '0' + n : '' + n)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}`
}

const downloadPNG = async () => {
  if (!chart) return
  try {
    const { imgURI } = await chart.dataURI()
    const a = document.createElement('a')
    a.href = imgURI
    const base = props.series?.[0]?.name || 'chart'
    a.download = `${safeFileName(base)}_${nowStamp()}.png`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  } catch (e) {
    console.error('PNG export failed:', e)
  }
}

const downloadCSV = () => {
  // Costruiamo CSV: prima colonna categories, poi una colonna per ogni serie
  const cats = Array.isArray(props.categories) ? props.categories : []
  const series = Array.isArray(props.series) ? props.series : []
  const headers = ['category', ...series.map((s) => s?.name ?? 'series')]
  const rows = []

  for (let i = 0; i < cats.length; i++) {
    const row = [cats[i]]
    for (let s = 0; s < series.length; s++) {
      const val = Array.isArray(series[s]?.data) ? series[s].data[i] : ''
      row.push(val ?? '')
    }
    rows.push(row)
  }

  const toCSV = (arr) =>
    arr
      .map((row) =>
        row
          .map((cell) => {
            const v = cell == null ? '' : String(cell)
            // escape minimale
            if (/[",;\n]/.test(v)) return `"${v.replace(/"/g, '""')}"`
            return v
          })
          .join(',')
      )
      .join('\n')

  const csv = [headers, ...rows]
  const blob = new Blob([toCSV(csv)], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  const base = series?.[0]?.name || 'chart'
  a.href = url
  a.download = `${safeFileName(base)}_${nowStamp()}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>
