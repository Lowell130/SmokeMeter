<script setup>
const api = useApi();
const profile = ref(null);
const baseline = ref(null);
const price = ref(null);

onMounted(async () => {
  profile.value = await api.get("/users/me");
  baseline.value = profile.value.baseline_cigs_per_day;
  price.value = profile.value.price_per_pack;
});

async function save() {
  const res = await api.patch("/users/me", {
    baseline_cigs_per_day: baseline.value,
    price_per_pack: price.value,
  });
  profile.value = res;
}
</script>
<template>
  <div class="p-6 max-w-xl mx-auto">
    <h2 class="text-2xl font-bold mb-4">Profilo</h2>
    <div class="flex flex-col gap-3">
      <label>Sigarette/giorno baseline</label>
      <input v-model.number="baseline" type="number" class="border p-2" />
      <label>Prezzo pacchetto (€)</label>
      <input
        v-model.number="price"
        type="number"
        class="border p-2"
        step="0.01"
      />
      <button class="bg-black text-white p-2 mt-2" @click="save">Salva</button>
    </div>
  </div>
</template>