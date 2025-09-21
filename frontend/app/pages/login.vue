<template>
  <form class="max-w-md space-y-4" @submit.prevent="onSubmit">
    <h2 class="text-xl font-semibold">Login</h2>
    <input v-model="email" type="email" class="w-full border p-2 rounded" placeholder="Email" required>
    <input v-model="password" type="password" class="w-full border p-2 rounded" placeholder="Password" required>
    <button class="w-full bg-gray-900 text-white p-2 rounded">Entra</button>
  </form>
</template>

<script setup>
const email = ref('')
const password = ref('')
const { login } = useAuth()
const onSubmit = async () => {
  await login(email.value, password.value)
  navigateTo('/dashboard')
}
</script>
