<template>
  <div class="flex flex-col p-4">
    <!-- Navbar -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-gray-700 pb-2">
      <div class="w-full sm:flex-1">
        <input v-model="searchTerm" type="text" placeholder="Buscar empresa..."
          class="w-full px-3 py-1 text-gray-900 focus:outline-none focus:ring focus:ring-gray-500 rounded" />
      </div>

      <div class="flex w-full sm:w-auto gap-2 mt-2 sm:mt-0">
        <button @click.prevent="showAddModal = true"
          class="relative inline-flex items-center justify-center w-full sm:w-auto px-3 py-2 font-mono font-medium tracking-tighter text-white bg-gray-800 rounded-lg overflow-hidden group">
          <span
            class="absolute w-0 h-0 bg-[#ff6600] rounded-full transition-all duration-500 ease-out group-hover:w-56 group-hover:h-56"></span>
          <span
            class="absolute inset-0 w-full h-full opacity-30 bg-gradient-to-b from-transparent via-transparent to-gray-700 rounded-lg -mt-1"></span>
          <span class="relative">➕ Agregar Empresa</span>
        </button>

        <!-- Botón eliminar seleccionados -->
        <transition name="fade-scale">
          <button v-if="selectedIds.length > 0" @click="deleteSelected"
            class="bg-red-600 hover:bg-red-700 text-white p-2 rounded flex items-center justify-center"
            title="Eliminar seleccionados">
            <SvgIcon name="trash" class="w-5 h-5" />
          </button>
        </transition>
      </div>
    </div>

    <!-- Tabla -->
    <div class="flex-1 mt-4 flex flex-col">
      <div class="overflow-y-auto min-h-[400px] max-h-[400px] rounded-lg shadow flex-1">
        <table class="min-w-full bg-gray-800 text-white">
          <thead>
            <tr class="bg-[#102372] text-left">
              <th class="py-6 px-4 w-1/12 flex items-center gap-1">
                <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
              </th>
              <th class="py-2 px-4">Fecha de Creación</th>
              <th class="py-2 px-4">Nombre</th>
              <th class="py-2 px-4">Rut</th>
              <th class="py-2 px-4">Contacto</th>
              <th class="py-2 px-4">Ciudad</th>
              <th class="py-2 px-4">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in paginatedCustomers" :key="customer.id"
              class="border-t border-gray-700 bg-gray-20 hover:bg-gray-700 transition">
              <td class="py-2 px-4">
                <input type="checkbox" v-model="selectedIds" :value="customer.id" />
              </td>
              <td class="py-2 px-4">{{ customer.createdAt }}</td>
              <td class="py-2 px-4">{{ customer.name }}</td>
              <td class="py-2 px-4">{{ customer.rut }}</td>
              <td class="py-2 px-4">{{ customer.contact }}</td>
              <td class="py-2 px-4">{{ customer.city }}</td>
              <td class="py-2 px-4 flex gap-2">
                <!-- Editar -->
                <button @click="editCustomer(customer)" title="Editar"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md flex items-center gap-1">
                  <SvgIcon name="pencil" class="w-4 h-4" />
                </button>

                <!-- Copiar -->
                <button @click="copyCustomerData(customer)" title="Copiar"
                  class="px-2 py-1 bg-gray-800 text-white rounded hover:bg-gray-700 relative flex items-center">
                  <SvgIcon name="copy" class="w-5 h-5" />
                  <span v-if="copiedId === customer.id"
                    class="absolute -top-6 left-1/2 transform -translate-x-1/2 bg-gray-700 text-white text-xs px-2 py-1 rounded">
                    Copiado!
                  </span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div
        class="bg-gray-900 text-gray-300 p-4 rounded-b-lg shadow-inner flex flex-col sm:flex-row sm:justify-between items-center gap-4">
        <div class="flex items-center gap-2">
          <span>Filas por página:</span>
          <select v-model="rowsPerPage" class="bg-gray-800 text-white rounded px-2 py-1 focus:outline-none">
            <option v-for="option in rowsPerPageOptions" :key="option" :value="option">{{ option }}</option>
          </select>
        </div>

        <ul class="flex justify-center gap-1 text-gray-300">
          <li>
            <button @click="previousPage" :disabled="currentPage === 1"
              class="grid w-8 h-8 place-content-center rounded border border-gray-700 transition-colors hover:bg-gray-700 disabled:opacity-50"
              aria-label="Previous page">
              <SvgIcon name="chevron-left" class="w-4 h-4" />
            </button>
          </li>

          <li v-for="page in totalPages" :key="page">
            <button @click="currentPage = page" :class="[
              'w-8 h-8 text-sm font-medium rounded border flex items-center justify-center',
              page === currentPage
                ? 'bg-indigo-600 border-indigo-600 text-white'
                : 'border-gray-700 hover:bg-gray-700'
            ]">
              {{ page }}
            </button>
          </li>

          <li>
            <button @click="nextPage" :disabled="currentPage === totalPages"
              class="grid w-8 h-8 place-content-center rounded border border-gray-700 transition-colors hover:bg-gray-700 disabled:opacity-50"
              aria-label="Next page">
              <SvgIcon name="chevron-right" class="w-4 h-4" />
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
  <!-- Sidebar Edición -->
  <transition name="slide-fade">
    <div v-if="showEditSidebar" class="fixed inset-0 z-50 flex justify-end">

      <!-- Fondo semi-transparente -->
      <div @click="showEditSidebar = false" class="absolute inset-0 bg-black bg-opacity-50"></div>

      <!-- Sidebar -->
      <div class="relative w-full max-w-md sm:w-96 bg-gray-800 text-white shadow-xl flex flex-col h-full">

        <!-- Contenido scrollable -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- Botón cerrar -->
          <button @click="showEditSidebar = false" class="self-end p-2 rounded hover:bg-gray-700 transition mb-2">
            <SvgIcon name="close" class="w-6 h-6" />
          </button>

          <h2 class="text-2xl font-bold mb-4">Editar Empresa</h2>

          <form @submit.prevent="updateCompany" class="flex flex-col gap-3">
            <input v-model="editingCompany.name" type="text" placeholder="Nombre de la empresa"
              class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />

            <input v-model="editingCompany.rut" type="text" placeholder="RUT de la empresa"
              class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />

            <input v-model="editingCompany.contact" type="text" placeholder="Contacto"
              class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />

            <input v-model="editingCompany.city" type="text" placeholder="Ciudad de la empresa"
              class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />

            <!-- Plantillas -->
            <div class="mt-4">
              <label class="block mb-1">Plantilla / Permisos:</label>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div v-for="template in templates" :key="template.id" @click="editingCompany.templateId = template.id"
                  :class="[
                    'p-3 rounded-lg border cursor-pointer text-center transition',
                    editingCompany.templateId === template.id
                      ? 'border-blue-500 bg-blue-700'
                      : 'border-gray-600 hover:bg-gray-700'
                  ]">
                  <h3 class="font-semibold">{{ template.name }}</h3>
                  <p class="text-gray-300 text-sm">{{ template.description }}</p>
                </div>
              </div>
            </div>
          </form>
        </div>

        <!-- Botones siempre visibles -->
        <div class="p-6 border-t border-gray-700 bg-gray-800 flex justify-center gap-2">

          <button @click="updateCompany" class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded">
            Guardar Cambios
          </button>
          <button @click="showEditSidebar = false" class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded">
            Cancelar
          </button>
        </div>

      </div>
    </div>
  </transition>




  <!-- Modal multi-paso -->
  <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 text-white rounded-lg relative flex flex-col w-full max-w-lg h-auto p-6">

      <!-- Botón volver paso 2 -> 1 -->
      <button v-if="step === 2" @click="step = 1" class="absolute top-4 left-4 p-2 rounded hover:bg-gray-700 transition"
        title="Volver">
        <SvgIcon name="arrow-left" class="w-6 h-6" />
      </button>

      <h2 class="text-2xl font-bold mb-4 text-center">
        {{ step === 1 ? 'Agregar Empresa' : 'Seleccionar Template' }}
      </h2>

      <span class="h-px bg-gray-600 mb-4"></span>

      <!-- Paso 1 -->
      <form v-if="step === 1" @submit.prevent="goToNextStep" class="flex-1 flex flex-col gap-3 py-2 overflow-y-auto">
        <input v-model="newCompany.name" type="text" placeholder="Nombre de la empresa"
          class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />

        <input v-model="newCompany.rut" type="text" placeholder="RUT de la empresa"
          class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required
          @input="formatRut(newCompany)" />

        <input v-model="newCompany.contact" type="text" placeholder="Contacto"
          class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />

        <input v-model="newCompany.city" type="text" placeholder="Ciudad de la empresa"
          class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />
      </form>

      <!-- Paso 2 -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4">
        <div v-for="template in templates" :key="template.id" @click="selectedTemplate = template.id" :class="[
          'p-6 rounded-lg border cursor-pointer text-center transition',
          selectedTemplate === template.id
            ? 'border-blue-500 bg-blue-700'
            : 'border-gray-600 hover:bg-gray-700'
        ]">
          <h3 class="text-lg font-semibold mb-2">{{ template.name }}</h3>
          <p class="text-gray-300 text-sm">{{ template.description }}</p>
        </div>
      </div>

      <!-- Botones del modal multi-paso -->
      <div class="flex justify-between mt-6">
        <button @click="cancel" class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded w-[48%]">
          Cancelar
        </button>

        <button v-if="step === 1" @click="goToNextStep" :disabled="!isStep1Valid"
          :class="['px-4 py-2 rounded w-[48%]', isStep1Valid ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-600 opacity-50 cursor-not-allowed']">
          {{ modalButtonText }}
        </button>

        <button v-else @click="addCompany" :disabled="isModalButtonDisabled" :class="[
          'px-4 py-2 rounded w-[48%]',
          isModalButtonDisabled
            ? 'bg-green-600 opacity-50 cursor-not-allowed'
            : 'bg-green-600 hover:bg-green-700'
        ]">
          {{ modalButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'

// Constante para plantilla por defecto
const DEFAULT_TEMPLATE_ID = 1

// Datos iniciales
const customers = ref([
  { id: 1, createdAt: '2025-07-30', name: 'Demo Combustible', rut: '76.145.230-9', contact: 'Marcelo Díaz', city: 'Santiago' },
  { id: 2, createdAt: '2025-07-23', name: 'Industrial Glover S.P.A.', rut: '77.239.684-2', contact: 'Patricia González', city: 'Lautaro' },
  { id: 3, createdAt: '2025-05-29', name: 'Cuenta Demo', rut: '76.003.412-5', contact: 'Claudia Muñoz', city: 'Temuco' },
  { id: 4, createdAt: '2025-05-19', name: 'Constructora Rucol Limitada', rut: '76.918.527-1', contact: 'Rodrigo Herrera', city: 'Temuco' },
  { id: 5, createdAt: '2025-05-19', name: 'Armory Sustentable', rut: '77.562.981-3', contact: 'Andrea Castillo', city: 'Temuco' },
  { id: 6, createdAt: '2025-05-19', name: 'Transportes Betancourt', rut: '76.421.875-6', contact: 'Carlos Fuentes', city: 'Temuco' },
  { id: 7, createdAt: '2025-05-19', name: 'Áridos Macoga SPA', rut: '77.158.443-0', contact: 'Natalia Vega', city: 'Temuco' },
  { id: 8, createdAt: '2025-05-19', name: 'Servicios Marítimos Plast Marine Limitada', rut: '76.998.224-9', contact: 'Ignacio Contreras', city: 'Puerto Montt' },
  { id: 9, createdAt: '2025-05-19', name: 'Constructora Stange Hermanos Ltda', rut: '77.304.652-2', contact: 'Francisca Rojas', city: 'Temuco' },
  { id: 10, createdAt: '2025-05-16', name: 'Safco', rut: '76.842.913-8', contact: 'Germán Paredes', city: 'Temuco' }
])

const searchTerm = ref('')
const selectedIds = ref([])
const selectAll = ref(false)
const rowsPerPageOptions = [5, 10, 20, 50]
const rowsPerPage = ref(5)
const currentPage = ref(1)
const showAddModal = ref(false)
const step = ref(1)
const selectedTemplate = ref(null)
const showEditSidebar = ref(false)
const editingCompany = ref({ id: null, name: '', rut: '', contact: '', city: '', templateId: DEFAULT_TEMPLATE_ID })
const newCompany = ref({ name: '', rut: '', contact: '', city: '' })
const copiedId = ref(null)

// Plantillas
const templates = ref([
  { id: 1, name: 'Básico', description: 'Acceso limitado a reportes y panel general.' },
  { id: 2, name: 'Profesional', description: 'Incluye reportes y comentarios.' },
  { id: 3, name: 'Avanzado', description: 'Incluye dashboards personalizados y reportes completos.' },
  { id: 4, name: 'Full', description: 'Todas las funciones habilitadas.' }
])

// Validación RUT chileno (formato xx.xxx.xxx-x)
const isValidRut = (rut) => /^(\d{1,2}\.\d{3}\.\d{3}-[\dkK])$/.test(rut)

// Computed: filtrado y paginación
const filteredCustomers = computed(() => {
  if (!searchTerm.value) return customers.value
  const term = searchTerm.value.toLowerCase()
  return customers.value.filter(c =>
    c.name.toLowerCase().includes(term) ||
    c.rut.toLowerCase().includes(term) ||
    c.contact.toLowerCase().includes(term) ||
    c.createdAt.toLowerCase().includes(term)
  )
})

// Formateo automático RUT mientras se escribe
const formatRut = (company) => {
  let rut = company.rut.replace(/[^0-9kK]/g, '')
  if (rut.length > 9) rut = rut.slice(0, 9)

  if (rut.length > 1) {
    const body = rut.slice(0, -1)
    const dv = rut.slice(-1)
    const reversed = body.split('').reverse()
    const withDots = []
    reversed.forEach((char, i) => { if (i > 0 && i % 3 === 0) withDots.push('.'); withDots.push(char) })
    company.rut = withDots.reverse().join('') + '-' + dv
  } else {
    company.rut = rut
  }
}

// Validación paso 1: todos los campos requeridos + RUT válido
const isStep1Valid = computed(() => {
  const { name, rut, contact, city } = newCompany.value
  return name.trim() && rut.trim() && contact.trim() && city.trim() && isValidRut(rut)
})

// Paginar clientes
const paginatedCustomers = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value
  return filteredCustomers.value.slice(start, start + rowsPerPage.value)
})

