<template>
  <div class="p-4 bg-white rounded-2xl shadow space-y-3">
    <h3 class="font-semibold">Aggiungi pacchetto</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
      <input v-model="brand" placeholder="Marca" class="border p-2 rounded" />
      <select v-model.number="size" class="border p-2 rounded">
        <option :value="20">20</option>
        <option :value="10">10</option>
      </select>
      <input v-model.number="price" type="number" step="0.01" placeholder="Prezzo" class="border p-2 rounded" />
    </div>
    <button @click="add" class="bg-gray-900 text-white px-3 py-2 rounded">Salva</button>
  </div>
</template>
<script setup>
const emit = defineEmits(['added'])
const brand = ref('')
const size = ref(20)
const price = ref()
const { post } = useApi()
const add = async () => {
  const body = { brand: brand.value, size: size.value, price: price.value || 0 }
  await post('/packs', body)
  brand.value = ''
  price.value = undefined
  emit('added')
}
</script>
