<template>
  <div class="flex flex-col  p-4">
    <!-- Navbar -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-gray-700 pb-2">
      <div class="w-full sm:flex-1">
        <input v-model="searchTerm" type="text" placeholder="Buscar empresa..."
          class="w-full px-3 py-1  text-gray-900 focus:outline-none focus:ring focus:ring-gray-500" />
      </div>
      <div class="w-full sm:w-auto mt-2 sm:mt-0">
        <a href="#_" @click.prevent="showAddModal = true"
          class="relative inline-flex w-full sm:w-auto items-center justify-center px-3 py-2 overflow-hidden font-mono font-medium tracking-tighter text-white bg-gray-800 rounded-lg group">
          <span
            class="absolute w-0 h-0 transition-all duration-500 ease-out bg-[#ff6600] rounded-full group-hover:w-56 group-hover:h-56"></span>
          <span
            class="absolute inset-0 w-full h-full -mt-1 rounded-lg opacity-30 bg-gradient-to-b from-transparent via-transparent to-gray-700"></span>
          <span class="relative">➕ Agregar Empresa</span>
        </a>


      </div>
    </div>



    <!-- 📊 Contenedor de tabla (altura fija) -->
    <div class="flex-1 mt-4 flex flex-col">
      <div class="overflow-y-auto min-h-[400px] max-h-[400px] rounded-lg shadow flex-1">
        <table class="min-w-full bg-gray-800 text-white">
          <thead>
            <tr class="bg-[#102372] text-left">
              <!-- Checkbox global + botón eliminar todos -->
              <th class="py-2 px-4 w-1/12 flex items-center gap-1" title="Seleccionar todo">
                <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
                <button @click="deleteSelected"
                  class="bg-red-600 hover:bg-red-700 text-white p-1 rounded w-6 h-6 flex items-center justify-center"
                  :disabled="selectedIds.length === 0" title="Eliminar seleccionados">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    stroke-width="2" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M10 3h4a1 1 0 011 1v1H9V4a1 1 0 011-1z" />
                  </svg>
                </button>
              </th>
              <th class="py-2 px-4">Fecha de Creación</th>
              <th class="py-2 px-4">Nombre</th>
              <th class="py-2 px-4">Rut</th>
              <th class="py-2 px-4">Contacto</th>
              <th class="py-2 px-4">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in paginatedCustomers" :key="customer.id"
              class="border-t border-gray-700 hover:bg-gray-700 transition">
              <td class="py-2 px-4">
                <input type="checkbox" v-model="selectedIds" :value="customer.id" />
              </td>
              <td class="py-2 px-4">{{ customer.createdAt }}</td>
              <td class="py-2 px-4">{{ customer.name }}</td>
              <td class="py-2 px-4">{{ customer.rut }}</td>
              <td class="py-2 px-4">{{ customer.contact }}</td>
              <td class="py-2 px-4 flex gap-2">
                <!-- Editar -->
                <button @click="editCustomer(customer)" title="Editar"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round"
                      d="M11 5H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5" />
                    <path stroke-linecap="round" stroke-linejoin="round"
                      d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                  </svg>
                </button>

                <!-- Copiar -->
                <button @click="copyCustomerData(customer)" title="Copiar"
                  class="px-2 py-1 bg-gray-800 text-white rounded hover:bg-gray-700 relative flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                    stroke="currentColor" class="w-5 h-5">
                    <path stroke-linecap="round" stroke-linejoin="round"
                      d="M8 16H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 8h8v8a2 2 0 0 1-2 2H8V8z" />
                  </svg>
                </button>

                <!-- Eliminar fila -->
                <button @click="deleteCustomer(customer.id)" 
                  class="bg-red-600 hover:bg-red-700 text-white p-1 rounded w-6 h-6 flex items-center justify-center"
                  title="Eliminar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    stroke-width="2" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M10 3h4a1 1 0 011 1v1H9V4a1 1 0 011-1z" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>

        </table>
      </div>

      <!-- 📌 Footer de paginación -->
      <div
        class="bg-gray-900 text-gray-300 p-4 rounded-b-lg shadow-inner flex flex-col sm:flex-row sm:justify-between items-center gap-4">

        <!-- Filas por página -->
        <div class="flex items-center gap-2">
          <span>Filas por página:</span>
          <select v-model="rowsPerPage" class="bg-gray-800 text-white rounded px-2 py-1 focus:outline-none">
            <option v-for="option in rowsPerPageOptions" :key="option" :value="option">{{ option }}</option>
          </select>
        </div>

        <!-- Paginación numérica -->
        <ul class="flex justify-center gap-1 text-gray-300">
          <!-- Anterior -->
          <li>
            <button @click="previousPage" :disabled="currentPage === 1"
              class="grid w-8 h-8 place-content-center rounded border border-gray-700 transition-colors hover:bg-gray-700 disabled:opacity-50"
              aria-label="Previous page">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd"
                  d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                  clip-rule="evenodd" />
              </svg>
            </button>
          </li>

          <!-- Números de página -->
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

          <!-- Siguiente -->
          <li>
            <button @click="nextPage" :disabled="currentPage === totalPages"
              class="grid w-8 h-8 place-content-center rounded border border-gray-700 transition-colors hover:bg-gray-700 disabled:opacity-50"
              aria-label="Next page">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clip-rule="evenodd" />
              </svg>
            </button>
          </li>
        </ul>
      </div>

    </div>
  </div>
  <!-- Modal -->
  <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div
      class="bg-gray-800 text-white rounded-lg relative flex flex-col w-full sm:w-full max-w-xs sm:max-w-md md:max-w-lg h-full px-10 sm:h-5/6 py-4 sm:py-6">

      <!-- Botón cerrar -->
      <button @click="showAddModal = false"
        class="absolute top-2 right-2 text-gray-400 hover:text-white text-2xl">&times;</button>

      <h2 class="text-xl sm:text-2xl font-bold mb-4 text-center">Agregar Empresa</h2>
      <span class="flex items-center">
        <span class="h-px flex-1 bg-gray-600"></span>
      </span>

      <!-- Formulario -->
      <form @submit.prevent="addCompany" class="flex-1 flex flex-col gap-2 py-10 px-4  overflow-y-auto">
        <!-- Texto instructivo -->
        <p class="text-gray-300 mb-2">Ingrese el nombre de la empresa:</p>

        <input v-model="newCompany.name" type="text" placeholder="Nombre"
          class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />
        <p class="text-gray-300 mb-2">Ingrese el rut de la empresa:</p>
        <input v-model="newCompany.rut" type="text" placeholder="12.630.254-K"
          class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />
        <p class="text-gray-300 mb-2">Ingrese contacto de la empresa:</p>
        <input v-model="newCompany.contact" type="text" placeholder="Contacto"
          class="px-3 py-2 rounded bg-gray-700 text-white focus:outline-none w-full" required />

        <button type="submit"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded mt-auto w-full sm:w-auto self-center">Agregar</button>
      </form>

    </div>
  </div>


