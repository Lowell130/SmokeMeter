<script setup>
definePageMeta({ middleware: 'auth-client' })

const logs = useLogs()
const auth = useAuth()
const { toast } = useToast()

auth.load()

const loading = ref(true)

onMounted(async () => {
  try {
    await logs.refresh()
  } catch (e) {
    toast({ message: 'Errore nel caricamento dati', type: 'error' })
  } finally {
    loading.value = false
  }
})

async function onAdd () {
  try {
    await logs.addCig()
    toast({ message: 'Sigaretta registrata', type: 'success' })
  } catch (e) {
    toast({ message: 'Errore nella registrazione', type: 'error' })
  }
}
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <h2 class="text-2xl font-bold mb-4">La tua giornata</h2>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="animate-pulse h-20 bg-gray-100 dark:bg-gray-800 rounded-xl"></div>
      <div class="grid md:grid-cols-2 gap-6">
        <div class="animate-pulse h-72 bg-gray-100 dark:bg-gray-800 rounded-xl"></div>
        <div class="animate-pulse h-72 bg-gray-100 dark:bg-gray-800 rounded-xl"></div>
      </div>
    </div>

    <!-- Contenuto -->
    <template v-else>
      <TodayCard :count="logs.today" @add="onAdd" />

      <div class="grid md:grid-cols-2 gap-6 mt-6">
        <TrendChart :series="logs.series" title="Ultimi 7 giorni" />
        <HourlyBar :hist="logs.hourly" title="Distribuzione oraria (30gg)" />
      </div>

      <!-- Empty state -->
      <div v-if="(!logs.series || logs.series.length === 0) && (!logs.hourly || logs.hourly.length === 0)"
           class="mt-6 text-sm text-gray-500">
        Ancora nessun dato. Premi “+1” per iniziare a registrare.
      </div>
    </template>
  </div>
</template>
