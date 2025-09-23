<template>
  <footer class="border-t py-8 text-center text-sm text-gray-500">
    © {{ year }} Smoke Tracker
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>
