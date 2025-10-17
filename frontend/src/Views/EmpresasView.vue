<template>
  <div class="flex flex-col  p-4">
    <!-- Navbar -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-gray-700 pb-2">
      <div class="w-full sm:flex-1">
        <input v-model="searchTerm" type="text" placeholder="Buscar empresa..."
          class="w-full px-3 py-1  text-gray-900 focus:outline-none focus:ring focus:ring-gray-500" />
      </div>
      <div class="w-full sm:w-auto mt-2 sm:mt-0">
        <a href="#_"
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
            <tr class="bg-gray-700 text-left">
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
              <td class="py-2 px-4">{{ customer.createdAt }}</td>
              <td class="py-2 px-4">{{ customer.name }}</td>
              <td class="py-2 px-4">{{ customer.rut }}</td>
              <td class="py-2 px-4">{{ customer.contact }}</td>
              <td class="py-2 px-4">
                <button class="text-blue-400 hover:text-blue-600">Editar</button>
                <button class="text-red-400 hover:text-red-600 ml-2">Eliminar</button>
              </td>
            </tr>
            <tr v-if="paginatedCustomers.length === 0">
              <td colspan="5" class="text-center py-4 text-gray-400">No se encontraron resultados</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 📌 Footer de paginación siempre visible debajo -->
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
</template>

<script setup>
import { ref, computed } from 'vue'

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

// 📄 Paginación
const rowsPerPageOptions = [5, 10, 20, 50]
const rowsPerPage = ref(5)
const currentPage = ref(1)

const filteredCustomers = computed(() => {
  if (!searchTerm.value) return customers.value
  return customers.value.filter((c) =>
    c.name.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

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
</script>

<style scoped>
/* Puedes personalizar estilos si quieres */
</style>
