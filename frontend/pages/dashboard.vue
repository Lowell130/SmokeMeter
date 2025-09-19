<script setup>
const logs = useLogs();
const auth = useAuth();
auth.load();
onMounted(() => logs.refresh());
</script>
<template>
  <div class="p-6 max-w-4xl mx-auto">
    <h2 class="text-2xl font-bold mb-4">La tua giornata</h2>
     <TodayCard :count="logs.today" @add="logs.addCig" />
    <div class="grid md:grid-cols-2 gap-6 mt-6">
   
<TrendChart :series="logs.series" title="Ultimi 7 giorni" />
<HourlyBar :hist="logs.hourly" title="Distribuzione oraria (30gg)" />

    </div>
  </div>
</template>