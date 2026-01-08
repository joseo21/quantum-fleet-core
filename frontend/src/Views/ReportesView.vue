<template>
  <div class="w-full flex justify-center mt-2">

    <!-- CONTENEDOR PRINCIPAL (flotando, limpio, sin doble tarjeta) -->
    <div class="w-full max-w-[1500px] bg-white shadow-[0_8px_32px_rgba(0,0,0,0.12)] 
             rounded-2xl border border-gray-200 px-8 py-8 space-y-8">

      <!-- ==========================
           FILTROS SUPERIORES
      =========================== -->
      <div class="flex flex-col lg:flex-row gap-4 items-center">

        <DeviceFilter class="flex-1 w-full lg:flex-[3] lg:min-w-[420px]
         h-[46px] shadow-sm hover:shadow-md transition rounded-xl" :dispositivos="dispositivos"
          @update:selected="selectedDevices = $event" />


        <VariableFilter class="flex-1 min-w-[200px] h-[46px] shadow-sm hover:shadow-md transition rounded-xl"
          :variables="availableVariables" @update:selected="selectedVariables = $event" />

        <DateFilter class="flex-1 min-w-[200px] h-[46px] shadow-sm hover:shadow-md transition rounded-xl"
          @update:range="dateRange = $event" />

        <ReportActions class="flex-none h-[46px] shadow-sm hover:shadow-md transition rounded-xl"
          :devices="selectedDevices" :variables="selectedVariables" @export:pdf="exportPDF" @export:excel="exportExcel"
          @export:csv="exportCSV" />

      </div>



      <!-- ==========================
           TABLA DE RESULTADOS
      =========================== -->

      <div class="rounded-xl overflow-hidden shadow-[0_4px_20px_rgba(0,0,0,0.08)]">
        <ReportesTable :items="filteredDevices" :variables="selectedVariables" :dateRange="dateRange" />
      </div>

    </div>

  </div>
</template>


<script setup>
import { ref, computed } from "vue"

// COMPONENTES
import DeviceFilter from "@/components/ReportesUi/DeviceFilter.vue"
import VariableFilter from "@/components/ReportesUi/VariableFilter.vue"
import DateFilter from "@/components/ReportesUi/DateFilter.vue"
import ReportActions from "@/components/ReportesUi/ReportActions.vue"
import ReportesTable from "@/components/ReportesUi/ReportesTable.vue"



