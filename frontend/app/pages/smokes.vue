<!-- pages/smokes.vue -->
<template>
  <section class="space-y-4">
    <h1 class="text-xl font-semibold">Sigarette</h1>

    <div class="flex flex-wrap items-center gap-3">
      <label class="inline-flex items-center cursor-pointer text-sm">
        <input type="checkbox" class="sr-only peer" v-model="looseOnly" @change="goPage(1)">
        <div class="relative w-10 h-5 bg-gray-200 rounded-full peer peer-checked:bg-blue-600 after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:h-4 after:w-4 after:rounded-full after:transition-all peer-checked:after:translate-x-5"></div>
        <span class="ms-2">Solo “loose”</span>
      </label>

      <div class="flex items-center gap-2">
        <label class="text-sm">Per pagina</label>
        <select v-model.number="limit" @change="goPage(1)" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
               focus:ring-blue-500 focus:border-blue-500 block w-fit p-2.5 pr-8
               dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
               dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
        <span class="text-sm text-gray-500">Totale: {{ total }}</span>
      </div>
    </div>

    <!-- ⛔️ RIMOSSO <SmokesTable ... /> per evitare duplicazione -->
<div class="p-4 bg-white rounded-2xl shadow">
    <h3 class="font-semibold mb-3">Sigarette</h3>
    <div class="relative overflow-x-auto">
      <table class="w-full text-sm text-left text-gray-500">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
          <tr>
            <th class="px-6 py-3">Data/Ora</th>
            <th class="px-6 py-3">Tipo</th>
            <th class="px-6 py-3">Fonte</th>
            <th class="px-6 py-3">Marca</th>
            <th class="px-6 py-3 text-right">Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in items" :key="s._id" class="bg-white border-b border-gray-200">
            <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap font-mono">
              {{ formatTs(s.ts) }}
            </th>
            <td class="px-6 py-4 capitalize">{{ s.type }}</td>
            <td class="px-6 py-4">
              <span class="px-2 py-0.5 rounded text-xs"
                :class="s.source === 'loose' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-700'">
                {{ s.source || (s.pack_id ? 'pack' : 'loose') }}
              </span>
            </td>
            <td class="px-6 py-4">{{ s.brand || '—' }}</td>
            <td class="px-6 py-4">
              <div class="flex items-center justify-end">
                <button
                  class="p-1.5 rounded hover:bg-red-50 text-red-600"
                  @click="onDelete(s)"
                  title="Elimina"
                  aria-label="Elimina">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7h6m-7 0V6a2 2 0 012-2h2a2 2 0 012 2v1" />
                  </svg>
                </button>
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

   <nav aria-label="Page navigation example" class="flex justify-center">
  <ul class="inline-flex -space-x-px text-base h-10">
    <!-- Previous -->
    <li>
      <button
        class="flex items-center justify-center px-4 h-10 ms-0 leading-tight text-gray-500 bg-white border border-e-0 border-gray-300 rounded-s-lg hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="page <= 1"
        @click="goPrev"
      >
        Previous
      </button>
    </li>

    <!-- Pages -->
    <li v-for="p in pages" :key="'p-' + p">
      <!-- separatore -->
      <span
        v-if="p === '…'"
        class="flex items-center justify-center px-4 h-10 leading-tight text-gray-400 bg-white border border-gray-300 select-none"
      >…</span>

      <!-- numero -->
      <button
        v-else
        @click="goPage(p)"
        :aria-current="p === page ? 'page' : undefined"
        :class="[
          'flex items-center justify-center px-4 h-10 leading-tight border',
          p === page
            ? 'text-blue-600 border-gray-300 bg-blue-50 hover:bg-blue-100 hover:text-blue-700'
            : 'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-700'
        ]"
      >
        {{ p }}
      </button>
    </li>

    <!-- Next -->
    <li>
      <button
        class="flex items-center justify-center px-4 h-10 leading-tight text-gray-500 bg-white border border-gray-300 rounded-e-lg hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="page >= totalPages"
        @click="goNext"
      >
        Next
      </button>
    </li>
  </ul>
</nav>

  </section>
</template>


<script setup>
const { get, del } = useApi()

const items = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(20)
const looseOnly = ref(true)
const refreshTick = ref(0)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit.value)))
const skip = computed(() => (page.value - 1) * limit.value)

const formatTs = (ts) => new Date((ts || 0) * 1000).toLocaleString('it-IT', {
  year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit'
})

const load = async () => {
  const res = await get(`/smokes?skip=${skip.value}&limit=${limit.value}&loose_only=${looseOnly.value}`)
  items.value = res.items || []
  total.value = res.total || 0
}

const goPage = (p) => {
  page.value = Math.min(Math.max(1, p), totalPages.value)
  load()
}
const goPrev = () => goPage(page.value - 1)
const goNext = () => goPage(page.value + 1)

const reload = () => {
  load().then(() => {
    if (page.value > totalPages.value) goPage(totalPages.value)
    refreshTick.value++
  })
}

// finestra pagine (max 7 visibili con ellissi)
const pages = computed(() => {
  const total = totalPages.value
  const current = page.value
  const windowSize = 7
  if (total <= windowSize) return Array.from({ length: total }, (_, i) => i + 1)

  const pagesArr = []
  const add = (v) => pagesArr.push(v)

  const start = Math.max(2, current - 2)
  const end = Math.min(total - 1, current + 2)

  add(1)
  if (start > 2) add('…')
  for (let p = start; p <= end; p++) add(p)
  if (end < total - 1) add('…')
  add(total)

  return pagesArr
})


const onDelete = async (s) => {
  if (!confirm('Eliminare questa sigaretta?')) return
  try {
    await del(`/smokes/${s._id}`)
    reload()
  } catch (e) {
    console.error(e)
  }
}

watch(looseOnly, () => goPage(1))

onMounted(load)
</script>