const totalPages = computed(() => Math.ceil(filteredCustomers.value.length / rowsPerPage.value))

// Select all toggle
const toggleSelectAll = () => selectAll.value
  ? selectedIds.value = paginatedCustomers.value.map(c => c.id)
  : selectedIds.value = []

// Paginación
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const previousPage = () => { if (currentPage.value > 1) currentPage.value-- }

// Modal multi-paso
const goToNextStep = () => {
  if (isStep1Valid.value) step.value = 2
  else alert('Completa todos los campos correctamente antes de continuar.')
}

// Cancelar modal
const cancel = () => {
  showAddModal.value = false
  step.value = 1
  selectedTemplate.value = null
  newCompany.value = { name: '', rut: '', contact: '', city: '' }
}

// Agregar empresa con ID único y validación RUT
const addCompany = () => {
  if (!selectedTemplate.value) return
  if (!isValidRut(newCompany.value.rut)) {
    alert('RUT inválido. Formato esperado: xx.xxx.xxx-x')
    return
  }
  const id = Date.now()
  const createdAt = new Date().toISOString().slice(0, 10)
  customers.value.push({ id, createdAt, ...newCompany.value, templateId: selectedTemplate.value })
  cancel()
}

// Eliminar seleccionados
const deleteSelected = () => {
  customers.value = customers.value.filter(c => !selectedIds.value.includes(c.id))
  selectedIds.value = []
}

