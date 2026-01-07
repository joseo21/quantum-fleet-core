<template>
  <div class="h-full flex flex-col bg-gray-50">

    <!-- BARRA SUPERIOR -->
    <div class="shrink-0 border-b bg-white flex items-center justify-between px-4 h-12">

      <AlertsFilters v-model:device="deviceFilter" v-model:variable="variableFilter" v-model:assignee="assigneeFilter"
        :devices="devices" />


      <!-- BOTÓN CREAR ALERTA -->
      <button class="ml-4 h-8 px-3 rounded-lg text-sm font-medium
               bg-[#102372] text-white hover:bg-[#0c1c5a]
               transition" @click="showCreateModal = true">
        + Crear alerta
      </button>
    </div>

    <!-- LISTADO -->
    <div class="flex-1 overflow-y-auto">
      <div class="px-4 py-2 space-y-2">

        <AlertCard v-for="alert in filteredAlerts" :key="alert.id" :alert="alert" @view-history="openHistory" />

        <AlertsEmpty v-if="filteredAlerts.length === 0" />
      </div>
    </div>

    <!-- MODAL CREAR ALERTA -->
    <CreateAlertModal v-if="showCreateModal" @close="showCreateModal = false" @save="createAlertRule" />

    <!-- MODAL HISTORIAL -->
    <AlertHistoryModal v-if="selectedAlert" :alert="selectedAlert" @close="selectedAlert = null" />

  </div>
</template>

<script setup>
import { ref, computed } from "vue"

import AlertsFilters from "@/components/alerts/AlertsFilters.vue"
import AlertCard from "@/components/alerts/AlertCard.vue"
import AlertsEmpty from "@/components/alerts/AlertsEmpty.vue"
import CreateAlertModal from "@/components/alerts/CreateAlertModal.vue"
import AlertHistoryModal from "@/components/alerts/AlertHistoryModal.vue"

/* =========================
 * DISPOSITIVOS (mock)
 * ========================= */
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

/* =========================
 * FILTROS
 * ========================= */
const deviceFilter = ref("")     // 🔴 NUEVO
const variableFilter = ref("")
const assigneeFilter = ref(null)

/* =========================
 * MODALES
 * ========================= */
const showCreateModal = ref(false)
const selectedAlert = ref(null)

/* =========================
 * ALERTAS
 * ========================= */
const alerts = ref([])

/* =========================
 * FILTRADO CORRECTO
 * ========================= */
const filteredAlerts = computed(() => {
  return alerts.value.filter(a => {

    /* 🔹 FILTRO POR DISPOSITIVO */
    if (deviceFilter.value && a.device_id !== deviceFilter.value) {
      return false
    }

    /* 🔹 FILTRO POR VARIABLE
       - solo aplica si la alerta tiene variable */
    if (variableFilter.value) {
      if (!a.variable || a.variable !== variableFilter.value) {
        return false
      }
    }

    /* 🔹 FILTRO POR RESPONSABLE */
    if (assigneeFilter.value && a.assignee !== assigneeFilter.value) {
      return false
    }

    return true
  })
})

/* =========================
 * ABRIR HISTORIAL
 * ========================= */
const openHistory = (alert) => {
  selectedAlert.value = alert
}

/* =========================
 * CREAR ALERTA
 * ========================= */
const createAlertRule = (rule) => {
  const now = new Date()
  const device = devices.find(d => d.id === rule.device_id)

  const newAlert = {
    id: crypto.randomUUID(),

    device_id: device.id,
    device_name: device.name,

    variable: rule.variable ?? null,
    assignee: rule.assignee ?? null,
    created_at: now.toISOString(),

    condition: rule.condition,
    history: []
  }

  /* ===========================
   * FUERA DE RANGO (GLOBAL)
   * =========================== */
  if (newAlert.condition.type === "max") {
    const { limit_value, limit_type } = rule.condition

    const values =
      limit_type === "min"
        ? [limit_value - 5, limit_value - 2]
        : [limit_value + 12, limit_value + 5]

    newAlert.history.push(
      {
        triggered_at: new Date(now.getTime() - 1000 * 60 * 90).toISOString(),
        variable: device.variables[0],
        value: values[0],
        limit: limit_value,
        limit_type
      },
      {
        triggered_at: new Date(now.getTime() - 1000 * 60 * 30).toISOString(),
        variable: device.variables[1] ?? device.variables[0],
        value: values[1],
        limit: limit_value,
        limit_type
      }
    )
  }

  /* ===========================
   * TIMEOUT
   * =========================== */
  if (newAlert.condition.type === "timeout") {
    newAlert.history.push(
      {
        triggered_at: new Date(now.getTime() - 1000 * 60 * 60).toISOString(),
        minutes_without_data: rule.condition.timeout_minutes,
        recovered_at: new Date(now.getTime() - 1000 * 60 * 40).toISOString()
      },
      {
        triggered_at: new Date(now.getTime() - 1000 * 60 * 15).toISOString(),
        minutes_without_data: rule.condition.timeout_minutes,
        recovered_at: null
      }
    )
  }

  /* ===========================
   * CONSUMO ACUMULADO
   * =========================== */
  if (newAlert.condition.type === "volume_accumulated") {
    newAlert.history.push(
      {
        triggered_at: new Date(now.getTime() - 1000 * 60 * 120).toISOString(),
        accumulated_liters: rule.condition.limit_liters + 180,
        limit_liters: rule.condition.limit_liters,
        period: rule.condition.period
      },
      {
        triggered_at: new Date(now.getTime() - 1000 * 60 * 30).toISOString(),
        accumulated_liters: rule.condition.limit_liters + 40,
        limit_liters: rule.condition.limit_liters,
        period: rule.condition.period
      }
    )
  }

  alerts.value.unshift(newAlert)
  showCreateModal.value = false
}
</script>
