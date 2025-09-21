<template>
  <div class="space-y-4 max-w-lg">
    <h2 class="text-xl font-semibold">Profilo</h2>
    <div class="p-4 bg-white rounded-2xl shadow">
      <div class="text-sm text-gray-500">Email</div>
      <div class="font-mono">{{ user?.email }}</div>
    </div>
  </div>
</template>
<script setup>
const { user, fetchMe } = useAuth()
if (!user.value) await fetchMe()
</script>
