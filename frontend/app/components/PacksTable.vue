<template>
  <div class="p-4 bg-white rounded-2xl shadow">
    <h3 class="font-semibold mb-3">Pacchetti inseriti</h3>

    <div class="relative overflow-x-auto">
      <table class="w-full text-sm text-left rtl:text-right text-gray-500">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3">Data</th>
            <th scope="col" class="px-6 py-3">Marca</th>
            <th scope="col" class="px-6 py-3">Formato</th>
            <th scope="col" class="px-6 py-3">Prezzo</th>
            <th scope="col" class="px-6 py-3 text-right">Azioni</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="p in localPacks"
            :key="p._id"
            class="bg-white border-b border-gray-200"
          >
            <!-- DATA -->
            <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap font-mono">
              {{ formatDate(p.created_at) }}
            </th>

            <!-- MARCA -->
            <td class="px-6 py-4">
              <template v-if="editingId === p._id">
                <input v-model.trim="draft.brand" class="border p-1 rounded w-full" />
              </template>
              <template v-else>
                {{ p.brand }}
              </template>
            </td>

            <!-- FORMATO -->
            <td class="px-6 py-4">
              <template v-if="editingId === p._id">
                <select v-model.number="draft.size" class="border p-1 rounded">
                  <option :value="20">20</option>
                  <option :value="10">10</option>
                </select>
              </template>
              <template v-else>
                {{ p.size }}
              </template>
            </td>

            <!-- PREZZO -->
            <td class="px-6 py-4">
              <template v-if="editingId === p._id">
                <input v-model.number="draft.price" type="number" step="0.01" min="0" class="border p-1 rounded w-28" />
              </template>
              <template v-else>
                € {{ Number(p.price).toFixed(2) }}
              </template>
            </td>

            <!-- AZIONI -->
            <td class="px-6 py-4">
              <div class="flex items-center justify-end gap-2">
                <!-- EDIT MODE -->
                <template v-if="editingId === p._id">
                  <button
                    class="px-2 py-1 rounded bg-gray-900 text-white text-xs disabled:opacity-50"
                    :disabled="saving"
                    @click="saveEdit(p)"
                    title="Salva"
                  >
                    Salva
                  </button>
                  <button
                    class="px-2 py-1 rounded border text-xs"
                    :disabled="saving"
                    @click="cancelEdit"
                    title="Annulla"
                  >
                    Annulla
                  </button>
                </template>

                <!-- VIEW MODE -->
                <template v-else>
                  <button
                    class="p-1.5 rounded hover:bg-gray-100"
                    @click="startEdit(p)"
                    title="Modifica"
                    aria-label="Modifica"
                  >
                    <!-- pencil -->
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M15.232 5.232a2.5 2.5 0 013.536 3.536L8.5 19H5v-3.5l10.232-10.268z" />
                    </svg>
                  </button>

                  <button
                    class="p-1.5 rounded hover:bg-red-50 text-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="deletingId === p._id"
                    @click="onDelete(p)"
                    title="Elimina"
                    aria-label="Elimina"
                  >
                    <!-- trash -->
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7h6m-7 0V6a2 2 0 012-2h2a2 2 0 012 2v1" />
                    </svg>
                  </button>
                </template>
              </div>

              <div v-if="errorById[p._id]" class="mt-1 text-xs text-red-600">
                {{ errorById[p._id] }}
              </div>
            </td>
          </tr>

          <tr v-if="!localPacks?.length" class="bg-white">
            <td class="px-6 py-4 text-gray-500" colspan="5">Nessun pacchetto ancora inserito.</td>
          </tr>
        </tbody>
      </table>

      
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['updated', 'deleted'])
const props = defineProps({ packs: { type: Array, default: () => [] } })

const { del, patch } = useApi()

// copia locale per feedback immediato
const localPacks = ref([])
watch(() => props.packs, (v) => { localPacks.value = Array.isArray(v) ? v.map(x => ({ ...x })) : [] }, { immediate: true })

const deletingId = ref(null)
const errorById = ref({})

// stato edit
const editingId = ref(null)
const saving = ref(false)
const draft = reactive({ brand: '', size: 20, price: 0 })

const formatDate = (ts) => {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('it-IT', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const startEdit = (p) => {
  editingId.value = p._id
  draft.brand = p.brand
  draft.size = Number(p.size) || 20
  draft.price = Number(p.price) || 0
  errorById.value = { ...errorById.value, [p._id]: '' }
}

const cancelEdit = () => {
  editingId.value = null
  saving.value = false
}

const saveEdit = async (p) => {
  if (!editingId.value) return

  // validazioni minime
  if (!draft.brand || draft.brand.length < 2) {
    errorById.value = { ...errorById.value, [p._id]: 'Marca non valida' }
    return
  }
  if (![10, 20].includes(Number(draft.size))) {
    errorById.value = { ...errorById.value, [p._id]: 'Formato non valido (10 o 20)' }
    return
  }
  if (Number.isNaN(Number(draft.price)) || Number(draft.price) < 0) {
    errorById.value = { ...errorById.value, [p._id]: 'Prezzo non valido' }
    return
  }

  // invia solo campi modificati
  const payload = {}
  if (draft.brand !== p.brand) payload.brand = draft.brand
  if (Number(draft.size) !== Number(p.size)) payload.size = Number(draft.size)
  if (Number(draft.price) !== Number(p.price)) payload.price = Number(draft.price)

  if (Object.keys(payload).length === 0) { editingId.value = null; return }

  saving.value = true
  errorById.value = { ...errorById.value, [p._id]: '' }

  try {
    const updated = await patch(`/packs/${p._id}`, payload)
    const idx = localPacks.value.findIndex(x => x._id === p._id)
    if (idx !== -1) {
      localPacks.value[idx] = { ...localPacks.value[idx], ...payload, ...updated }
    }
    editingId.value = null
    emit('updated', p._id)
  } catch (e) {
    const msg = e?.data?.detail || e?.message || 'Errore durante il salvataggio'
    errorById.value = { ...errorById.value, [p._id]: `${msg}${e?.status ? ` (HTTP ${e.status})` : ''}` }
  } finally {
    saving.value = false
  }
}

const onDelete = async (p) => {
  errorById.value = { ...errorById.value, [p._id]: '' }
  if (!confirm(`Eliminare il pacchetto ${p.brand} (${p.size}) da € ${Number(p.price).toFixed(2)}?`)) return
  deletingId.value = p._id
  try {
    await del(`/packs/${p._id}`)
    emit('deleted', p._id)
    localPacks.value = localPacks.value.filter(x => x._id !== p._id)
  } catch (e) {
    errorById.value = { ...errorById.value, [p._id]: e?.data?.detail || 'Errore durante l’eliminazione' }
  } finally {
    deletingId.value = null
  }
}
</script>
