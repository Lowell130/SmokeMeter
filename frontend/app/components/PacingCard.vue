<template>
  <div class="p-4 bg-white rounded-2xl shadow">
    <h3 class="font-semibold mb-2">Ritmo fumate (intervallo)</h3>

    <p class="text-sm text-gray-600 mb-4 leading-snug">
      Questa sezione mostra <strong>ogni quanto tempo in media fumi una sigaretta</strong>,
      calcolato sugli intervalli tra una fumata e la successiva negli ultimi giorni.
      <br>
      La <em>media</em> considera tutti gli intervalli (in minuti), mentre la <em>mediana</em>
      riduce l’effetto di valori estremi. Il numero di intervalli analizzati è indicato come
      <strong>campione</strong>.
    </p>

    <template v-if="(data?.sample || 0) > 0">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <div class="text-xs text-gray-500">Media</div>
          <div class="text-2xl font-bold">
            {{ Number(data.mean_minutes || 0).toFixed(1) }} min
            <span class="text-sm text-gray-500">
              ({{ formatHours(data.mean_minutes) }})
            </span>
          </div>
        </div>
        <div>
          <div class="text-xs text-gray-500">Mediana</div>
          <div class="text-2xl font-bold">
            {{ Number(data.median_minutes || 0).toFixed(1) }} min
            <span class="text-sm text-gray-500">
              ({{ formatHours(data.median_minutes) }})
            </span>
          </div>
        </div>
      </div>

      <!-- Sparkline opzionale -->
      <ClientOnly v-if="(data?.intervals?.length || 0) > 0">
        <div ref="el" class="w-full h-24 mt-4"></div>
      </ClientOnly>

      <div class="mt-2 text-xs text-gray-500">
        Campione analizzato: {{ data.sample }} intervalli consecutivi
      </div>
    </template>

    <template v-else>
      <div class="text-sm text-gray-500">
        Nessun dato sufficiente per calcolare l’intervallo.
      </div>
    </template>
  </div>
</template>

<script setup>
const props = defineProps({
  data: { type: Object, default: () => ({}) }
})

const el = ref(null)
let chart = null
let ApexCharts = null

// Utility per formattare minuti → ore:minuti
const formatHours = (mins) => {
  if (!mins || mins <= 0) return "0h"
  const h = Math.floor(mins / 60)
  const m = Math.round(mins % 60)
  if (h === 0) return `${m}m`
  if (m === 0) return `${h}h`
  return `${h}h ${m}m`
}

const buildOptions = () => ({
  chart: { type: 'line', sparkline: { enabled: true } },
  series: [{
    name: 'Intervallo',
    data: (props.data?.intervals || []).map(n => Number(n || 0))
  }],
  stroke: { width: 2, curve: 'smooth' },
  tooltip: { enabled: false }
})

const mountChart = async () => {
  if (!process.client) return
  const hasData = (props.data?.intervals?.length || 0) > 0
  if (!hasData || !el.value) return

  if (!ApexCharts) {
    ApexCharts = (await import('apexcharts')).default
  }
  if (chart) {
    await chart.updateOptions(buildOptions(), false, true)
  } else {
    chart = new ApexCharts(el.value, buildOptions())
    await chart.render()
  }
}

const destroyChart = () => {
  if (chart) {
    chart.destroy()
    chart = null
  }
}

onMounted(mountChart)

watch(
  () => props.data,
  async () => {
    const hasData = (props.data?.intervals?.length || 0) > 0
    if (!hasData) {
      destroyChart()
      return
    }
    await mountChart()
  },
  { deep: true }
)

onBeforeUnmount(destroyChart)
</script>
