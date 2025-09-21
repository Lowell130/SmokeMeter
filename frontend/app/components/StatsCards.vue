<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-sm text-gray-500">Sigarette fumate</div>
      <div class="text-2xl font-bold">{{ stats.total_smokes }}</div>
    </div>
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-sm text-gray-500">Spesa totale</div>
      <div class="text-2xl font-bold">€ {{ Number(stats.total_spent || 0).toFixed(2) }}</div>
    </div>
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-sm text-gray-500">Pacchetti</div>
      <div class="text-2xl font-bold">{{ packs.length }}</div>
    </div>
  </div>
</template>
<script setup>
const props = defineProps(['stats', 'packs'])
</script>
