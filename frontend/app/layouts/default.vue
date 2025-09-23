<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <AppHeader />

    <main class="max-w-7xl mx-auto w-full p-4 flex-1">
      <slot />
    </main>

    <AppFooter />
  </div>
</template>

<script setup>
// Nuxt auto-importa i componenti da /components, ma l'import esplicito è ok se preferisci
// import AppHeader from '~/components/AppHeader.vue'
// import AppFooter from '~/components/AppFooter.vue'
</script>
