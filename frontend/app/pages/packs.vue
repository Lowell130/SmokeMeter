<!-- pages/packs.vue -->
<template>
  <section class="space-y-4">
    <h1 class="text-xl font-semibold">Pacchetti</h1>

    <div class="flex items-center gap-2">
      <label class="text-sm">Per pagina</label>
      <select
        v-model.number="limit"
        @change="goPage(1)"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
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

    <PacksTable
      :packs="items"
      @deleted="reload"
      @updated="reload"
    />

    <!-- Pagination -->
    <nav aria-label="Page navigation" class="flex justify-center">
    <ul class="inline-flex -space-x-px text-sm">
        <!-- Prev -->
        <li>
          <a
            href="#"
            @click.prevent="goPrev"
            :class="[
              'flex items-center justify-center px-4 h-10 ms-0 leading-tight bg-white border border-e-0 rounded-s-lg',
              page <= 1
                ? 'text-gray-300 border-gray-200 cursor-not-allowed'
                : 'text-gray-500 border-gray-300 hover:bg-gray-100 hover:text-gray-700',
              'dark:bg-gray-800 dark:border-gray-700',
              page <= 1 ? 'dark:text-gray-600' : 'dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'
            ]"
          >Previous</a>
        </li>

        <!-- Page numbers -->
        <li v-for="p in pagesToShow" :key="p">
          <a
            href="#"
            @click.prevent="goPage(p)"
            :aria-current="p === page ? 'page' : null"
            :class="[
              'flex items-center justify-center px-4 h-10 border',
              p === page
                ? 'text-blue-600 bg-blue-50 hover:bg-blue-100 hover:text-blue-700 border-gray-300 dark:bg-gray-700 dark:text-white'
                : 'leading-tight text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'
            ]"
          >{{ p }}</a>
        </li>

        <!-- Next -->
        <li>
          <a
            href="#"
            @click.prevent="goNext"
            :class="[
              'flex items-center justify-center px-4 h-10 leading-tight bg-white border rounded-e-lg',
              page >= totalPages
                ? 'text-gray-300 border-gray-200 cursor-not-allowed'
                : 'text-gray-500 border-gray-300 hover:bg-gray-100 hover:text-gray-700',
              'dark:bg-gray-800 dark:border-gray-700',
              page >= totalPages ? 'dark:text-gray-600' : 'dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'
            ]"
          >Next</a>
        </li>
      </ul>
    </nav>
  </section>
</template>

<script setup>
import PacksTable from '~/components/PacksTable.vue'

const { get } = useApi()

const items = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(20)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit.value)))
const skip = computed(() => (page.value - 1) * limit.value)

/**
 * Mostra una finestra di max 5 pagine intorno alla pagina corrente.
 * Esempi:
 * - Se totalPages <= 5 → [1..totalPages]
 * - Al centro quando possibile, ai bordi quando vicino a 1 o totalPages.
 */
const pagesToShow = computed(() => {
  const tp = totalPages.value
  if (tp <= 5) return Array.from({ length: tp }, (_, i) => i + 1)

  let start = Math.max(1, page.value - 2)
  let end = Math.min(tp, start + 4)
  // aggiusta se non arriviamo a 5 elementi
  if (end - start + 1 < 5) start = Math.max(1, end - 4)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

const load = async () => {
  const res = await get(`/packs?skip=${skip.value}&limit=${limit.value}`)
  // lato backend /packs ora deve supportare paginazione e tornare { items, total }
  // se non l'hai ancora fatto, mantieni un endpoint separato per la pagina liste.
  items.value = res.items || []
  total.value = res.total || 0
}

const goPage = (p) => {
  const tp = totalPages.value
  page.value = Math.min(Math.max(1, p), tp)
  load()
}
const goPrev = () => goPage(page.value - 1)
const goNext = () => goPage(page.value + 1)

const reload = () => {
  // dopo update/delete può cambiare il totale → ricalcolo
  load().then(() => {
    if (page.value > totalPages.value) goPage(totalPages.value)
  })
}

onMounted(load)
</script>
