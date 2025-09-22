<template>
  <div class="p-4 bg-white rounded-2xl shadow">
    <h3 class="font-semibold mb-3">Pacchetti inseriti</h3>

    <div class="overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead class="text-left text-gray-600">
          <tr>
            <th class="py-2 pr-4">Data</th>
            <th class="py-2 pr-4">Marca</th>
            <th class="py-2 pr-4">Formato</th>
            <th class="py-2 pr-4">Prezzo</th>
            <th class="py-2 pr-2 text-right">Azioni</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="p in packs" :key="p._id" class="border-t">
            <td class="py-2 pr-4 font-mono">{{ formatDate(p.created_at) }}</td>
            <td class="py-2 pr-4">{{ p.brand }}</td>
            <td class="py-2 pr-4">{{ p.size }}</td>
            <td class="py-2 pr-4">€ {{ Number(p.price).toFixed(2) }}</td>

            <td class="py-2 pr-2">
              <div class="flex items-center justify-end gap-2">
                <!-- EDIT -->
                <button
                  class="p-1.5 rounded hover:bg-gray-100"
                  @click="emit('edit', p)"
                  title="Modifica"
                  aria-label="Modifica"
                >
                  <!-- pencil -->
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M15.232 5.232a2.5 2.5 0 013.536 3.536L8.5 19H5v-3.5l10.232-10.268z" />
                  </svg>
                </button>

                <!-- DELETE -->
                <button
                  class="p-1.5 rounded hover:bg-red-50 text-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="deletingId === p._id"
                  @click="onDelete(p)"
                  title="Elimina"
                  aria-label="Elimina"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7h6m-7 0V6a2 2 0 012-2h2a2 2 0 012 2v1" />
                  </svg>
                </button>
              </div>

              <div v-if="errorById[p._id]" class="mt-1 text-xs text-red-600">
                {{ errorById[p._id] }}
              </div>
            </td>
          </tr>

          <tr v-if="!packs?.length">
            <td class="py-4 text-gray-500" colspan="5">Nessun pacchetto ancora inserito.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['edit', 'deleted'])
defineProps({ packs: { type: Array, default: () => [] } })

const { del } = useApi()
const deletingId = ref(null)
const errorById = ref({})

const formatDate = (ts) => {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('it-IT', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const onDelete = async (p) => {
  errorById.value = { ...errorById.value, [p._id]: '' }
  if (!confirm(`Eliminare il pacchetto ${p.brand} (${p.size}) da € ${Number(p.price).toFixed(2)}?`)) return

  deletingId.value = p._id
  try {
    await del(`/packs/${p._id}`)
    emit('deleted', p._id)     // la dashboard può fare refresh()
  } catch (e) {
    errorById.value = {
      ...errorById.value,
      [p._id]: e?.data?.detail || 'Errore durante l’eliminazione'
    }
  } finally {
    deletingId.value = null
  }
}
</script>
