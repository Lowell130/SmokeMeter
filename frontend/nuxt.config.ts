import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
   runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000',
       
      tmdbApiKey: process.env.NUXT_PUBLIC_TMDB_API_KEY || ''
    }
    
  },
  devtools: { enabled: true },
  compatibilityDate: '2025-05-15',
  css: ['~/assets/css/input.css'], // you'll have to create this file
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
  
});