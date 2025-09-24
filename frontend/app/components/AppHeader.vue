<template>
  <nav class="bg-white border-b border-gray-200 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between p-4">
      <!-- Brand -->
      <NuxtLink to="/" class="flex items-center space-x-3 rtl:space-x-reverse" @click="closeOnMobile">
        <img src="~/assets/images/logo.png" class="h-10" alt="Logo" />
      </NuxtLink>

      <!-- Hamburger -->
      <button
        type="button"
        class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-600 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-300 dark:hover:bg-gray-800 dark:focus:ring-gray-700"
        :aria-expanded="open ? 'true' : 'false'"
        aria-controls="navbar-default"
        @click="open = !open"
      >
        <span class="sr-only">Apri menù</span>
        <svg class="w-5 h-5" aria-hidden="true" fill="none" viewBox="0 0 17 14">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M1 1h15M1 7h15M1 13h15" />
        </svg>
      </button>

      <!-- Menu -->
      <div
        :class="['w-full md:block md:w-auto', open ? 'block' : 'hidden']"
        id="navbar-default"
      >
        <ul
          class="font-medium flex flex-col p-4 md:p-0 mt-4 md:mt-0
                 border border-gray-100 rounded-lg bg-gray-50
                 md:flex-row md:space-x-6 md:border-0 md:bg-white
                 dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700
                 md:items-center"
        >
          <!-- Link protetti -->
          <li v-if="isAuthed">
            <NuxtLink to="/dashboard"
              class="block py-2 px-3 rounded-sm md:p-0 text-gray-900 md:hover:text-blue-700 dark:text-white md:dark:hover:text-blue-500"
              @click="closeOnMobile">
              Dashboard
            </NuxtLink>
          </li>
          <li v-if="isAuthed">
            <NuxtLink to="/packs"
              class="block py-2 px-3 rounded-sm md:p-0 text-gray-900 md:hover:text-blue-700 dark:text-white md:dark:hover:text-blue-500"
              @click="closeOnMobile">
              Pacchetti
            </NuxtLink>
          </li>
          <li v-if="isAuthed">
            <NuxtLink to="/smokes"
              class="block py-2 px-3 rounded-sm md:p-0 text-gray-900 md:hover:text-blue-700 dark:text-white md:dark:hover:text-blue-500"
              @click="closeOnMobile">
              Sigarette
            </NuxtLink>
          </li>
          <li v-if="isAuthed">
            <NuxtLink to="/profile"
              class="block py-2 px-3 rounded-sm md:p-0 text-gray-900 md:hover:text-blue-700 dark:text-white md:dark:hover:text-blue-500"
              @click="closeOnMobile">
              Profilo
            </NuxtLink>
          </li>

          <!-- Link pubblici -->
          <li v-if="!isAuthed">
            <NuxtLink to="/login"
              class="block py-2 px-3 rounded-sm md:p-0 text-gray-900 md:hover:text-blue-700 dark:text-white md:dark:hover:text-blue-500"
              @click="closeOnMobile">
              Login
            </NuxtLink>
          </li>
          <li v-if="!isAuthed">
            <NuxtLink to="/register"
              class="block py-2 px-3 rounded-sm md:p-0 text-gray-900 md:hover:text-blue-700 dark:text-white md:dark:hover:text-blue-500"
              @click="closeOnMobile">
              Registrati
            </NuxtLink>
          </li>

          <!-- Logout -->
          <li v-if="isAuthed" class="md:pl-2 flex items-center">
            <button
              @click="onLogout"
              class="w-full md:w-auto px-3 py-2 text-xs font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
              Logout
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
const open = ref(false)

const { user, token, logout, loadToken, fetchMe } = useAuth()
const isAuthed = computed(() => !!token.value)

onMounted(async () => {
  loadToken()
  if (token.value) {
    try { await fetchMe() } catch {}
  }
})

function closeOnMobile() {
  if (process.client && window.innerWidth < 768) open.value = false
}

function onLogout() {
  logout()
  open.value = false
  navigateTo('/login')
}
</script>
