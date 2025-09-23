<!-- pages/packs.vue -->
<template>
  <section class="space-y-4">
    <h1 class="text-xl font-semibold">Pacchetti</h1>

    <div class="flex items-center gap-2">
      <label class="text-sm">Per pagina</label>
      <select v-model.number="limit" @change="goPage(1)" class="border rounded p-1 text-sm">
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

    <div class="flex items-center justify-between">
      <button class="px-3 py-1 rounded border" :disabled="page<=1" @click="goPrev">« Prec</button>
      <div class="text-sm text-gray-600">Pagina {{ page }} / {{ totalPages }}</div>
      <button class="px-3 py-1 rounded border" :disabled="page>=totalPages" @click="goNext">Succ »</button>
    </div>
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

const load = async () => {
  const res = await get(`/packs?skip=${skip.value}&limit=${limit.value}`)
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
  // dopo update/delete può cambiare il totale → ricalcolo
  load().then(() => {
    if (page.value > totalPages.value) goPage(totalPages.value)
  })
}

onMounted(load)
</script>
