<!-- pages/login.vue -->
<template>
  <section class="bg-gray-50 dark:bg-gray-900">
    <div class="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0">
      <NuxtLink to="/" class="flex items-center mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
        <img :src="logo" class="h-10" alt="Smokio logo" />
        <!-- Smokio -->
      </NuxtLink>

      <div class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700">
        <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
          <h1 class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
            Accedi al tuo account
          </h1>

          <form class="space-y-4 md:space-y-6" @submit.prevent="onSubmit">
            <div>
              <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Email</label>
              <input
                v-model="email"
                type="email"
                name="email"
                id="email"
                autocomplete="email"
                class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5
                       dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                placeholder="name@company.com"
                required
              >
            </div>

            <div>
              <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Password</label>
              <input
                v-model="password"
                type="password"
                name="password"
                id="password"
                autocomplete="current-password"
                placeholder="••••••••"
                class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5
                       dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                required
              >
            </div>

            <div class="flex items-center justify-between">
              <label class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-300">
                <input
                  id="remember"
                  v-model="remember"
                  type="checkbox"
                  class="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-blue-300
                         dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-blue-600 dark:ring-offset-gray-800"
                >
                Ricordami
              </label>

              <NuxtLink to="/forgot" class="text-sm font-medium text-blue-600 hover:underline dark:text-blue-500">
                Password dimenticata?
              </NuxtLink>
            </div>

            <div v-if="errorMsg" class="text-sm text-red-600">
              {{ errorMsg }}
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300
                     font-medium rounded-lg text-sm px-5 py-2.5 text-center disabled:opacity-60 disabled:cursor-not-allowed
                     dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
            >
              <span v-if="!loading">Entra</span>
              <span v-else>Accesso…</span>
            </button>

            <p class="text-sm font-light text-gray-500 dark:text-gray-400">
              Non hai un account?
              <NuxtLink to="/register" class="font-medium text-blue-600 hover:underline dark:text-blue-500">
                Registrati
              </NuxtLink>
            </p>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import logo from '~/assets/images/logo.png'

const email = ref('')
const password = ref('')
const remember = ref(false) // se un giorno vuoi gestire un refresh token "persistente"
const loading = ref(false)
const errorMsg = ref('')

const { login } = useAuth()

const onSubmit = async () => {
  if (loading.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    await login(email.value, password.value, { remember: remember.value })
    navigateTo('/dashboard')
  } catch (e) {
    errorMsg.value = e?.data?.detail || e?.message || 'Credenziali non valide'
  } finally {
    loading.value = false
  }
}
</script>