</template>

<script setup>
import { ref, computed, watch } from 'vue'


// 🧑‍💼 Datos de ejemplo
const customers = ref([
  { id: 1, createdAt: '2025-10-10', name: 'Juan Pérez', rut: '12.345.678-9', contact: '+56 9 1234 5678' },
  { id: 2, createdAt: '2025-10-11', name: 'Ana López', rut: '98.765.432-1', contact: '+54 9 1111 2222' },
  { id: 3, createdAt: '2025-10-12', name: 'Pedro Gómez', rut: '11.111.111-1', contact: '+56 9 3333 4444' },
  { id: 4, createdAt: '2025-10-13', name: 'María Torres', rut: '22.222.222-2', contact: '+54 9 5555 6666' },
  { id: 5, createdAt: '2025-10-14', name: 'Luis Fernández', rut: '33.333.333-3', contact: '+56 9 7777 8888' },
  { id: 6, createdAt: '2025-10-15', name: 'Carla Ruiz', rut: '44.444.444-4', contact: '+54 9 9999 0000' },
  { id: 7, createdAt: '2025-10-16', name: 'Diego Soto', rut: '55.555.555-5', contact: '+56 9 1212 3434' },
  { id: 8, createdAt: '2025-10-17', name: 'Paula Vargas', rut: '66.666.666-6', contact: '+54 9 5656 7878' },
  { id: 9, createdAt: '2025-10-18', name: 'Tomás Rojas', rut: '77.777.777-7', contact: '+56 9 9090 1234' },
  { id: 10, createdAt: '2025-10-19', name: 'Valentina Pino', rut: '88.888.888-8', contact: '+54 9 4567 8901' },
])


// 🔍 Búsqueda
const searchTerm = ref('')
const selectedIds = ref([])   // IDs seleccionados
const selectAll = ref(false)  // Checkbox del header

// 📄 Paginación
const rowsPerPageOptions = [5, 10, 20, 50]
const rowsPerPage = ref(5)
const currentPage = ref(1)

const showAddModal = ref(false)

const newCompany = ref({
  name: '',
  rut: '',
  contact: ''
})
const addCompany = () => {
  if (!newCompany.value.name || !newCompany.value.rut || !newCompany.value.contact) return
  const id = customers.value.length + 1
  const createdAt = new Date().toISOString().slice(0, 10)
  customers.value.push({ id, createdAt, ...newCompany.value })
  newCompany.value = { name: '', rut: '', contact: '' }
  showAddModal.value = false
}
const deleteCustomer = (id) => {
  customers.value = customers.value.filter(c => c.id !== id)
  selectedIds.value = selectedIds.value.filter(sel => sel !== id)
}

const deleteSelected = () => {
  customers.value = customers.value.filter(c => !selectedIds.value.includes(c.id))
  selectedIds.value = []
}

const filteredCustomers = computed(() => {
  if (!searchTerm.value) return customers.value
  return customers.value.filter((c) =>
    c.name.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})
const copiedId = ref(null)
const copyCustomerData = (customer) => {
  const data = `Nombre: ${customer.name}\nRUT: ${customer.rut}\nContacto: ${customer.contact}`
  navigator.clipboard.writeText(data)
    .then(() => {
      copiedId.value = customer.id
      setTimeout(() => copiedId.value = null, 1000) // desaparece después de 1s
    })
    .catch(err => console.error('Error al copiar:', err))
}
const editCustomer = (customer) => {
  console.log('Editar cliente:', customer)
  // Aquí puedes abrir un modal o redirigir a otra página para editar
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedIds.value = paginatedCustomers.value.map(c => c.id)
  } else {
    selectedIds.value = []
  }
}

const totalPages = computed(() =>
  Math.ceil(filteredCustomers.value.length / rowsPerPage.value)
)

const paginatedCustomers = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value
  return filteredCustomers.value.slice(start, start + rowsPerPage.value)
})

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const previousPage = () => {
  if (currentPage.value > 1) currentPage.value--
}
watch(paginatedCustomers, () => {
  selectAll.value = false
})
</script>

<style scoped>
/* Puedes personalizar estilos si quieres */
</style>
