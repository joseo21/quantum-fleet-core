<template>
  <div
    class="w-full flex flex-col gap-2
           md:flex-row md:items-center md:gap-3"
  >

    <!-- DISPOSITIVO -->
    <select
      class="filter-input"
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
      class="filter-input"
      :disabled="!device"
      :value="variable"
      @change="$emit('update:variable', $event.target.value)"
    >
      <option value="">
        {{ device ? "Variable: Todas" : "Selecciona un dispositivo primero" }}
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
      class="filter-input"
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

<style scoped>
/* ===== INPUT BASE ===== */
.filter-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  font-size: 0.875rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #374151;
  transition: background .15s, box-shadow .15s, border-color .15s;
}

.filter-input:focus {
  outline: none;
  border-color: #102372;
  box-shadow: 0 0 0 2px rgba(16, 35, 114, 0.35);
}

/* ✅ ESTADO DESHABILITADO (CLAVE) */
.filter-input:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  border-color: #e5e7eb;
  cursor: not-allowed;
}

/* ===== DESKTOP ===== */
@media (min-width: 768px) {
  .filter-input {
    width: auto;
    min-width: 180px;
  }
}
</style>