// ===========================================
// DATOS TEMPORALES
// ===========================================
const dispositivos = ref([
  {
    id: 1,
    nombre: "Dispositivo 01",
    datos: [
      { fecha: "2026-01-08 14:30", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 14:30", clave: "litros_total", valor: 350 },
      { fecha: "2026-01-08 14:30", clave: "nivel_estanque", valor: 180 },
      { fecha: "2026-01-08 14:30", clave: "temperatura", valor: 24.6 },
      { fecha: "2026-01-08 14:30", clave: "voltaje_bateria", valor: 12.4 },
      { fecha: "2026-01-08 14:30", clave: "horas_operacion", valor: 56 }
    ]
  },
  {
    id: 2,
    nombre: "Dispositivo 02",
    datos: [
      { fecha: "2026-01-08 14:20", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 14:20", clave: "litros_total", valor: 520 },
      { fecha: "2026-01-08 14:20", clave: "nivel_estanque", valor: null },
      { fecha: "2026-01-08 14:20", clave: "temperatura", valor: 22.4 },
      { fecha: "2026-01-08 14:20", clave: "voltaje_bateria", valor: 12.6 },
      { fecha: "2026-01-08 14:20", clave: "horas_operacion", valor: 128 },
      { fecha: "2026-01-08 14:20", clave: "pulsos_total", valor: 8750 },
      { fecha: "2026-01-08 14:20", clave: "caudal_lpm", valor: 45.2 }
    ]
  },
  {
    id: 3,
    nombre: "Dispositivo 03",
    datos: [
      { fecha: "2026-01-08 13:55", clave: "estado_dispositivo", valor: "offline" },
      { fecha: "2026-01-08 13:55", clave: "litros_total", valor: null },
      { fecha: "2026-01-08 13:55", clave: "nivel_estanque", valor: 300 },
      { fecha: "2026-01-08 13:55", clave: "temperatura", valor: 21.1 },
      { fecha: "2026-01-08 13:55", clave: "voltaje_bateria", valor: 12.7 },
      { fecha: "2026-01-08 13:55", clave: "horas_operacion", valor: 74 },
      { fecha: "2026-01-08 13:55", clave: "corriente_bateria", valor: 1.8 }
    ]
  },
  {
    id: 4,
    nombre: "Estanque Central",
    datos: [
      { fecha: "2026-01-08 14:40", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 14:40", clave: "litros_total", valor: 12900 },
      { fecha: "2026-01-08 14:40", clave: "nivel_estanque", valor: 8450 },
      { fecha: "2026-01-08 14:40", clave: "temperatura", valor: 18.9 },
      { fecha: "2026-01-08 14:40", clave: "voltaje_bateria", valor: 12.9 },
      { fecha: "2026-01-08 14:40", clave: "horas_operacion", valor: 2400 },
      { fecha: "2026-01-08 14:40", clave: "presion", valor: 3.2 },
      { fecha: "2026-01-08 14:40", clave: "alarma_nivel_bajo", valor: false }
    ]
  },
  {
    id: 5,
    nombre: "Generador A1",
    datos: [
      { fecha: "2026-01-08 14:10", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 14:10", clave: "litros_total", valor: null },
      { fecha: "2026-01-08 14:10", clave: "nivel_estanque", valor: null },
      { fecha: "2026-01-08 14:10", clave: "temperatura", valor: 67 },
      { fecha: "2026-01-08 14:10", clave: "voltaje_bateria", valor: 13.1 },
      { fecha: "2026-01-08 14:10", clave: "horas_operacion", valor: 356 },
      { fecha: "2026-01-08 14:10", clave: "rpm_motor", valor: 2800 },
      { fecha: "2026-01-08 14:10", clave: "consumo_lph", valor: 14.8 }
    ]
  },
  {
    id: 6,
    nombre: "Camión 223-B",
    datos: [
      { fecha: "2026-01-08 14:05", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 14:05", clave: "litros_total", valor: 860 },
      { fecha: "2026-01-08 14:05", clave: "nivel_estanque", valor: 410 },
      { fecha: "2026-01-08 14:05", clave: "temperatura", valor: 26.3 },
      { fecha: "2026-01-08 14:05", clave: "voltaje_bateria", valor: 12.8 },
      { fecha: "2026-01-08 14:05", clave: "horas_operacion", valor: 1840 },
      { fecha: "2026-01-08 14:05", clave: "velocidad", valor: 68 },
      { fecha: "2026-01-08 14:05", clave: "odometro_km", valor: 55832 },
      { fecha: "2026-01-08 14:05", clave: "rpm_motor", valor: 2100 }
    ]
  },
  {
    id: 7,
    nombre: "Camioneta 4x4 ZR",
    datos: [
      { fecha: "2026-01-08 14:15", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 14:15", clave: "litros_total", valor: 240 },
      { fecha: "2026-01-08 14:15", clave: "nivel_estanque", valor: 130 },
      { fecha: "2026-01-08 14:15", clave: "temperatura", valor: 25.1 },
      { fecha: "2026-01-08 14:15", clave: "voltaje_bateria", valor: 12.6 },
      { fecha: "2026-01-08 14:15", clave: "horas_operacion", valor: 960 },
      { fecha: "2026-01-08 14:15", clave: "velocidad", valor: 72 },
      { fecha: "2026-01-08 14:15", clave: "odometro_km", valor: 18450 },
      { fecha: "2026-01-08 14:15", clave: "temperatura_motor", valor: 91 }
    ]
  },
  {
    id: 8,
    nombre: "Motobomba Sur",
    datos: [
      { fecha: "2026-01-08 13:50", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 13:50", clave: "litros_total", valor: null },
      { fecha: "2026-01-08 13:50", clave: "nivel_estanque", valor: null },
      { fecha: "2026-01-08 13:50", clave: "temperatura", valor: 36.5 },
      { fecha: "2026-01-08 13:50", clave: "voltaje_bateria", valor: 11.9 },
      { fecha: "2026-01-08 13:50", clave: "horas_operacion", valor: 420 },
      { fecha: "2026-01-08 13:50", clave: "presion", valor: 4.1 },
      { fecha: "2026-01-08 13:50", clave: "caudal_lpm", valor: 120 }
    ]
  },
  {
    id: 9,
    nombre: "Tractor Case 550",
    datos: [
      { fecha: "2026-01-08 13:40", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 13:40", clave: "litros_total", valor: 640 },
      { fecha: "2026-01-08 13:40", clave: "nivel_estanque", valor: 320 },
      { fecha: "2026-01-08 13:40", clave: "temperatura", valor: 27.4 },
      { fecha: "2026-01-08 13:40", clave: "voltaje_bateria", valor: 12.9 },
      { fecha: "2026-01-08 13:40", clave: "horas_operacion", valor: 1820 },
      { fecha: "2026-01-08 13:40", clave: "rpm_motor", valor: 2200 },
      { fecha: "2026-01-08 13:40", clave: "temperatura_motor", valor: 88 }
    ]
  },
  {
    id: 10,
    nombre: "Bodega Norte",
    datos: [
      { fecha: "2026-01-08 14:00", clave: "estado_dispositivo", valor: "online" },
      { fecha: "2026-01-08 14:00", clave: "litros_total", valor: null },
      { fecha: "2026-01-08 14:00", clave: "nivel_estanque", valor: null },
      { fecha: "2026-01-08 14:00", clave: "temperatura", valor: 15.2 },
      { fecha: "2026-01-08 14:00", clave: "voltaje_bateria", valor: 12.1 },
      { fecha: "2026-01-08 14:00", clave: "horas_operacion", valor: 0 },
      { fecha: "2026-01-08 14:00", clave: "humedad", valor: 63 },
      { fecha: "2026-01-08 14:00", clave: "temperatura_max", valor: 18.7 },
      { fecha: "2026-01-08 14:00", clave: "temperatura_min", valor: 12.4 },
      { fecha: "2026-01-08 14:00", clave: "alarma_temperatura", valor: false }
    ]
  }
])





// ===========================================
// ESTADOS SELECCIONADOS
// ===========================================
const selectedDevices = ref([])
const selectedVariables = ref([])
const dateRange = ref({ type: "preset", value: "last_24h" })



// ===========================================
// DISPOSITIVOS FILTRADOS
// ===========================================
const filteredDevices = computed(() =>
  dispositivos.value.filter(d => selectedDevices.value.includes(d.id))
)


// ===========================================
// VARIABLES DINÁMICAS SEGÚN DISPOSITIVOS
// ===========================================
const availableVariables = computed(() => {
  const keys = new Set()

  for (const d of filteredDevices.value) {
    const datos = Array.isArray(d.datos) ? d.datos : []
    for (const dato of datos) {
      if (dato?.clave) keys.add(dato.clave)
    }
  }

  return Array.from(keys).map(k => ({
    key: k,
    label: k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())
  }))
})



// ===========================================
// EXPORTACIÓN
// ===========================================
function exportPDF() {
  console.log("EXPORTAR PDF:", {
    dispositivos: selectedDevices.value,
    variables: selectedVariables.value,
    rango: dateRange.value
  })
}

function exportExcel() {
  console.log("EXPORTAR EXCEL:", {
    dispositivos: selectedDevices.value,
    variables: selectedVariables.value,
    rango: dateRange.value
  })
}

function exportCSV() {
  console.log("EXPORTAR CSV:", {
    dispositivos: selectedDevices.value,
    variables: selectedVariables.value,
    rango: dateRange.value
  })
}
</script>
