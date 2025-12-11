<template>
  <div class="w-full flex justify-center mt-2">

    <!-- CONTENEDOR PRINCIPAL (flotando, limpio, sin doble tarjeta) -->
    <div
      class="w-full max-w-[1500px] bg-white shadow-[0_8px_32px_rgba(0,0,0,0.12)] 
             rounded-2xl border border-gray-200 px-8 py-8 space-y-8"
    >

      <!-- ==========================
           FILTROS SUPERIORES
      =========================== -->
      <div class="flex flex-col lg:flex-row gap-4 items-center">

        <DeviceFilter
          class="flex-[3] min-w-[500px] h-[46px] shadow-sm hover:shadow-md transition rounded-xl"
          :dispositivos="dispositivos"
          @update:selected="selectedDevices = $event"
        />

        <VariableFilter
          class="flex-1 min-w-[200px] h-[46px] shadow-sm hover:shadow-md transition rounded-xl"
          :variables="availableVariables"
          @update:selected="selectedVariables = $event"
        />

        <DateFilter
          class="flex-1 min-w-[200px] h-[46px] shadow-sm hover:shadow-md transition rounded-xl"
          @update:range="dateRange = $event"
        />

        <ReportActions
          class="flex-none h-[46px] shadow-sm hover:shadow-md transition rounded-xl"
          :devices="selectedDevices"
          :variables="selectedVariables"
          @export:pdf="exportPDF"
          @export:excel="exportExcel"
          @export:csv="exportCSV"
        />

      </div>



      <!-- ==========================
           TABLA DE RESULTADOS
      =========================== -->

      <div class="rounded-xl overflow-hidden shadow-[0_4px_20px_rgba(0,0,0,0.08)]">
        <ReportesTable
          :items="filteredDevices"
          :variables="selectedVariables"
          :dateRange="dateRange"
        />
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
      { fecha: "2025-12-10 12:01", clave: "litros_total", valor: 350 },
      { fecha: "2025-12-10 12:01", clave: "nivel_estanque", valor: 180 }
    ]
  },
  {
    id: 2,
    nombre: "Dispositivo 02",
    datos: [
      { fecha: "2025-12-10 12:03", clave: "litros_total", valor: 520 },
      { fecha: "2025-12-08 16:00", clave: "pulsos_total", valor: 8750 },
      { fecha: "2025-12-08 16:00", clave: "temperatura", valor: 22.4 }
    ]
  },
  {
    id: 3,
    nombre: "Dispositivo 03",
    datos: [
      { fecha: "2025-12-09 09:00", clave: "nivel_estanque", valor: 300 },
      { fecha: "2025-12-09 09:00", clave: "voltaje_bateria", valor: 12.7 }
    ]
  },
  {
    id: 4,
    nombre: "Estanque Central",
    datos: [
      { fecha: "2025-12-11 08:20", clave: "litros_total", valor: 12900 },
      { fecha: "2025-12-11 08:20", clave: "presion", valor: 3.2 }
    ]
  },
  {
    id: 5,
    nombre: "Generador A1",
    datos: [
      { fecha: "2025-12-11 14:10", clave: "temperatura", valor: 67 },
      { fecha: "2025-12-11 14:10", clave: "pulsos_total", valor: 12000 }
    ]
  },
  {
    id: 6,
    nombre: "Camión 223-B",
    datos: [
      { fecha: "2025-12-10 19:43", clave: "litros_total", valor: 860 },
      { fecha: "2025-12-10 19:43", clave: "nivel_estanque", valor: 410 },
      { fecha: "2025-12-10 19:43", clave: "odometro_km", valor: 55832 }
    ]
  },
  {
    id: 7,
    nombre: "Camioneta 4x4 ZR",
    datos: [
      { fecha: "2025-12-11 11:25", clave: "litros_total", valor: 240 },
      { fecha: "2025-12-11 11:25", clave: "velocidad", valor: 72 }
    ]
  },
  {
    id: 8,
    nombre: "Motobomba Sur",
    datos: [
      { fecha: "2025-12-11 10:00", clave: "presion", valor: 4.1 },
      { fecha: "2025-12-11 10:00", clave: "voltaje_bateria", valor: 11.9 }
    ]
  },
  {
    id: 9,
    nombre: "Tractor Case 550",
    datos: [
      { fecha: "2025-12-10 17:00", clave: "litros_total", valor: 640 },
      { fecha: "2025-12-10 17:00", clave: "rpm_motor", valor: 2200 }
    ]
  },
  {
    id: 10,
    nombre: "Bodega Norte",
    datos: [
      { fecha: "2025-12-11 07:40", clave: "temperatura", valor: 15.2 },
      { fecha: "2025-12-11 07:40", clave: "humedad", valor: 63 }
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
