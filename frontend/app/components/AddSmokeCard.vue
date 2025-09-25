<template>
  <div class="p-4 bg-white rounded-2xl shadow space-y-3">
    <h3 class="font-semibold">Segna sigaretta</h3>

    <div v-if="!packs?.length" class="text-sm text-gray-500">
      Nessun pacchetto disponibile. Puoi comunque registrare una sigaretta <strong>senza pacchetto</strong>.
    </div>

    <!-- toggle senza pacchetto -->
    <label class="inline-flex items-center cursor-pointer gap-3">
      <input type="checkbox" class="sr-only peer" v-model="loose">
      <div
        class="relative w-11 h-6 bg-gray-200 rounded-full peer peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:bg-blue-600
               dark:bg-gray-700 dark:peer-focus:ring-blue-800
               after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border
               after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full">
      </div>
      <span class="text-sm text-gray-900">Senza pacchetto (offerta)</span>
    </label>

    <template v-if="!loose && packs?.length">
      <div class="flex gap-2 items-center">
        <select
          v-model="packId"
          :disabled="loadingConsumption"
          class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
                 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5
                 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
                 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        >
          <option value="">-- seleziona pacchetto --</option>
          <option
            v-for="p in packsSorted"
            :key="p._id"
            :value="p._id"
            :disabled="isPackFinished(p._id)"
            :class="isPackFinished(p._id) ? 'text-gray-400' : ''"
          >
            {{ optionLabel(p) }}
          </option>
        </select>

        <button
          class="text-gray-900 bg-white border border-gray-300 focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-100
                 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-gray-800 dark:text-white dark:border-gray-600
                 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700"
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
      <input
        v-model.trim="brandLoose"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
               focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5
               dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
               dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        placeholder="Marca (opzionale)"
      />
    </template>

    <select
      v-model="type"
      class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
             focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5
             dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
             dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
    >
      <option value="smoked">Fumata</option>
      <option value="wasted">Rott(a)/Buttata</option>
      <option value="gifted">Offerta a qualcuno</option>
    </select>

    <div class="text-xs text-gray-500" v-if="loadingConsumption && !loose">
      Calcolo rimanenti…
    </div>

    <div class="text-sm text-red-600" v-if="error">{{ error }}</div>

    <button
      :disabled="!canSubmit || loading"
      @click="add"
      class="w-full md:w-auto focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900"
    >
      <span v-if="!loading">Aggiungi</span>
      <span v-else>Aggiungo…</span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  packs: { type: Array, default: () => [] },
  // 👉 opzionale ma consigliato: quando la dashboard fa refreshTick++, qui rifacciamo /packs/consumption
  refreshKey: { type: Number, default: 0 },
})
const emit = defineEmits(['added'])
const { post, get } = useApi()

const packId = ref('')
const type = ref('smoked')
const loose = ref(false)
const brandLoose = ref('')
const loading = ref(false)
const dupLoading = ref(false)
const error = ref('')

const loadingConsumption = ref(false)
const consumptionMap = ref({}) // { [packId]: { remaining, smokes_count, ... } }

// mappa rapida packId -> pack (serve per fallback size)
const packById = computed(() => {
  const map = {}
  for (const p of props.packs || []) map[p._id] = p
  return map
})

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

// ✅ Fallback: se non abbiamo ancora i consumi di quel pack, usa il formato (size) come remaining provvisorio
const remainingOf = (id) => {
  const cm = consumptionMap.value?.[id]
  if (cm && typeof cm.remaining === 'number') return Number(cm.remaining)
  const p = packById.value[id]
  return p ? Number(p.size || 0) : 0
}

const isPackFinished = (id) => remainingOf(id) <= 0

const optionLabel = (p) => {
  const rem = remainingOf(p._id)
  const status = rem > 0 ? `${rem} rimaste` : 'FINITO'
  return `${p.brand} (${p.size}) — ${formatDate(p.created_at)} — ${status}`
}

const fetchConsumption = async () => {
  loadingConsumption.value = true
  try {
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
    // se il pack selezionato è finito dopo l’update, deseleziona
    if (packId.value && isPackFinished(packId.value)) packId.value = ''
  } catch (e) {
    console.warn('Impossibile caricare /packs/consumption', e?.status || e)
  } finally {
    loadingConsumption.value = false
  }
}

// primo load
onMounted(fetchConsumption)

// 🔁 quando la dashboard fa refreshTick++, rifacciamo i consumi (opzionale ma consigliato)
watch(() => props.refreshKey, () => { fetchConsumption() })

// 🔁 quando cambiano i packs (e magari arriva un pack nuovo), scegli il più recente non finito se non c’è selezione
watch(
  () => props.packs,
  (val) => {
    if (!Array.isArray(val) || val.length === 0) return
    if (!packId.value) {
      const firstUsable = [...val]
        .sort((a,b) => (b.created_at||0)-(a.created_at||0))
        .find(p => remainingOf(p._id) > 0)
      if (firstUsable) packId.value = firstUsable._id
    }
  },
  { immediate: true, deep: true }
)

const canSubmit = computed(() => {
  const okType = ['smoked', 'wasted', 'gifted'].includes(type.value)
  if (loose.value) return okType
  return okType && !!packId.value && remainingOf(packId.value) > 0
})

const add = async () => {
  if (!canSubmit.value || loading.value) return
  loading.value = true
  error.value = ''
  try {
    if (loose.value) {
      const body = { type: type.value }
      if (brandLoose.value) body.brand = brandLoose.value
      await post('/smokes', body)
      brandLoose.value = ''
    } else {
      if (isPackFinished(packId.value)) {
        error.value = 'Pacchetto finito: seleziona un altro pacchetto.'
        return
      }
      await post('/smokes', { pack_id: packId.value, type: type.value })
      // refresh rimanenti
      await fetchConsumption()
    }
    type.value = 'smoked'
    emit('added')
  } catch (e) {
    error.value = e?.data?.detail || 'Errore durante l’inserimento'
  } finally {
    loading.value = false
  }
}

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
