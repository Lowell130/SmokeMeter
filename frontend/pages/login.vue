<script setup>
const api = useApi()
const auth = useAuth()
const email = ref('')
const password = ref('')

async function submit () {
  const res = await api.post('/auth/login', { email: email.value, password: password.value })
  auth.setTokens(res.access_token, res.refresh_token)
  await navigateTo('/dashboard')
}

</script>
<template>
  <div class="p-8 max-w-md mx-auto">
    <h2 class="text-2xl font-semibold mb-4">Accedi</h2>
    <form @submit.prevent="submit" class="flex flex-col gap-3">
      <input
        v-model="email"
        type="email"
        placeholder="Email"
        class="border p-2 rounded"
      />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        class="border p-2 rounded"
      />
      <button type="submit" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Entra</button>
    </form>
  </div>
</template>