<template>
  <div class="flex items-center gap-3">

    <!-- DISPOSITIVO -->
    <select
      class="h-8 px-3 text-sm rounded-lg border
             bg-gray-50 text-gray-700
             focus:ring-2 focus:ring-[#102372]/40"
      :value="device"
      @change="$emit('update:device', $event.target.value)"
    >
      <option value="">Dispositivo: Todos</option>
      <option
        v-for="d in devices"
        :key="d.id"
        :value="d.id"
      >
        {{ d.name }}
      </option>
    </select>

    <!-- VARIABLE -->
    <select
      class="h-8 px-3 text-sm rounded-lg border
             bg-gray-50 text-gray-700
             disabled:bg-gray-100 disabled:text-gray-400
             focus:ring-2 focus:ring-[#102372]/40"
      :disabled="!device"
      :value="variable"
      @change="$emit('update:variable', $event.target.value)"
    >
      <option value="">
        {{ device ? "Variable: Todas" : "Selecciona dispositivo" }}
      </option>

      <option
        v-for="v in availableVariables"
        :key="v"
        :value="v"
      >
        {{ variableLabel(v) }}
      </option>
    </select>

    <!-- RESPONSABLE -->
    <input
      type="text"
      class="h-8 px-3 text-sm rounded-lg border
             bg-gray-50 text-gray-700 w-[220px]
             focus:ring-2 focus:ring-[#102372]/40"
      placeholder="Responsable"
      :value="assignee ?? ''"
      @input="$emit('update:assignee', $event.target.value || null)"
    />

  </div>
</template>

<script setup>
import { computed, watch } from "vue"

const props = defineProps({
  device: {
    type: String,
    default: ""
  },
  variable: {
    type: String,
    default: ""
  },
  assignee: {
    type: String,
    default: null
  },
  devices: {
    type: Array,
    required: true
  }
})

const emit = defineEmits([
  "update:device",
  "update:variable",
  "update:assignee"
])

/* =========================
 * VARIABLES SEGÚN DISPOSITIVO
 * ========================= */
const availableVariables = computed(() => {
  const device = props.devices.find(d => d.id === props.device)
  return device ? device.variables : []
})

/* =========================
 * LIMPIAR VARIABLE SI CAMBIA DISPOSITIVO
 * ========================= */
watch(
  () => props.device,
  () => {
    emit("update:variable", "")
  }
)

/* =========================
 * LABEL VARIABLE
 * ========================= */
const variableLabel = v => ({
  fuel_level: "Nivel de combustible",
  fuel_flow: "Flujo de combustible",
  temperature: "Temperatura"
}[v] ?? v)
</script>
