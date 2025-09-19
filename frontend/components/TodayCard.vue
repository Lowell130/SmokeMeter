<script setup>
import { computed } from 'vue'

const props = defineProps({ count: { type: [Number, Object], default: 0 } })
const emit = defineEmits(['add'])

const count = computed(() => {
  const c = props.count
  return Number((c && typeof c === 'object' && 'value' in c) ? c.value : c) || 0
})
</script>

<template>
  <div class="border p-4 rounded-xl flex items-center justify-between">
    <div>
      <div class="text-sm text-gray-500">Oggi</div>
      <div class="text-3xl font-bold">{{ count }}</div>
    </div>
    <button class="px-4 py-2 rounded bg-gray-900 text-white hover:bg-gray-800" @click="emit('add')">+1</button>
  </div>
</template>
