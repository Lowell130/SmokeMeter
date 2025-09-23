<template>
  <div class="p-4 bg-white rounded-2xl shadow">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold">
        {{ looseOnly ? 'Sigarette senza pacchetto' : 'Tutte le sigarette' }}
      </h3>

      <label class="inline-flex items-center cursor-pointer text-sm">
        <input type="checkbox" class="sr-only peer" v-model="looseOnly" @change="load">
        <div class="relative w-10 h-5 bg-gray-200 rounded-full peer peer-checked:bg-blue-600 after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:h-4 after:w-4 after:rounded-full after:transition-all peer-checked:after:translate-x-5"></div>
        <span class="ms-2">Solo “loose”</span>
      </label>
    </div>

    <div class="relative overflow-x-auto">
      <table class="w-full text-sm text-left rtl:text-right text-gray-500">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3">Data/Ora</th>
            <th scope="col" class="px-6 py-3">Tipo</th>
            <th scope="col" class="px-6 py-3">Fonte</th>
            <th scope="col" class="px-6 py-3">Marca</th>
            <th scope="col" class="px-6 py-3 text-right">Azioni</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="s in items"
            :key="s._id"
            class="bg-white border-b border-gray-200"
          >
            <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap font-mono">
              {{ formatTs(s.ts) }}
            </th>
            <td class="px-6 py-4 capitalize">
              {{ s.type }}
            </td>
            <td class="px-6 py-4">
              <span
                class="px-2 py-0.5 rounded text-xs"
                :class="s.source === 'loose' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-700'">
                {{ s.source || (s.pack_id ? 'pack' : 'loose') }}
              </span>
            </td>
            <td class="px-6 py-4">
              {{ s.brand || '—' }}
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center justify-end">
                <button
                  class="p-1.5 rounded hover:bg-red-50 text-red-600 disabled:opacity-50"
                  :disabled="deletingId === s._id"
                  @click="onDelete(s)"
                  title="Elimina"
                  aria-label="Elimina">
                  <!-- trash -->
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7h6m-7 0V6a2 2 0 012-2h2a2 2 0 012 2v1" />
                  </svg>
                </button>
              </div>
              <div v-if="errorById[s._id]" class="mt-1 text-xs text-red-600">
                {{ errorById[s._id] }}
              </div>
            </td>
          </tr>

          <tr v-if="!items.length" class="bg-white">
            <td class="px-6 py-4 text-gray-500" colspan="5">Nessuna sigaretta trovata.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['deleted'])
const props = defineProps({
  limit: { type: Number, default: 20 },
  refreshKey: { type: Number, default: 0 }
})

const { get, del } = useApi()
const looseOnly = ref(true)
const items = ref([])
const deletingId = ref(null)
const errorById = ref({})

const formatTs = (ts) => new Date((ts || 0) * 1000).toLocaleString('it-IT', {
  year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit'
})

const load = async () => {
  const all = await get('/smokes')
  const filtered = looseOnly.value ? all.filter(s => !s.pack_id) : all
  items.value = filtered.slice(0, props.limit)
}

watch(() => props.refreshKey, () => { load() })
watch(looseOnly, () => { load() })

const onDelete = async (s) => {
  errorById.value = { ...errorById.value, [s._id]: '' }
  if (!confirm('Eliminare questa sigaretta?')) return
  deletingId.value = s._id
  try {
    await del(`/smokes/${s._id}`)
    items.value = items.value.filter(x => x._id !== s._id)
    emit('deleted', s._id)
  } catch (e) {
    errorById.value = { ...errorById.value, [s._id]: e?.data?.detail || 'Errore durante l’eliminazione' }
  } finally {
    deletingId.value = null
  }
}

onMounted(load)
</script>
