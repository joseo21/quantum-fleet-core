<template>
  <div class="p-2 sm:p-4 w-full flex flex-col">
    <div class="flex flex-col sm:flex-row justify-between items-center mb-4 gap-3">
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

      <div class="flex gap-2">
        <button @click.prevent="showAddModal = true"
          class="flex items-center justify-center gap-2 px-4 py-2 bg-[#ff6600] hover:bg-[#e65500] text-white rounded-md font-medium transition">
          <SvgIcon name="plus" class="w-5 h-5" />
          <span>Agregar Empresa</span>
        </button>

        <transition name="fade-scale">
          <button v-if="selectedIds.length > 0" @click="deleteSelected"
            class="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition">
            <SvgIcon name="trash" class="w-5 h-5" />
          </button>
        </transition>
      </div>
    </div>

    <EmpresasTable
      :customers="paginatedCustomers"
      :selectedIds="selectedIds"
      :selectAll="selectAll"
      :copiedId="copiedId"
      @update:selectedIds="selectedIds = $event"
      @update:selectAll="toggleSelectAll"
      @edit-customer="editCustomer"
      @copy-customer-data="copyCustomerData"
    />

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

  <EditarEmpresasSidebar
    :showEditSidebar="showEditSidebar"
    :editingCompany="editingCompany"
    :templates="templates"
    @close="showEditSidebar = false"
    @update-company="updateCompany"
  />

  <AgregarEmpresasModal
    :showAddModal="showAddModal"
    :templates="templates"
    @close="cancel"
    @add-company="addCompany"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'
import EmpresasTable from '@/components/EmpresasUi/EmpresasTable.vue'
import AgregarEmpresasModal from '@/components/EmpresasUi/AgregarEmpresasModal.vue'
import EditarEmpresasSidebar from '@/components/EmpresasUi/EditarEmpresasSidebar.vue'

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
const showEditSidebar = ref(false)
const editingCompany = ref({ id: null, name: '', rut: '', contact: '', city: '', templateId: DEFAULT_TEMPLATE_ID })
const copiedId = ref(null)

// Plantillas
const templates = ref([
  { id: 1, name: 'Básico', description: 'Acceso limitado a reportes y panel general.' },
  { id: 2, name: 'Profesional', description: 'Incluye reportes y comentarios.' },
  { id: 3, name: 'Avanzado', description: 'Incluye dashboards personalizados y reportes completos.' },
  { id: 4, name: 'Full', description: 'Todas las funciones habilitadas.' }
])

// Validación RUT chileno (formato xx.xxx.xxx-x) - Se mantiene aquí para validar la actualización y adición
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

// Paginar clientes
const paginatedCustomers = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value
  return filteredCustomers.value.slice(start, start + rowsPerPage.value)
})

const totalPages = computed(() => Math.ceil(filteredCustomers.value.length / rowsPerPage.value))

// Select all toggle
const toggleSelectAll = (checked) => {
  selectAll.value = checked
  selectedIds.value = checked ? paginatedCustomers.value.map(c => c.id) : []
}


// Paginación
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const previousPage = () => { if (currentPage.value > 1) currentPage.value-- }

// Cancelar modal - Lógica de reset
const cancel = () => {
  showAddModal.value = false
}

// Agregar empresa con ID único y validación RUT (Emitido desde AgregarEmpresasModal)
const addCompany = (newCompanyData) => {
  if (!isValidRut(newCompanyData.rut)) {
    alert('RUT inválido. Formato esperado: xx.xxx.xxx-x')
    return
  }
  const id = Date.now()
  const createdAt = new Date().toISOString().slice(0, 10)
  customers.value.push({ id, createdAt, ...newCompanyData })
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

// Editar empresa (Llamado desde EmpresasTable)
const editCustomer = (customer) => {
  editingCompany.value = { ...customer }
  if (!editingCompany.value.templateId) editingCompany.value.templateId = DEFAULT_TEMPLATE_ID
  showEditSidebar.value = true
}

// Guardar cambios (Emitido desde EditarEmpresasSidebar)
const updateCompany = (updatedCompany) => {
  if (!isValidRut(updatedCompany.rut)) {
    alert('RUT inválido. Formato esperado: xx.xxx.xxx-x')
    return
  }
  const index = customers.value.findIndex(c => c.id === updatedCompany.id)
  if (index !== -1) customers.value[index] = { ...updatedCompany }
  showEditSidebar.value = false
}


// Watcher: Reset selectAll al cambiar página
watch(paginatedCustomers, () => selectAll.value = false)
watch(rowsPerPage, () => currentPage.value = 1)

</script>

<style scoped>
/* Las transiciones se mantienen aquí si afectan a elementos en este componente (como el botón de eliminar) */
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
/* Las transiciones específicas de los modales se pueden mover a los componentes hijos si solo afectan a ellos. */
</style>