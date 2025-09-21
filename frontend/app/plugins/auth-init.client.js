// plugins/auth-initAccordions.client.js
export default defineNuxtPlugin(() => {
  const token = useState('token')
  if (process.client && !token.value) {
    const t = localStorage.getItem('token')
    if (t) token.value = t
  }
})
