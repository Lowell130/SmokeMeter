// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
   runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
    },
  },
  app: { head: { title: "Smoke Tracker" } },
   css: ['~/assets/css/input.css'], // you'll have to create this file
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
})




