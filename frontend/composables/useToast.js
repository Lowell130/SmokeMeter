export function useToast () {
  const toasts = useState('toasts', () => [])

  function toast ({ message, type = 'info', duration = 3000 } = {}) {
    const id = Math.random().toString(36).slice(2)
    toasts.value.push({ id, message, type })
    if (duration) {
      setTimeout(() => remove(id), duration)
    }
  }

  function remove (id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return { toasts, toast, remove }
}
