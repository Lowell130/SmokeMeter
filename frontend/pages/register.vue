<!-- page/register.vue -->
<script setup>
const api = useApi()
const auth = useAuth()
const email = ref('')
const password = ref('')

async function submit () {
  const res = await api.post('/auth/register', { email: email.value, password: password.value })
  auth.setTokens(res.access_token, res.refresh_token)
  await navigateTo('/dashboard')
}

</script>
<template>
  <div class="p-8 max-w-md mx-auto">
    <h2 class="text-2xl font-semibold mb-4">Crea account</h2>
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
      <button type="submit" class="btn btn-dark">Registrati</button>
    </form>
  </div>
</template>