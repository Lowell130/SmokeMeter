<template>
  <section class="bg-gray-50 dark:bg-gray-900">
    <div class="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0">
     <NuxtLink to="/" class="flex items-center mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
         <img src="~/assets/images/logo.png" class="h-10" alt="Logo" />
        <!-- Smokio -->
      </NuxtLink>

      <div class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700">
        <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
          <h1 class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
            Crea un account
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
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
                       focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5
                       dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
                       dark:focus:ring-blue-500 dark:focus:border-blue-500"
                placeholder="nome@azienda.com"
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
                autocomplete="new-password"
                placeholder="••••••••"
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
                       focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5
                       dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
                       dark:focus:ring-blue-500 dark:focus:border-blue-500"
                required
                minlength="6"
              >
            </div>

            <div>
              <label for="confirm-password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Conferma password</label>
              <input
                v-model="confirmPassword"
                type="password"
                name="confirm-password"
                id="confirm-password"
                placeholder="••••••••"
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
                       focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5
                       dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
                       dark:focus:ring-blue-500 dark:focus:border-blue-500"
                required
                minlength="6"
              >
            </div>

            <div class="flex items-start">
              <div class="flex items-center h-5">
                <input
                  id="terms"
                  type="checkbox"
                  v-model="termsAccepted"
                  class="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-blue-300
                         dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-blue-600 dark:ring-offset-gray-800"
                  required
                >
              </div>
              <div class="ml-3 text-sm">
                <label for="terms" class="font-light text-gray-500 dark:text-gray-300">
                  Accetto i <a class="font-medium text-blue-600 hover:underline dark:text-blue-500" href="#">Termini e Condizioni</a>
                </label>
              </div>
            </div>

            <!-- error/success messages -->
            <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

            <button
              type="submit"
              :disabled="submitting || !canSubmit"
              class="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300
                     font-medium rounded-lg text-sm px-5 py-2.5 text-center
                     disabled:opacity-60 disabled:cursor-not-allowed
                     dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
            >
              <span v-if="!submitting">Crea account</span>
              <span v-else>Creazione in corso…</span>
            </button>

            <p class="text-sm font-light text-gray-500 dark:text-gray-400">
              Hai già un account?
              <NuxtLink to="/login" class="font-medium text-blue-600 hover:underline dark:text-blue-500">Accedi</NuxtLink>
            </p>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const termsAccepted = ref(false)
const submitting = ref(false)
const error = ref('')

const { register } = useAuth()

const canSubmit = computed(() =>
  !!email.value &&
  !!password.value &&
  password.value.length >= 6 &&
  confirmPassword.value === password.value &&
  termsAccepted.value
)

const onSubmit = async () => {
  error.value = ''
  if (!canSubmit.value) {
    error.value = 'Controlla i campi: password almeno 6 caratteri e conferma corretta.'
    return
  }
  try {
    submitting.value = true
    await register(email.value, password.value)
    navigateTo('/dashboard')
  } catch (e) {
    error.value = e?.data?.detail || e?.message || 'Registrazione non riuscita.'
  } finally {
    submitting.value = false
  }
}
</script>
