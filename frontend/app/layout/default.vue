<template>
  <div>
    <header class="border-b bg-white">
      <nav class="max-w-5xl mx-auto flex items-center justify-between p-4">
        <NuxtLink to="/" class="font-bold">Smoke Tracker</NuxtLink>
        <div class="flex gap-3 items-center">
          <NuxtLink to="/dashboard">Dashboard</NuxtLink>
          <NuxtLink to="/profile">Profilo</NuxtLink>
          <AuthButtons />
        </div>
      </nav>
    </header>
    <main class="max-w-5xl mx-auto p-4 min-h-screen bg-gray-50">
      <slot />
    </main>
    <footer class="border-t py-8 text-center text-sm text-gray-500">
      © {{ new Date().getFullYear() }} Smoke Tracker
    </footer>
  </div>
</template>

<script setup>
const AuthButtons = defineComponent({
  setup() {
    const { user, logout } = useAuth()
    return () =>
      user.value ? (
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">{{ user.value.email }}</span>
          <button class="px-3 py-1 rounded bg-gray-800 text-white" onClick={logout}>Logout</button>
        </div>
      ) : (
        <div class="flex gap-2">
          <NuxtLink class="px-3 py-1 rounded bg-gray-800 text-white" to="/login">Login</NuxtLink>
          <NuxtLink class="px-3 py-1 rounded border" to="/register">Registrati</NuxtLink>
        </div>
      )
  }
})
</script>
