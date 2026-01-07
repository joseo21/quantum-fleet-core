<template>
  <div class="bg-white border border-gray-200 rounded-xl
           px-5 py-4 flex items-center gap-5
           hover:border-gray-300 hover:shadow-sm
           transition-all">

    <!-- ICONO -->
    <div class="w-11 h-11 rounded-xl flex items-center justify-center
             shrink-0" :class="iconBg">
      <SvgIcon name="bell" class="w-5 h-5" :class="iconColor" />

    </div>

    <!-- CONTENIDO -->
    <div class="flex-1 min-w-0 grid grid-cols-1 gap-1">

      <!-- FILA 1: TÍTULO + BADGE -->
      <div class="flex items-center gap-3">
        <h3 class="text-base font-semibold text-gray-900 truncate">
          {{ mainLabel }}
        </h3>

        <span class="text-xs font-medium px-2 py-0.5 rounded-full" :class="badgeClass">
          {{ conditionLabel }}
        </span>
      </div>

      <!-- FILA 2: RESPONSABLE -->
      <div class="text-sm text-gray-700">
        Responsable:
        <span class="font-medium">
          {{ alert.assignee || "Sin asignar" }}
        </span>
      </div>

      <!-- FILA 3: FECHA -->
      <div class="text-xs text-gray-500">
        Creada el {{ formattedDate }}
      </div>

    </div>

    <!-- ACCIÓN -->
    <div class="shrink-0">
      <button class="px-4 py-2 rounded-lg text-sm font-medium
               border border-gray-200
               bg-gray-50 hover:bg-gray-100
               transition" @click="$emit('view-history', alert)">
        Historial
      </button>
    </div>

  </div>
</template>

<script setup>
import { computed } from "vue"
import SvgIcon from '@/components/icons/SvgIcon.vue';

const props = defineProps({
  alert: { type: Object, required: true }
})

/* =========
 * ACTIVACIONES
 * ========= */
const activationCount = computed(() =>
  Array.isArray(props.alert.history)
    ? props.alert.history.length
    : 0
)

/* =========
 * LABEL PRINCIPAL
 * ========= */
const mainLabel = computed(() => {
  // 🔴 ALERTA GLOBAL (por dispositivo)
  if (props.alert.condition?.type === "max") {
    return props.alert.device_name ?? "Dispositivo"
  }

  // 🔹 ALERTA POR VARIABLE
  return variableName(props.alert.variable)
})

/* =========
 * TEXTO CONDICIÓN + ACTIVACIONES
 * ========= */
const conditionLabel = computed(() => {
  const type = props.alert.condition?.type
  const count = activationCount.value

  let base = "Alerta"

  if (type === "timeout") base = "Sensor sin señal"
  if (type === "max") base = "Fuera de rango"
  if (type === "volume_accumulated") base = "Consumo excesivo"

  if (count === 0) return base
  if (count === 1) return `${base} · 1 activación`
  return `${base} · ${count} activaciones`
})

/* =========
 * BADGE
 * ========= */
const badgeClass = computed(() => {
  return activationCount.value > 0
    ? "bg-green-100 text-green-700"
    : "bg-gray-100 text-gray-600"
})

/* =========
 * ICONO
 * ========= */
const iconBg = computed(() => {
  const type = props.alert.condition?.type

  if (type === "max") return "bg-purple-100"
  if (type === "timeout") return "bg-red-100"
  if (type === "volume_accumulated") return "bg-amber-100"

  return "bg-blue-100"
})

const iconColor = computed(() => {
  const type = props.alert.condition?.type

  if (type === "max") return "text-purple-600"
  if (type === "timeout") return "text-red-600"
  if (type === "volume_accumulated") return "text-amber-600"

  return "text-blue-600"
})

/* =========
 * FECHA
 * ========= */
const formattedDate = computed(() => {
  const d = new Date(props.alert.created_at)
  return d.toLocaleString("es-CL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  })
})

/* =========
 * HELPERS
 * ========= */
const variableName = v => ({
  fuel_level: "Nivel de combustible",
  fuel_flow: "Flujo de combustible",
  temperature: "Temperatura"
}[v] ?? v)
</script>
