<script setup>
import { computed } from 'vue'
const { toasts, remove } = useToast()

function iconClasses (type) {
  if (type === 'success') return 'text-green-500 bg-green-100 dark:bg-green-800 dark:text-green-200'
  if (type === 'error')   return 'text-red-500 bg-red-100 dark:bg-red-800 dark:text-red-200'
  if (type === 'warn')    return 'text-yellow-500 bg-yellow-100 dark:bg-yellow-800 dark:text-yellow-200'
  return 'text-blue-500 bg-blue-100 dark:bg-blue-800 dark:text-blue-200' // info
}
</script>

<template>
  <div class="fixed right-4 bottom-4 z-50 space-y-2">
    <div
      v-for="t in toasts"
      :key="t.id"
      :id="`toast-${t.id}`"
      class="flex items-center w-full max-w-xs p-4 text-gray-500 bg-white rounded-lg shadow-sm dark:text-gray-400 dark:bg-gray-800"
      role="alert"
    >
      <div class="inline-flex items-center justify-center shrink-0 w-8 h-8 rounded-lg"
           :class="iconClasses(t.type)">
        <!-- icona generica -->
        <svg class="w-4 h-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none"
             viewBox="0 0 18 20">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15.147 15.085a7.159 7.159 0 0 1-6.189 3.307A6.713 6.713 0 0 1 3.1 15.444c-2.679-4.513.287-8.737.888-9.548A4.373 4.373 0 0 0 5 1.608c1.287.953 6.445 3.218 5.537 10.5 1.5-1.122 2.706-3.01 2.853-6.14 1.433 1.049 3.993 5.395 1.757 9.117Z"/>
        </svg>
        <span class="sr-only">Icon</span>
      </div>
      <div class="ms-3 text-sm font-normal">{{ t.message }}</div>
      <button
        type="button"
        class="ms-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex items-center justify-center h-8 w-8 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700"
        :data-dismiss-target="`#toast-${t.id}`"
        aria-label="Close"
        @click="remove(t.id)"
      >
        <span class="sr-only">Close</span>
        <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none"
             viewBox="0 0 14 14">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
        </svg>
      </button>
    </div>
  </div>
</template>
