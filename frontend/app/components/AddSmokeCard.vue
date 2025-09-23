<template>
  <div class="p-4 bg-white rounded-2xl shadow space-y-3">
    <h3 class="font-semibold">Segna sigaretta</h3>

    <div v-if="!packs?.length" class="text-sm text-gray-500">
      Nessun pacchetto disponibile. Puoi comunque registrare una sigaretta <strong>senza pacchetto</strong>.
    </div>

    <!-- toggle senza pacchetto -->
    <label class="inline-flex items-center cursor-pointer gap-3">
      <input type="checkbox" class="sr-only peer" v-model="loose">
      <div class="relative w-11 h-6 bg-gray-200 rounded-full peer peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:bg-blue-600
                  dark:bg-gray-700 dark:peer-focus:ring-blue-800
                  after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border
                  after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full">
      </div>
      <span class="text-sm text-gray-900">Senza pacchetto (offerta)</span>
    </label>

    <template v-if="!loose && packs?.length">
      <!-- scelta pacchetto + duplica -->
      <div class="flex gap-2 items-center">
        <select v-model="packId" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
          <option value="">-- seleziona pacchetto --</option>
          <option v-for="p in packsSorted" :key="p._id" :value="p._id">
            {{ p.brand }} ({{ p.size }}) — {{ formatDate(p.created_at) }} — {{ remainingFor(p._id) }} rimaste
          </option>
        </select>

        <!-- Pulsante duplica esistente (opzionale) -->
        <button
          class="text-gray-900 bg-white border border-gray-300 focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-100 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700"
          :disabled="!packId || dupLoading"
          @click="duplicateSelected"
          title="Duplica pacchetto selezionato"
          aria-label="Duplica pacchetto selezionato"
        >
          <span v-if="!dupLoading">Duplica</span>
          <span v-else>...</span>
        </button>
      </div>
    </template>

    <template v-else>
      <!-- input per smoke senza pacchetto -->
      <input
        v-model.trim="brandLoose"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        placeholder="Marca (opzionale)"
      />
    </template>

    <!-- scelta tipo -->
    <select v-model="type" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
      <option value="smoked">Fumata</option>
      <option value="wasted">Rott(a)/Buttata</option>
      <option value="gifted">Offerta a qualcuno</option>
    </select>

    <div class="text-xs text-gray-500" v-if="loadingConsumption && !loose">
      Calcolo rimanenti…
    </div>

    <div class="text-sm text-red-600" v-if="error">{{ error }}</div>

    <!-- bottone -->
    <button
      :disabled="!canSubmit || loading"
      @click="add"
      class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700"
    >
      <span v-if="!loading">Aggiungi</span>
      <span v-else>Aggiungo…</span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps(['packs'])
const emit = defineEmits(['added'])

const { post, get } = useApi()

const packId = ref('')
const type = ref('smoked')
const loose = ref(false)         // <-- NUOVO: senza pacchetto
const brandLoose = ref('')       // <-- opzionale per loose
const loading = ref(false)
const dupLoading = ref(false)
const error = ref('')

// mappa { packId: remaining }
const loadingConsumption = ref(false)
const consumptionMap = ref({})

const formatDate = (ts) => {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('it-IT', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const packsSorted = computed(() =>
  Array.isArray(props.packs)
    ? [...props.packs].sort((a, b) => (b.created_at || 0) - (a.created_at || 0))
    : []
)

const remainingFor = (id) => {
  const info = consumptionMap.value[id]
  return typeof info?.remaining === 'number' ? info.remaining : '?'
}

// carica rimanenti (solo utile quando non è "loose")
onMounted(async () => {
  try {
    loadingConsumption.value = true
    const list = await get('/packs/consumption')
    const map = {}
    list.forEach(item => {
      map[item._id] = {
        remaining: Number(item.remaining ?? 0),
        smokes_count: Number(item.smokes_count ?? 0),
        consumed_count: Number(item.consumed_count ?? item.smokes_count ?? 0),
      }
    })
    consumptionMap.value = map
  } catch (e) {
    console.warn('Impossibile caricare /packs/consumption', e?.status || e)
  } finally {
    loadingConsumption.value = false
  }
})

const canSubmit = computed(() => {
  const okType = ['smoked', 'wasted', 'gifted'].includes(type.value)
  if (loose.value) return okType  // senza pack: basta il tipo
  return okType && !!packId.value // con pack: serve packId
})

const add = async () => {
  if (!canSubmit.value || loading.value) return
  loading.value = true
  error.value = ''
  try {
    if (loose.value) {
      // smoke senza pacchetto
      const body = { type: type.value }
      if (brandLoose.value) body.brand = brandLoose.value
      await post('/smokes', body)
      brandLoose.value = ''
    } else {
      // smoke collegata a un pack
      await post('/smokes', { pack_id: packId.value, type: type.value })
      // refresh rimanenti
      try {
        const list = await get('/packs/consumption')
        const map = {}
        list.forEach(item => { map[item._id] = { remaining: Number(item.remaining ?? 0), smokes_count: Number(item.smokes_count ?? 0), consumed_count: Number(item.consumed_count ?? item.smokes_count ?? 0) } })
        consumptionMap.value = map
      } catch (_) {}
      packId.value = ''
    }

    // reset tipo
    type.value = 'smoked'
    emit('added')
  } catch (e) {
    error.value = e?.data?.detail || 'Errore durante l’inserimento'
  } finally {
    loading.value = false
  }
}

// Duplica pacchetto selezionato (come prima)
const duplicateSelected = async () => {
  if (!packId.value || dupLoading.value) return
  dupLoading.value = true
  error.value = ''
  try {
    const src = props.packs.find(p => p._id === packId.value)
    if (!src) throw new Error('Pacchetto non trovato')
    await post('/packs', { brand: src.brand, size: Number(src.size), price: Number(src.price) })
    emit('added')
  } catch (e) {
    error.value = e?.data?.detail || e?.message || 'Errore nella duplicazione'
  } finally {
    dupLoading.value = false
  }
}
</script>
