<template>
  <div class="p-4 bg-white rounded-2xl shadow space-y-3">
    <h3 class="font-semibold">Segna sigaretta</h3>

    <!-- scelta pacchetto -->
    <select v-model="packId" class="border p-2 rounded w-full">
      <option value="">-- seleziona pacchetto --</option>
      <option v-for="p in packs" :key="p._id" :value="p._id">
        {{ p.brand }} ({{ p.size }})
      </option>
    </select>

    <!-- scelta tipo -->
    <select v-model="type" class="border p-2 rounded w-full">
      <option value="smoked">Fumata</option>
      <option value="wasted">Rott(a)/Buttata</option>
      <option value="gifted">Offerta a qualcuno</option>
    </select>

    <!-- bottone -->
    <button
      @click="add"
      class="bg-gray-900 text-white px-3 py-2 rounded w-full"
    >
      Aggiungi
    </button>
  </div>
</template>

<script setup>
const props = defineProps(['packs'])
const emit = defineEmits(['added'])

const packId = ref('')
const type = ref('smoked') // default

const { post } = useApi()

const add = async () => {
  if (!packId.value) return
  await post('/smokes', { pack_id: packId.value, type: type.value })
  // reset selezione
  type.value = 'smoked'
  packId.value = ''
  emit('added')
}
</script>
