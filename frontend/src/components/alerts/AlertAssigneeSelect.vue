<template>
  <select
    class="border rounded-lg text-sm px-2 py-1"
    @change="$emit('select', $event.target.value)"
  >
    <option value="">Asignar</option>
    <option v-for="u in users" :key="u" :value="u">
      {{ u }}
    </option>
  </select>
</template>

<script setup>
defineProps({ current: String })

const users = [
  "Juan Pérez",
  "María López",
  "Supervisor Turno"
]
</script>
