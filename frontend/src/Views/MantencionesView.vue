<template>
  <div class="p-2">
    <MantencionesTable
      :mantenciones="mantenciones"
      @ver-mantenciones="verMantenciones"
      @agregar-mantencion="abrirModal"
    />

<ModalAgregar
  v-if="showAddModal"
  :show-add-modal="showAddModal"
  :selected-patente="patenteSeleccionada"
  :mantenciones="mantencionesPorPatente[patenteSeleccionada] || []"
  :selected-mantencion="mantencionSeleccionada"
  @close="cerrarModal"
  @save="guardarMantencion"
/>

<ModalVerMantenciones
  v-if="showVerModal"
  :patente="patenteSeleccionada"
  :mantenciones="mantencionesPorPatente[patenteSeleccionada] || []" 
  @close="showVerModal=false"
  @editar="editarMantencion"
  @eliminar="eliminarMantencion"
/>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import MantencionesTable from '@/components/MantencionesUi/MantencionesTable.vue'
import ModalAgregar from '@/components/MantencionesUi/ModalAgregar.vue'
import ModalVerMantenciones from '@/components/MantencionesUi/ModalVerMantenciones.vue'

const patenteSeleccionada = ref('')
const selectedVehiculo = ref(null)
const mantencionSeleccionada = ref(null) // Para editar

const showAddModal = ref(false)
const showVerModal = ref(false)

// Mantenciones por patente
const mantencionesPorPatente = ref({})

// Lista inicial de vehículos
const mantenciones = ref([
  { patente: 'ABC123', odometro: 4500, estado: 'OK' },
  { patente: 'XYZ789', odometro: 72000, estado: 'Requiere mantención' },
  { patente: 'DEF456', odometro: 60000, estado: 'Próxima mantención' },
])

function abrirModal(item) {
  selectedVehiculo.value = item
  patenteSeleccionada.value = item.patente
  mantencionSeleccionada.value = null // Nuevo registro
  showAddModal.value = true
}

function cerrarModal() {
  showAddModal.value = false
  selectedVehiculo.value = null
  mantencionSeleccionada.value = null
}

function verMantenciones(item) {
  patenteSeleccionada.value = item.patente
  showVerModal.value = true
}

// Guardar mantención (nuevo o editar)
function guardarMantencion(maintenance) {
  const patente = patenteSeleccionada.value
  if (!mantencionesPorPatente.value[patente]) {
    mantencionesPorPatente.value[patente] = []
  }

  if (mantencionSeleccionada.value !== null) {
    // Editar existente
    mantencionesPorPatente.value[patente][mantencionSeleccionada.value] = maintenance
  } else {
    // Agregar nuevo
    mantencionesPorPatente.value[patente].push(maintenance)
  }

  cerrarModal()
}

// Editar desde ModalVerMantenciones
function editarMantencion(idx) {
  const patente = patenteSeleccionada.value
  mantencionSeleccionada.value = idx
  selectedVehiculo.value = { patente }
  showAddModal.value = true
}

// Eliminar desde ModalVerMantenciones
function eliminarMantencion(idx) {
  const patente = patenteSeleccionada.value
  mantencionesPorPatente.value[patente].splice(idx, 1)
}
</script>
