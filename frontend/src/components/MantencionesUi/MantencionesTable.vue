<template>
  <div class="p-2 sm:p-4 w-full flex flex-col">
    <div class="flex flex-col xl:flex-row justify-between items-start xl:items-center mb-4 gap-4">

      <div class="flex w-full xl:w-1/2 flex-col sm:flex-row gap-3 sm:gap-4 items-start sm:items-center">
        <div
          class="flex flex-1 w-full sm:w-auto border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden shadow-inner">
          <div class="flex items-center justify-center px-3 bg-gray-100 dark:bg-gray-800 text-gray-500">
            <SvgIcon name="search" class="w-4 h-4" />
          </div>
          <input v-model="search" placeholder="Buscar patente..." title="Busca una patente"
            class="flex-1 p-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-300 focus:outline-none focus:ring-1 focus:ring-[#ff6600]" />
          <button v-if="search" @click="clearSearch"
            class="px-3 bg-[#ff6600] hover:bg-[#e65500] text-white font-semibold text-xs transition duration-150 ease-in-out">
            Limpiar
          </button>
        </div>

        <div
          class="flex items-center gap-4 text-xs w-full justify-between sm:w-auto sm:justify-start xl:justify-between xl:flex-1">
          <!-- Total de vehículos -->
          <div class="text-gray-600 dark:text-gray-300 flex-shrink-0">
            Total de vehículos: <span class="font-bold ml-1">{{ mantenciones.length }}</span>
          </div>

          <div class="flex justify-end xl:flex-1">
            <button @click="toggleSort" title="Alternar Orden" :class="[
              'flex items-center justify-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition duration-300 ease-in-out shadow-sm hover:shadow-md border whitespace-nowrap w-[200px]',
              sortIndex === 0 ? 'bg-green-600 text-white border-green-700 hover:bg-green-700' :
                sortIndex === 1 ? 'bg-[#ecb404] text-white border-yellow-500 hover:bg-yellow-600' :
                  'bg-red-600 text-white border-red-700 hover:bg-red-700'
            ]">
              <span>Ordenar por: {{ priorityOrders[sortIndex][0] }}</span>
            </button>
          </div>

        </div>

      </div>

      <div class="flex gap-2 flex-wrap justify-center sm:justify-start xl:justify-end w-full xl:w-auto">
        
        <button @click="setFilter('OK')" :class="[
          'mini-kpi kpi-green cursor-pointer',
          activeFilter === 'OK' ? 'ring-2 ring-offset-1 ring-emerald-500/80 shadow-xl' : ''
        ]">
          <span class="text-xs font-medium uppercase text-gray-600 dark:text-gray-300">Al Día</span>
          <span class="text-xl font-extrabold mt-1">{{ totalVerde }}</span>
        </button>

        <button @click="setFilter('Próxima mantención')" :class="[
          'mini-kpi kpi-yellow cursor-pointer',
          activeFilter === 'Próxima mantención' ? 'ring-2 ring-offset-1 ring-amber-500/80 shadow-xl' : ''
        ]">
          <span class="text-xs font-medium uppercase text-gray-600 dark:text-gray-300">Próximas</span>
          <span class="text-xl font-extrabold mt-1">{{ totalAmarillo }}</span>
        </button>

        <button @click="setFilter('Requiere mantención')" :class="[
          'mini-kpi kpi-red cursor-pointer',
          activeFilter === 'Requiere mantención' ? 'ring-2 ring-offset-1 ring-red-500/80 shadow-xl' : ''
        ]">
          <span class="text-xs font-medium uppercase text-gray-600 dark:text-gray-300">Vencidas</span>
          <span class="text-xl font-extrabold mt-1">{{ totalRojo }}</span>
        </button>

      </div>
    </div>

    <div class="space-y-2 max-h-[500px] overflow-y-auto pr-1">
      <div v-for="(item, idx) in paginatedData" :key="idx"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-md p-3 transition duration-300 hover:shadow-lg hover:ring-2 hover:ring-[#ff6600]/50 hover:scale-[1.005]">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">

          <div class="flex-1 flex items-center gap-4">
            <div class="flex-shrink-0">
              <img v-if="item.estado === 'OK'" src="https://sinergygroup.cl/Mantenciones/img/verde.png" alt="Al Día"
                class="w-8 h-auto object-contain" />
              <img v-else-if="item.estado === 'Próxima mantención'"
                src="https://sinergygroup.cl/Mantenciones/img/amarillo.png" alt="Próxima mantención"
                class="w-8 h-auto object-contain" />
              <img v-else-if="item.estado === 'Requiere mantención'"
                src="https://sinergygroup.cl/Mantenciones/img/rojo.png" alt="Mantención vencida"
                class="w-8 h-auto object-contain" />
            </div>

            <div class="flex flex-col items-center justify-center text-center w-28 h-8">
              <p class="text-sm font-extrabold text-[#102372] dark:text-[#ff6600] leading-tight">
                {{ item.patente }}
              </p>
              <div class="text-[10px] text-gray-500 dark:text-gray-400">
                <span class="uppercase font-medium">Odómetro:<br></span>
                <span class="font-bold text-gray-700 dark:text-gray-200">
                  {{ formatOdometro(item.odometro) }} Km
                </span>
              </div>
            </div>

            <div class="hidden md:flex items-center justify-center flex-shrink-0 ml-auto self-center h-full">
              <span v-if="item.estado === 'OK'"
                class="inline-flex items-center justify-center gap-1 rounded-full bg-emerald-100 dark:bg-emerald-900 px-2.5 py-0.5 text-emerald-700 dark:text-emerald-300 text-xs font-medium border border-emerald-300 dark:border-emerald-600 w-28 h-8 text-center">
                <SvgIcon name="ok" class="w-3 h-3" />
                <span>Al día</span>
              </span>

              <span v-else-if="item.estado === 'Próxima mantención'"
                class="inline-flex items-center justify-center gap-1 rounded-full bg-amber-100 dark:bg-amber-900 px-2.5 py-0.5 text-amber-700 dark:text-amber-300 text-xs font-medium border border-amber-300 dark:border-amber-600 w-28 h-8 text-center">
                <SvgIcon name="proxima" class="w-3 h-3" />
                <span>Próximo</span>
              </span>

              <span v-else-if="item.estado === 'Requiere mantención'"
                class="inline-flex items-center justify-center gap-1 rounded-full bg-red-100 dark:bg-red-900 px-2.5 py-0.5 text-red-700 dark:text-red-300 text-xs font-medium border border-red-300 dark:border-red-600 w-28 h-8 text-center">
                <SvgIcon name="vencida" class="w-3 h-3" />
                <span>Vencida</span>
              </span>
            </div>
          </div>



          <div class="flex gap-2 pt-2 sm:pt-0 w-full sm:w-auto flex-shrink-0">
            <button @click="$emit('ver-mantenciones', item)"
              class="flex-1 sm:flex-none flex items-center justify-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition duration-150 shadow-sm hover:shadow-md">
              <SvgIcon name="eye" class="w-3 h-3" /> <span class="hidden sm:inline">Ver</span>
              <span class="sm:hidden">Ver</span>
            </button>

            <button @click="$emit('agregar-mantencion', item)"
              class="flex-1 sm:flex-none flex items-center justify-center gap-1 px-3 py-1.5 rounded-lg bg-[#ff6600] hover:bg-[#e65500] text-white text-xs font-medium transition duration-150 shadow-sm hover:shadow-md">
              <SvgIcon name="plus" class="w-3 h-3" /> <span class="hidden sm:inline">Agregar</span>
              <span class="sm:hidden">Nuevo</span>
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredData.length === 0"
        class="text-center py-6 text-gray-500 dark:text-gray-400 border border-dashed rounded-lg">
        No se encontraron vehículos que coincidan con la búsqueda.
      </div>
    </div>


    <div
      class="flex flex-col sm:flex-row justify-between items-center mt-3 text-xs text-gray-700 dark:text-gray-300 gap-2 bg-[#f3f3f3] dark:bg-gray-800 p-2 rounded-lg shadow-inner border border-gray-200 dark:border-gray-700">
      <div class="flex items-center gap-2">
        <label for="rowsPerPage" class="text-xs font-medium">Mostrar:</label>
        <select id="rowsPerPage" v-model.number="rowsPerPage"
          class="border dark:border-gray-600 rounded-md px-2 py-1 text-xs bg-white dark:bg-gray-700 focus:ring-1 focus:ring-[#ff6600]">
          <option v-for="n in [5, 10, 25, 50, 100]" :key="n" :value="n">{{ n }}</option>
        </select>
        <span class="text-gray-500 dark:text-gray-400">registros por página</span>
      </div>

      <div class="flex items-center gap-1 sm:gap-2">
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1"
          class="flex items-center justify-center w-6 h-6 rounded-full border border-gray-400 dark:border-gray-600 disabled:opacity-40 hover:bg-[#ff6600] hover:text-white transition duration-150 ease-in-out"
          aria-label="Página anterior">
          <SvgIcon name="chevron-left" class="w-3 h-3" />
        </button>

        <span class="px-1 font-medium">Página {{ currentPage }} de {{ totalPages }}</span>

        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages"
          class="flex items-center justify-center w-6 h-6 rounded-full border border-gray-400 dark:border-gray-600 disabled:opacity-40 hover:bg-[#ff6600] hover:text-white transition duration-150 ease-in-out"
          aria-label="Página siguiente">
          <SvgIcon name="chevron-right" class="w-3 h-3" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import SvgIcon from '@/components/icons/SvgIcon.vue'

export default {
  name: "MantencionesCards",
  components: { SvgIcon },
  props: { mantenciones: { type: Array, default: () => [] } },
  data() {
    return {
      search: "",
      debouncedSearch: "",
      currentPage: 1,
      rowsPerPage: 5,
      sortIndex: 0,
      activeFilter: null,
      priorityOrders: [
        ['Al día', 'Próxima mantención', 'Requiere mantención'],
        ['Próxima mantención', 'Requiere mantención', 'OK'],
        ['Requiere mantención', 'OK', 'Próxima mantención']
      ],
    };
  },
  computed: {
    filteredData() {
      let data = this.mantenciones;

      // Filtrar por búsqueda
      if (this.debouncedSearch) {
        data = data.filter(item =>
          item.patente.toLowerCase().includes(this.debouncedSearch)
        );
      }


      if (this.activeFilter) {
        data = data.filter(item => item.estado === this.activeFilter);
      }

      const currentOrder = this.priorityOrders[this.sortIndex];
      data = [...data].sort((a, b) => {
        const aIndex = currentOrder.indexOf(a.estado);
        const bIndex = currentOrder.indexOf(b.estado);
        return aIndex - bIndex;
      });

      return data;
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredData.length / this.rowsPerPage));
    },
    paginatedData() {
      const start = (this.currentPage - 1) * this.rowsPerPage;
      return this.filteredData.slice(start, start + this.rowsPerPage);
    },
    totalVerde() {
      return this.mantenciones.filter(m => m.estado === 'OK').length;
    },
    totalAmarillo() {
      return this.mantenciones.filter(m => m.estado === 'Próxima mantención').length;
    },
    totalRojo() {
      return this.mantenciones.filter(m => m.estado === 'Requiere mantención').length;
    }
  },
  watch: {
    search(val) {
      clearTimeout(this._debounceTimeout);
      this._debounceTimeout = setTimeout(() => {
        this.debouncedSearch = val.trim().toLowerCase();
        this.currentPage = 1;
      }, 300);
    },
    filteredData() {
      if (this.currentPage > this.totalPages) {
        this.currentPage = 1;
      }
    }
  },
  methods: {
    toggleSort() {
      this.sortIndex = (this.sortIndex + 1) % this.priorityOrders.length;
      this.currentPage = 1; // reinicia la paginación
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) this.currentPage = page;
    },
    formatOdometro(valor) {
      // Formato con separador de miles y dos decimales (ej. 10.000,00)
      const num = parseFloat(valor);
      return isNaN(num) ? '0.00' : num.toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    clearSearch() {
      this.search = "";
      this.debouncedSearch = "";
    },
    setFilter(estado) {
      this.activeFilter = this.activeFilter === estado ? null : estado;

      this.search = "";
      this.debouncedSearch = "";
      this.currentPage = 1;
    },
  },
};
</script>

<style scoped>
.mini-kpi {
  /* Estilo Compacto: Menos padding y fuentes más pequeñas */
  @apply flex flex-col items-center justify-center rounded-lg px-3 py-2
  /* Reducido de px-4 py-3 */
  text-center transition duration-200 ease-in-out shadow-inner;
  min-width: 75px;
  /* Reducido de 90px */
}

/* Colores de Fondo y Texto Sutiles, más profesionales */
.kpi-green {
  @apply bg-emerald-50 dark:bg-gray-700 border border-emerald-300 dark:border-emerald-700 text-emerald-800 dark:text-emerald-300;
}

.kpi-yellow {
  @apply bg-amber-50 dark:bg-gray-700 border border-amber-300 dark:border-amber-700 text-amber-800 dark:text-amber-300;
}

.kpi-red {
  @apply bg-red-50 dark:bg-gray-700 border border-red-300 dark:border-red-700 text-red-800 dark:text-red-300;
}
</style>