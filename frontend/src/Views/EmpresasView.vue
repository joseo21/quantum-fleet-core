<template>
  <div class="p-2 sm:p-4 w-full flex flex-col">
    <div class="flex flex-col sm:flex-row justify-between items-center mb-4 gap-3">
      <!-- Barra de búsqueda -->
      <div class="flex w-full sm:w-2/3 md:w-1/2">
        <div class="flex w-full border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
          <div class="flex items-center justify-center px-3 bg-gray-100 dark:bg-gray-800 text-gray-500">
            <SvgIcon name="search" class="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <input v-model="searchTerm" placeholder="Buscar empresa..."
            class="flex-1 p-2 text-sm sm:text-base bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-300 focus:outline-none" />
          <button v-if="searchTerm" @click="searchTerm = ''"
            class="px-4 bg-[#ff6600] hover:bg-[#e65500] text-white font-semibold text-sm transition">
            Limpiar
          </button>
        </div>
      </div>

      <!-- Botones -->
      <div class="flex gap-2">
        <button @click.prevent="showAddModal = true"
          class="flex items-center justify-center gap-2 px-4 py-2 bg-[#ff6600] hover:bg-[#e65500] text-white rounded-md font-medium transition">
          <SvgIcon name="plus" class="w-5 h-5" />
          <span>Agregar Empresa</span>
        </button>

        <!-- Eliminar seleccionados -->
        <transition name="fade-scale">
          <button v-if="selectedIds.length > 0" @click="deleteSelected"
            class="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition">
            <SvgIcon name="trash" class="w-5 h-5" />
          </button>
        </transition>
      </div>
    </div>

    <!-- 📋 Tabla -->
    <div class="border border-gray-300 dark:border-gray-700 rounded-lg shadow-sm overflow-y-auto max-h-[500px]">
      <table class="min-w-full text-xs sm:text-sm md:text-base text-center border-collapse">
        <thead class="bg-[#102372] dark:bg-[#102372] sticky top-0 z-10 text-gray-100">
          <tr>
            <th class="py-2 px-3">
              <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
            </th>
            <th class="py-2 px-3">Fecha de Creación</th>
            <th class="py-2 px-3">Nombre</th>
            <th class="py-2 px-3">RUT</th>
            <th class="py-2 px-3">Contacto</th>
            <th class="py-2 px-3">Ciudad</th>
            <th class="py-2 px-3">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in paginatedCustomers" :key="customer.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b dark:border-gray-600 transition">
            <td class="py-2 px-3">
              <input type="checkbox" v-model="selectedIds" :value="customer.id" />
            </td>
            <td class="py-2 px-3">{{ customer.createdAt }}</td>
            <td class="py-2 px-3">{{ customer.name }}</td>
            <td class="py-2 px-3">{{ customer.rut }}</td>
            <td class="py-2 px-3">{{ customer.contact }}</td>
            <td class="py-2 px-3">{{ customer.city }}</td>
            <td class="py-2 px-3 flex justify-center gap-2">
              <!-- Editar -->
              <button @click="editCustomer(customer)" title="Editar"
                class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md flex items-center gap-1">
                <SvgIcon name="pencil" class="w-4 h-4" />
                <span class="hidden sm:inline">Editar</span>
              </button>

              <!-- Copiar -->
              <button @click="copyCustomerData(customer)" title="Copiar"
                class="px-3 py-1 bg-gray-800 text-white rounded hover:bg-gray-700 relative flex items-center gap-1">
                <SvgIcon name="copy" class="w-4 h-4" />
                <span v-if="copiedId === customer.id"
                  class="absolute top-6 left-1/2 transform -translate-x-1/2 bg-gray-700 text-white text-xs px-2 py-1 rounded">
                  Copiado!
                </span>

              </button>
            </td>
          </tr>
          <tr v-if="paginatedCustomers.length === 0">
            <td colspan="7" class="text-center py-4 text-gray-500 dark:text-gray-400">
              No hay empresas registradas
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 📑 Paginación -->
    <div
      class="flex flex-col sm:flex-row justify-between items-center mt-4 text-xs sm:text-sm text-gray-700 dark:text-gray-300 gap-2 bg-[#f3f3f3] dark:bg-gray-800 p-2 rounded-md shadow-sm">
      <div class="flex items-center gap-2">
        <label for="rowsPerPage" class="text-xs">Filas por página:</label>
        <select id="rowsPerPage" v-model.number="rowsPerPage"
          class="border dark:border-gray-600 rounded px-2 py-1 text-xs sm:text-sm bg-white dark:bg-gray-700">
          <option v-for="n in rowsPerPageOptions" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>

      <div class="flex items-center gap-2">
        <button @click="previousPage" :disabled="currentPage === 1"
          class="px-2 py-1 rounded border border-gray-400 dark:border-gray-600 disabled:opacity-40 hover:bg-[#ff6600] hover:text-white transition">
          <SvgIcon name="chevron-left" class="w-4 h-4" />
        </button>
        <span>Página {{ currentPage }} / {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages"
          class="px-2 py-1 rounded border border-gray-400 dark:border-gray-600 disabled:opacity-40 hover:bg-[#ff6600] hover:text-white transition">
          <SvgIcon name="chevron-right" class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>

  <!-- 🟣 Sidebar edición -->
  <transition name="slide-fade">
    <div v-if="showEditSidebar" class="fixed inset-0 z-50 flex justify-end">
      <div @click="showEditSidebar = false" class="absolute inset-0 bg-black bg-opacity-50"></div>

      <div
        class="relative w-full max-w-md sm:w-96 bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-xl flex flex-col h-full">
        <div class="flex-1 overflow-y-auto p-6">
          <button @click="showEditSidebar = false"
            class="self-end p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition mb-2">
            <SvgIcon name="close" class="w-6 h-6" />
          </button>
          <h2 class="text-2xl font-bold mb-4 text-[#102372] dark:text-[#ff6600]">Editar Empresa</h2>

          <form @submit.prevent="updateCompany" class="flex flex-col gap-3">
            <input v-model="editingCompany.name" type="text" placeholder="Nombre de la empresa"
              class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              required />

            <input v-model="editingCompany.rut" type="text" placeholder="RUT de la empresa"
              class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              required />

            <input v-model="editingCompany.contact" type="text" placeholder="Contacto"
              class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              required />

            <input v-model="editingCompany.city" type="text" placeholder="Ciudad de la empresa"
              class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              required />

            <div class="mt-4">
              <label class="block mb-1 text-sm font-semibold text-[#102372] dark:text-[#ff6600]">Plantilla /
                Permisos:</label>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div v-for="template in templates" :key="template.id" @click="editingCompany.templateId = template.id"
                  :class="[
                    'p-3 rounded-lg border cursor-pointer text-center transition',
                    editingCompany.templateId === template.id
                      ? 'border-[#ff6600] bg-orange-100 dark:bg-[#e65500]/30'
                      : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                  ]">
                  <h3 class="font-semibold">{{ template.name }}</h3>
                  <p class="text-gray-500 dark:text-gray-400 text-sm">{{ template.description }}</p>
                </div>
              </div>
            </div>
          </form>
        </div>

        <div
          class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-center gap-2 bg-gray-50 dark:bg-gray-900">
          <button @click="updateCompany"
            class="bg-[#ff6600] hover:bg-[#e65500] px-4 py-2 rounded text-white font-medium">
            Guardar Cambios
          </button>
          <button @click="showEditSidebar = false" class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded text-white">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </transition>

  <!-- 🟠 Modal multi-paso -->
  <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div
      class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white rounded-lg relative flex flex-col w-full max-w-lg h-auto p-6 border border-gray-300 dark:border-gray-700 shadow-xl">

      <button v-if="step === 2" @click="step = 1"
        class="absolute top-4 left-4 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition" title="Volver">
        <SvgIcon name="arrow-left" class="w-6 h-6" />
      </button>

      <h2 class="text-2xl font-bold mb-4 text-center text-[#102372] dark:text-[#ff6600]">
        {{ step === 1 ? 'Agregar Empresa' : 'Seleccionar Template' }}
      </h2>

      <span class="h-px bg-gray-300 dark:bg-gray-700 mb-4"></span>

      <!-- Paso 1 -->
      <form v-if="step === 1" @submit.prevent="goToNextStep" class="flex-1 flex flex-col gap-3 py-2 overflow-y-auto">
        <input v-model="newCompany.name" type="text" placeholder="Nombre de la empresa"
          class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
          required />

        <input v-model="newCompany.rut" type="text" placeholder="RUT de la empresa"
          class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
          required @input="formatRut(newCompany)" />

        <input v-model="newCompany.contact" type="text" placeholder="Contacto"
          class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
          required />

        <input v-model="newCompany.city" type="text" placeholder="Ciudad de la empresa"
          class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
          required />
      </form>

      <!-- Paso 2 -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4">
        <div v-for="template in templates" :key="template.id" @click="selectedTemplate = template.id" :class="[
          'p-6 rounded-lg border cursor-pointer text-center transition',
          selectedTemplate === template.id
            ? 'border-[#ff6600] bg-orange-100 dark:bg-[#e65500]/30'
            : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
        ]">
          <h3 class="text-lg font-semibold mb-2">{{ template.name }}</h3>
          <p class="text-gray-500 dark:text-gray-400 text-sm">{{ template.description }}</p>
        </div>
      </div>

      <!-- Botones -->
      <div class="flex justify-between mt-6">
        <button @click="cancel" class="bg-gray-500 hover:bg-gray-600 px-4 py-2 rounded w-[48%] text-white">
          Cancelar
        </button>

        <button v-if="step === 1" @click="goToNextStep" :disabled="!isStep1Valid"
          :class="['px-4 py-2 rounded w-[48%] text-white font-medium', isStep1Valid ? 'bg-[#102372] hover:bg-[#0c1a5b]' : 'bg-[#102372]/50 cursor-not-allowed']">
          {{ modalButtonText }}
        </button>

        <button v-else @click="addCompany" :disabled="isModalButtonDisabled"
          :class="['px-4 py-2 rounded w-[48%] text-white font-medium', isModalButtonDisabled ? 'bg-[#ff6600]/50 cursor-not-allowed' : 'bg-[#ff6600] hover:bg-[#e65500]']">
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
