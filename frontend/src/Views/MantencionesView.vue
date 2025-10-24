<template>
  <div class="p-2">
    <MantencionesTable :mantenciones="mantenciones" @ver-mantenciones="verMantenciones"
      @agregar-mantencion="abrirModal" />

    <ModalAgregar :show-add-modal="showAddModal" :selected-patente="patenteSeleccionada"
      :mantenciones="mantencionesPorPatente[patenteSeleccionada] || []" :selected-mantencion="mantencionSeleccionada"
      :km-actual="selectedVehiculo?.odometro || 0" @close="cerrarModal" @save="guardarMantencion" />


    <ModalVerMantenciones v-if="showVerModal" :patente="patenteSeleccionada"
      :mantenciones="mantencionesPorPatente[patenteSeleccionada] || []"
      :odometro-actual="selectedVehiculo?.odometro || 0" :horometros-actuales="horometrosActuales"
      @close="showVerModal = false" @editar="editarMantencion" @eliminar="eliminarMantencion" />


  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import MantencionesTable from '@/components/MantencionesUi/MantencionesTable.vue'
import ModalAgregar from '@/components/MantencionesUi/ModalAgregar.vue'
import ModalVerMantenciones from '@/components/MantencionesUi/ModalVerMantenciones.vue'

// ------------------------------
// 🔹 Variables reactivas principales
// ------------------------------
const patenteSeleccionada = ref('')              // Guarda la patente del vehículo actualmente seleccionado
const selectedVehiculo = ref(null)               // Guarda los datos del vehículo al que se le está agregando/editar una mantención
const mantencionSeleccionada = ref(null)         // Índice de la mantención que se está editando

const showAddModal = ref(false)                  // Controla la visibilidad del modal de agregar/editar
const showVerModal = ref(false)                  // Controla la visibilidad del modal de ver mantenciones

// 🔹 Diccionario reactivo que guarda las mantenciones por vehículo (clave = patente)
const mantencionesPorPatente = reactive({})

// ------------------------------
// 🔹 Lista principal de vehículos
// ------------------------------
const mantenciones = ref([
  { patente: 'ABC123', odometro: 4500, estado: 'OK' },
  { patente: 'XYZ789', odometro: 72000, estado: 'Requiere mantención' },
  { patente: 'DEF456', odometro: 60000, estado: 'Próxima mantención' },
])
const horometrosActuales = {
  'ABC123': 145,   // vehículo 1
  'XYZ789': 230,  // vehículo 2
  'DEF456': 87,   // vehículo 3
}
// ------------------------------
// 🔹 Abrir modal para agregar o editar mantención
// ------------------------------
function abrirModal(item) {
  selectedVehiculo.value = item
  patenteSeleccionada.value = item.patente

  // Si no existe una lista de mantenciones para esa patente, se crea
  if (!mantencionesPorPatente[item.patente]) {
    mantencionesPorPatente[item.patente] = []
  }

  mantencionSeleccionada.value = null
  showAddModal.value = true
}

// ------------------------------
// 🔹 Cerrar modal de agregar/editar
// ------------------------------
function cerrarModal() {
  showAddModal.value = false
  selectedVehiculo.value = null
  mantencionSeleccionada.value = null
}

// ------------------------------
// 🔹 Abrir modal de visualización de mantenciones
// ------------------------------
function verMantenciones(item) {
  patenteSeleccionada.value = item.patente
  showVerModal.value = true
}

// ------------------------------
// 🔹 Guardar mantención (nuevo registro o edición existente)
// ------------------------------
function guardarMantencion(maintenance) {
  const patente = patenteSeleccionada.value

  // Si no existe una lista para esa patente, se crea reactivamente
  if (!mantencionesPorPatente[patente]) {
    mantencionesPorPatente[patente] = []
  }

  const mantencionesVehiculo = mantencionesPorPatente[patente]
  const editingIndex = mantencionSeleccionada.value

  // Si se está editando, reemplaza el registro
  if (editingIndex !== null) {
    mantencionesVehiculo[editingIndex] = maintenance
  }
  // Si es una nueva mantención, la agrega al final del array
  else {
    mantencionesVehiculo.push(maintenance)
  }

  // 🔹 Actualiza el estado del vehículo en la tabla principal según sus mantenciones
  actualizarEstadoVehiculo(patente)
  cerrarModal()
}

// ------------------------------
// 🔹 Editar una mantención existente desde el modal de ver
// ------------------------------
function editarMantencion(idx) {
  const patente = patenteSeleccionada.value

  // Si no existe lista, se inicializa vacía
  if (!mantencionesPorPatente[patente]) {
    mantencionesPorPatente[patente] = []
  }

  // Busca el vehículo real en la lista principal
  const vehiculo = mantenciones.value.find(v => v.patente === patente)

  mantencionSeleccionada.value = idx
  selectedVehiculo.value = vehiculo ? { ...vehiculo } : { patente, odometro: 0 }

  showAddModal.value = true
}

// ------------------------------
// 🔹 Determina el estado actual del vehículo según sus mantenciones
// ------------------------------
function actualizarEstadoVehiculo(patente) {
  const lista = mantencionesPorPatente[patente]

  // Si no hay mantenciones, el estado es "OK"
  if (!lista || lista.length === 0) {
    cambiarEstado(patente, 'OK')
    return
  }

  // Se prioriza el peor estado presente
  if (lista.some(m => m.estado === 'Requiere mantención')) {
    cambiarEstado(patente, 'Requiere mantención')
  } else if (lista.some(m => m.estado === 'Próxima mantención')) {
    cambiarEstado(patente, 'Próxima mantención')
  } else {
    cambiarEstado(patente, 'OK')
  }
}

// ------------------------------
// 🔹 Eliminar una mantención desde el modal de visualización
// ------------------------------
function eliminarMantencion(idx) {
  const patente = patenteSeleccionada.value
  mantencionesPorPatente[patente].splice(idx, 1)

  // Al eliminar, recalcula el estado del vehículo
  actualizarEstadoVehiculo(patente)
}

// ------------------------------
// 🔹 Cambiar el estado del vehículo en la tabla principal
// ------------------------------
function cambiarEstado(patente, nuevoEstado) {
  const vehiculo = mantenciones.value.find(v => v.patente === patente)
  if (vehiculo) {
    vehiculo.estado = nuevoEstado
  } else {
    console.warn(`[Padre] No se encontró vehículo con patente ${patente}`)
  }
}
</script>
