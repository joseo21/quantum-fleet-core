<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">

    <!-- CARD -->
    <div class="w-full max-w-xl md:max-w-4xl bg-white rounded-2xl shadow-xl flex flex-col max-h-[80vh] overflow-hidden">

      <!-- HEADER -->
      <div class="px-6 py-4 bg-[#102372] text-white flex justify-between items-center">
        <div>
          <h3 class="text-lg font-semibold">
            Historial de alertas
          </h3>
          <p class="text-xs text-white/80">
            {{ headerSubtitle }}
          </p>
        </div>

        <button
          class="text-white/70 hover:text-white text-xl transition"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>

      <!-- BODY -->
      <div class="flex-1 overflow-y-auto px-6 py-5 bg-gray-50 text-sm">

        <!-- SIN HISTORIAL -->
        <div
          v-if="!hasHistory"
          class="h-full flex items-center justify-center text-gray-500"
        >
          No existen registros para esta alerta
        </div>

        <!-- ===================== -->
        <!-- CONDICIÓN MAX (GLOBAL) -->
        <!-- ===================== -->
        <div
          v-else-if="conditionType === 'max'"
          class="bg-white rounded-xl border border-gray-200 overflow-hidden"
        >
          <table class="w-full">
            <thead class="bg-gray-100 text-gray-600 text-xs uppercase">
              <tr>
                <th class="px-4 py-3 text-left">Fecha</th>
                <th class="px-4 py-3 text-left">Variable</th>
                <th class="px-4 py-3 text-right">Valor</th>
                <th class="px-4 py-3 text-right">Límite</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="(row, i) in sortedHistory"
                :key="i"
                class="border-t hover:bg-[#102372]/5 transition"
              >
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">
                    {{ formatDate(row.triggered_at) }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ formatTime(row.triggered_at) }}
                  </div>
                </td>

                <!-- VARIABLE QUE DISPARÓ -->
                <td class="px-4 py-3 font-medium text-gray-700">
                  {{ variableName(row.variable) }}
                </td>

                <td class="px-4 py-3 text-right font-semibold text-[#102372]">
                  {{ row.value }}
                </td>

                <td class="px-4 py-3 text-right text-gray-600 font-medium">
                  {{ limitLabel(row) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ===================== -->
        <!-- CONDICIÓN TIMEOUT -->
        <!-- ===================== -->
        <div
          v-else-if="conditionType === 'timeout'"
          class="bg-white rounded-xl border border-gray-200 overflow-hidden"
        >
          <table class="w-full">
            <thead class="bg-gray-100 text-gray-600 text-xs uppercase">
              <tr>
                <th class="px-4 py-3 text-left">Detectado</th>
                <th class="px-4 py-3 text-right">Silencio</th>
                <th class="px-4 py-3 text-right">Estado</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="(row, i) in sortedHistory"
                :key="i"
                class="border-t hover:bg-[#102372]/5 transition"
              >
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">
                    {{ formatDate(row.triggered_at) }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ formatTime(row.triggered_at) }}
                  </div>
                </td>

                <td class="px-4 py-3 text-right font-medium">
                  {{ row.minutes_without_data }} min
                </td>

                <td class="px-4 py-3 text-right font-medium">
                  <span v-if="row.recovered_at" class="text-green-700">
                    Recuperado
                  </span>
                  <span v-else class="text-red-600">
                    Sin señal
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ===================== -->
        <!-- CONDICIÓN VOLUMEN -->
        <!-- ===================== -->
        <div
          v-else-if="conditionType === 'volume_accumulated'"
          class="bg-white rounded-xl border border-gray-200 overflow-hidden"
        >
          <table class="w-full">
            <thead class="bg-gray-100 text-gray-600 text-xs uppercase">
              <tr>
                <th class="px-4 py-3 text-left">Detectado</th>
                <th class="px-4 py-3 text-right">Consumo</th>
                <th class="px-4 py-3 text-right">Límite</th>
                <th class="px-4 py-3 text-right">Período</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="(row, i) in sortedHistory"
                :key="i"
                class="border-t hover:bg-[#102372]/5 transition"
              >
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">
                    {{ formatDate(row.triggered_at) }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ formatTime(row.triggered_at) }}
                  </div>
                </td>

                <td class="px-4 py-3 text-right font-semibold text-red-600">
                  {{ row.accumulated_liters }} L
                </td>

                <td class="px-4 py-3 text-right font-medium text-gray-700">
                  {{ row.limit_liters }} L
                </td>

                <td class="px-4 py-3 text-right text-gray-600">
                  {{ formatPeriod(row.period) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- FALLBACK -->
        <div
          v-else
          class="h-full flex items-center justify-center text-sm text-red-600"
        >
          La condición de la alerta no es válida
        </div>

      </div>

      <!-- FOOTER -->
      <div class="px-6 py-4 bg-gray-50 border-t flex justify-end">
        <button
          class="px-4 py-2 text-sm rounded-lg border hover:bg-gray-100 transition"
          @click="$emit('close')"
        >
          Cerrar
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  alert: { type: Object, required: true }
})

defineEmits(["close"])

/* =========================
 * ESTADO BASE
 * ========================= */
const hasHistory = computed(
  () => Array.isArray(props.alert.history) && props.alert.history.length > 0
)

const conditionType = computed(
  () => props.alert.condition?.type ?? null
)

const activationsCount = computed(
  () => props.alert.history?.length ?? 0
)

/* =========================
 * HEADER SUBTITLE
 * ========================= */
const headerSubtitle = computed(() => {
  const device = props.alert.device_name ?? "Dispositivo"
  const count = activationsCount.value

  if (conditionType.value === "max") {
    return `${device} · Alerta global · ${count} activación${count !== 1 ? "es" : ""}`
  }

  return `${device} · ${variableName(props.alert.variable)} · ${count} activación${count !== 1 ? "es" : ""}`
})

/* =========================
 * HISTORIAL ORDENADO
 * ========================= */
const sortedHistory = computed(() =>
  [...props.alert.history].sort(
    (a, b) => new Date(b.triggered_at) - new Date(a.triggered_at)
  )
)

/* =========================
 * HELPERS
 * ========================= */
const variableName = v => ({
  fuel_level: "Nivel de combustible",
  fuel_flow: "Flujo de combustible",
  temperature: "Temperatura"
}[v] ?? v)

const limitLabel = row => {
  if (row.limit_type === "min") return `Mínimo ${row.limit}`
  if (row.limit_type === "max") return `Máximo ${row.limit}`
  return row.limit
}

const formatDate = v =>
  new Date(v).toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric"
  })

const formatTime = v =>
  new Date(v).toLocaleTimeString("es-CL", {
    hour: "2-digit",
    minute: "2-digit"
  })

const formatPeriod = p => ({
  day: "Diario",
  week: "Semanal",
  month: "Mensual",
  semester: "Semestral",
  year: "Anual"
}[p] ?? p)
</script>