// Copiar datos con tooltip reutilizable
const copyCustomerData = (customer) => {
  const data = `Nombre: ${customer.name}\nRUT: ${customer.rut}\nContacto: ${customer.contact}`
  navigator.clipboard.writeText(data).then(() => {
    copiedId.value = customer.id
    setTimeout(() => copiedId.value = null, 1000)
  })
}

// Editar empresa
const editCustomer = (customer) => {
  editingCompany.value = { ...customer }
  if (!editingCompany.value.templateId) editingCompany.value.templateId = DEFAULT_TEMPLATE_ID
  showEditSidebar.value = true
}

// Guardar cambios
const updateCompany = () => {
  if (!isValidRut(editingCompany.value.rut)) {
    alert('RUT inválido. Formato esperado: xx.xxx.xxx-x')
    return
  }
  const index = customers.value.findIndex(c => c.id === editingCompany.value.id)
  if (index !== -1) customers.value[index] = { ...editingCompany.value }
  showEditSidebar.value = false
}

// Computed para texto dinámico de botones en modal
const modalButtonText = computed(() => step.value === 1 ? 'Siguiente' : 'Crear Empresa')
const isModalButtonDisabled = computed(() => step.value === 2 && !selectedTemplate.value)

// Reset selectAll al cambiar página
watch(paginatedCustomers, () => selectAll.value = false)
</script>



<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.3s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.fade-scale-enter-to,
.fade-scale-leave-from {
  opacity: 1;
  transform: scale(1);
}


.slide-fade-enter-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-fade-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-enter-to,
.slide-fade-leave-from {
  transform: translateX(0);
  opacity: 1;
}
</style>
