<template>
  <div class="p-4 bg-white rounded-2xl shadow space-y-3">
    <h3 class="font-semibold">Aggiungi pacchetto</h3>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
      <input
        v-model.trim="brand"
        @keyup.enter="tryAdd"
        placeholder="Marca"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      />
      <select v-model.number="size" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
        <option :value="20">20</option>
        <option :value="10">10</option>
      </select>
      <input
        v-model.number="price"
        @keyup.enter="tryAdd"
        type="number"
        min="0"
        step="0.01"
        placeholder="Prezzo"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      />
    </div>

    <div class="text-sm text-red-600" v-if="error">{{ error }}</div>

    <button
      :disabled="!isValid || loading"
      @click="tryAdd"
      class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700"
    >
      <span v-if="!loading">Salva</span>
      <span v-else>Salvataggio…</span>
    </button>
  </div>
</template>

<script setup>
const emit = defineEmits(['added'])
const { post } = useApi()

const brand = ref('')
const size = ref(20)
const price = ref()
const loading = ref(false)
const error = ref('')

const isValid = computed(() => {
  const okBrand = brand.value && brand.value.length >= 2
  const okSize = [10, 20].includes(Number(size.value))
  const okPrice = price.value !== undefined && !Number.isNaN(Number(price.value)) && Number(price.value) >= 0
  return okBrand && okSize && okPrice
})

const reset = () => {
  brand.value = ''
  size.value = 20
  price.value = undefined
  error.value = ''
}

const tryAdd = async () => {
  if (!isValid.value || loading.value) return
  loading.value = true
  error.value = ''
  try {
    const body = { brand: brand.value, size: Number(size.value), price: Number(price.value) || 0 }
    await post('/packs', body)
    reset()
    emit('added')
  } catch (e) {
    error.value = e?.data?.detail || 'Errore durante il salvataggio'
  } finally {
    loading.value = false
  }
}
</script>
