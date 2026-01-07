<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">

    <div class="w-full max-w-xl bg-white rounded-2xl shadow-xl overflow-hidden">

      <!-- HEADER -->
      <div class="px-6 py-4 bg-gradient-to-r from-[#102372] to-[#1a3fa0] text-white">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-lg font-semibold">Nueva alerta</h2>
            <p class="text-xs text-white/80">Configuración de monitoreo automático</p>
          </div>

          <button class="text-white/70 hover:text-white text-xl" @click="$emit('close')">
            ✕
          </button>
        </div>
      </div>

      <!-- BODY -->
      <div class="px-6 py-5 space-y-6 text-sm text-gray-800 max-h-[70vh] overflow-y-auto">

        <!-- BLOQUE PRINCIPAL -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

          <!-- DISPOSITIVO -->
          <div class="md:col-span-2">
            <label class="block text-xs font-semibold uppercase tracking-wide text-gray-500 mb-1">
              Dispositivo
            </label>
            <select
              v-model="form.device_id"
              class="w-full h-9 px-3 rounded-lg border
                     focus:border-[#102372] focus:ring-2 focus:ring-[#102372]/30"
            >
              <option disabled value="">Selecciona un dispositivo</option>
              <option
                v-for="d in devices"
                :key="d.id"
                :value="d.id"
              >
                {{ d.name }}
              </option>
            </select>
          </div>

          <!-- VARIABLE -->
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wide text-gray-500 mb-1">
              Variable
            </label>
            <select
              v-model="form.variable"
              :disabled="!form.device_id || form.condition_type === 'max'"
              class="w-full h-9 px-3 rounded-lg border
                     disabled:bg-gray-100 disabled:text-gray-400
                     focus:border-[#102372] focus:ring-2 focus:ring-[#102372]/30"
            >
              <option disabled value="">Selecciona variable</option>
              <option
                v-for="v in availableVariables"
                :key="v"
                :value="v"
              >
                {{ variableLabel(v) }}
              </option>
            </select>
          </div>

          <!-- RESPONSABLE -->
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wide text-gray-500 mb-1">
              Responsable
            </label>
            <select
              v-model="form.assignee"
              class="w-full h-9 px-3 rounded-lg border
                     focus:border-[#102372] focus:ring-2 focus:ring-[#102372]/30"
            >
              <option value="">Sin asignar</option>
              <option v-for="u in users" :key="u.id" :value="u.name">
                {{ u.name }}
              </option>
            </select>
          </div>

        </div>

        <!-- CONDICIÓN -->
        <div class="rounded-xl border border-gray-200 p-4 space-y-4 bg-gray-50">

          <div>
            <h3 class="font-medium text-gray-800">
              ¿Cuándo quieres recibir la alerta?
            </h3>
            <p class="text-xs text-gray-500">
              Define la situación que activará la notificación
            </p>
          </div>

          <select
            v-model="form.condition_type"
            class="w-full h-9 px-3 rounded-lg border bg-white
                   focus:border-[#102372] focus:ring-2 focus:ring-[#102372]/30"
          >
            <option value="timeout">Sensor sin señal</option>
            <option value="max">Valor fuera de rango (global)</option>
            <option value="volume_accumulated">Consumo excesivo</option>
          </select>

          <!-- EXPLICACIÓN -->
          <p class="text-xs text-gray-600 leading-relaxed">
            <template v-if="form.condition_type === 'timeout'">
              Se notificará si la variable deja de enviar datos.
            </template>
            <template v-else-if="form.condition_type === 'max'">
              Se notificará si cualquier variable del dispositivo sale del rango definido.
            </template>
            <template v-else>
              Se notificará si el consumo acumulado supera el límite configurado.
            </template>
          </p>

          <!-- TIMEOUT -->
          <div v-if="form.condition_type === 'timeout'" class="flex gap-2">
            <input
              type="number"
              min="1"
              v-model.number="form.timeout_minutes"
              placeholder="Tiempo máximo sin datos"
              class="flex-1 h-9 px-3 rounded-lg border bg-white
                     focus:ring-2 focus:ring-[#102372]/30"
            />
            <span class="flex items-center px-3 rounded-lg bg-white border text-xs text-gray-500">
              min
            </span>
          </div>

          <!-- FUERA DE RANGO GLOBAL -->
          <div v-if="form.condition_type === 'max'" class="space-y-3">
            <select
              v-model="form.limit_type"
              class="w-full h-9 px-3 rounded-lg border bg-white
                     focus:ring-2 focus:ring-[#102372]/30"
            >
              <option value="max">Valor máximo</option>
              <option value="min">Valor mínimo</option>
            </select>

            <input
              type="number"
              v-model.number="form.limit_value"
              placeholder="Valor límite"
              class="w-full h-9 px-3 rounded-lg border bg-white
                     focus:ring-2 focus:ring-[#102372]/30"
            />
          </div>

          <!-- CONSUMO -->
          <div
            v-if="form.condition_type === 'volume_accumulated'"
            class="grid grid-cols-1 md:grid-cols-2 gap-3"
          >
            <input
              type="number"
              min="1"
              v-model.number="form.limit_liters"
              placeholder="Límite de consumo (litros)"
              class="h-9 px-3 rounded-lg border bg-white
                     focus:ring-2 focus:ring-[#102372]/30"
            />

            <select
              v-model="form.period"
              class="h-9 px-3 rounded-lg border bg-white
                     focus:ring-2 focus:ring-[#102372]/30"
            >
              <option value="day">Diario</option>
              <option value="week">Semanal</option>
              <option value="month">Mensual</option>
              <option value="semester">Semestral</option>
              <option value="year">Anual</option>
            </select>
          </div>

        </div>

      </div>

      <!-- FOOTER -->
      <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3">
        <button class="px-4 py-2 text-sm rounded-lg border hover:bg-gray-100" @click="$emit('close')">
          Cancelar
        </button>

        <button
          class="px-5 py-2 text-sm rounded-lg bg-[#102372] text-white
                 hover:bg-[#0d1d50] disabled:opacity-40"
          :disabled="!isValid"
          @click="save"
        >
          Crear alerta
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { reactive, computed, watch } from "vue"

const emit = defineEmits(["close", "save"])

/* 🔹 MOCK DISPOSITIVOS */
const devices = [
  {
    id: "DEV-01",
    name: "Camión 12",
    variables: ["fuel_level", "fuel_flow", "temperature"]
  },
  {
    id: "DEV-02",
    name: "Estanque Central",
    variables: ["fuel_level", "temperature"]
  },
  {
    id: "DEV-03",
    name: "Generador Planta",
    variables: ["temperature"]
  }
]

const users = [
  { id: 1, name: "Juan Pérez" },
  { id: 2, name: "María González" },
  { id: 3, name: "Carlos Soto" },
  { id: 4, name: "Soporte Turno Noche" }
]

/* =========================
 * FORM
 * ========================= */
const form = reactive({
  device_id: "",        // 🔴 importante: string, no null
  variable: "",
  condition_type: "timeout",

  timeout_minutes: 10,

  limit_type: "max",
  limit_value: null,

  limit_liters: null,
  period: "day",

  assignee: ""
})

/* =========================
 * VARIABLES DISPONIBLES
 * ========================= */
const availableVariables = computed(() => {
  const device = devices.find(d => d.id === form.device_id)
  return device ? device.variables : []
})

/* =========================
 * LIMPIEZAS AUTOMÁTICAS
 * ========================= */
watch(() => form.device_id, () => {
  form.variable = ""
})

watch(() => form.condition_type, type => {
  if (type === "max") {
    form.variable = ""
  }
})

/* =========================
 * VALIDACIÓN
 * ========================= */
const isValid = computed(() => {
  if (!form.device_id) return false

  if (form.condition_type !== "max" && !form.variable) return false

  if (form.condition_type === "timeout") {
    return !!form.timeout_minutes
  }

  if (form.condition_type === "max") {
    return form.limit_value !== null
  }

  if (form.condition_type === "volume_accumulated") {
    return form.limit_liters !== null && !!form.period
  }

  return false
})

/* =========================
 * HELPERS
 * ========================= */
const variableLabel = v => ({
  fuel_level: "Nivel de combustible",
  fuel_flow: "Flujo de combustible",
  temperature: "Temperatura"
}[v] ?? v)

/* =========================
 * GUARDAR
 * ========================= */
const save = () => {
  let condition

  if (form.condition_type === "timeout") {
    condition = {
      type: "timeout",
      timeout_minutes: form.timeout_minutes
    }
  }

  if (form.condition_type === "max") {
    condition = {
      type: "max",
      limit_type: form.limit_type,
      limit_value: form.limit_value
    }
  }

  if (form.condition_type === "volume_accumulated") {
    condition = {
      type: "volume_accumulated",
      limit_liters: form.limit_liters,
      period: form.period
    }
  }

  const device = devices.find(d => d.id === form.device_id)

  emit("save", {
    device_id: form.device_id,
    device_name: device?.name ?? "Dispositivo",
    variable: form.condition_type === "max" ? null : form.variable,
    assignee: form.assignee || null,
    condition
  })
}
</script>
