<template>
  <div class="p-2 sm:p-4 w-full flex flex-col">
    <div class="flex flex-col xl:flex-row justify-between items-start xl:items-center mb-4 gap-4">
      
      <div class="flex w-full xl:w-1/2 flex-col sm:flex-row gap-3 sm:gap-4 items-start sm:items-center">
        <div class="flex flex-1 w-full sm:w-auto border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
          <div class="flex items-center justify-center px-3 bg-gray-100 dark:bg-gray-800 text-gray-500">
            <SvgIcon name="search" class="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <input v-model="search" placeholder="Buscar patente..."
            class="flex-1 p-2 text-sm sm:text-base bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-300 focus:outline-none" />
          <button v-if="search" @click="clearSearch"
            class="px-4 bg-[#ff6600] hover:bg-[#e65500] text-white font-semibold text-sm transition">
            Limpiar
          </button>
        </div>

        <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 flex-shrink-0">
          Total de registros: {{ mantenciones.length }}
        </div>
      </div>
      
      <div class="flex gap-3 flex-wrap justify-center sm:justify-start xl:justify-end w-full xl:w-auto">
        
        <div class="mini-kpi kpi-green">
          <div class="flex items-center gap-2">
            <SvgIcon name="ok" class="w-5 h-5" />
            <span class="text-xs font-medium uppercase">Al Día</span>
          </div>
          <span class="text-2xl font-extrabold mt-1">{{ totalVerde }}</span>
        </div>

        <div class="mini-kpi kpi-yellow">
          <div class="flex items-center gap-2">
            <SvgIcon name="proxima" class="w-5 h-5" />
            <span class="text-xs font-medium uppercase">Próximas</span>
          </div>
          <span class="text-2xl font-extrabold mt-1">{{ totalAmarillo }}</span>
        </div>

        <div class="mini-kpi kpi-red">
          <div class="flex items-center gap-2">
            <SvgIcon name="vencida" class="w-5 h-5" />
            <span class="text-xs font-medium uppercase">Vencidas</span>
          </div>
          <span class="text-2xl font-extrabold mt-1">{{ totalRojo }}</span>
        </div>
      </div>
    </div>
    
    <div class="space-y-4 max-h-[500px] overflow-y-auto">
      <div v-for="(item, idx) in paginatedData" :key="idx"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-md p-4 transition duration-200 hover:shadow-lg">

        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">

          <div class="flex-1 min-w-[150px]">
            <p class="text-lg font-bold text-[#102372] dark:text-[#ff6600]">{{ item.patente }}</p>
            <div class="text-sm text-gray-700 dark:text-gray-300 mb-2">
              <span class="text-xs text-gray-500 dark:text-gray-400 mr-1">Odómetro:</span>
              <span class="font-semibold">{{ formatOdometro(item.odometro) }} Km</span>
            </div>
            <div class="mt-2"> 
              <span v-if="item.estado === 'OK'"
                class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-emerald-700 text-xs font-medium shadow-sm">
                <SvgIcon name="ok" class="w-3 h-3" />
                <span>Vehículo al día</span>
              </span>

              <span v-else-if="item.estado === 'Próxima mantención'"
                class="inline-flex items-center gap-1 rounded-full bg-amber-100 px-3 py-1 text-amber-700 text-xs font-medium shadow-sm">
                <SvgIcon name="proxima" class="w-3 h-3" />
                <span>Próximo a Mantención</span>
              </span>

              <span v-else-if="item.estado === 'Requiere mantención'"
                class="inline-flex items-center gap-1 rounded-full bg-red-100 px-3 py-1 text-red-700 text-xs font-medium shadow-sm">
                <SvgIcon name="vencida" class="w-3 h-3" />
                <span>Mantención vencida</span>
              </span>
            </div>
          </div>
          
          <div class="flex flex-col items-center justify-center flex-shrink-0 w-full md:w-auto mt-4 md:mt-0">
            <img v-if="item.estado === 'OK'" src="https://sinergygroup.cl/Mantenciones/img/verde.png" alt="OK"
              class="w-16 h-auto object-contain" />
            <img v-else-if="item.estado === 'Próxima mantención'" src="https://sinergygroup.cl/Mantenciones/img/amarillo.png"
              alt="Próxima mantención" class="w-16 h-auto object-contain" />
            <img v-else-if="item.estado === 'Requiere mantención'" src="https://sinergygroup.cl/Mantenciones/img/rojo.png"
              alt="Mantención vencida" class="w-16 h-auto object-contain" />
            <span v-else class="text-gray-500 text-xs mt-2">{{ item.estado }}</span>
          </div>

          <div class="flex gap-3 pt-2 w-full md:w-auto md:flex-col justify-end flex-shrink-0">
            <button @click="$emit('ver-mantenciones', item)"
              class="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition">
              <SvgIcon name="eye" class="w-4 h-4" /> <span class="md:hidden lg:inline">Ver Historial</span>
            </button>

            <button @click="$emit('agregar-mantencion', item)"
              class="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded bg-[#ff6600] hover:bg-[#e65500] text-white text-xs font-medium transition">
              <SvgIcon name="plus" class="w-4 h-4" /> <span class="md:hidden lg:inline">Agregar Mantencion</span>
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredData.length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">
        No hay registros de mantenciones
      </div>
    </div>


    <div
      class="flex flex-col sm:flex-row justify-between items-center mt-4 text-xs sm:text-sm text-gray-700 dark:text-gray-300 gap-2 bg-[#f3f3f3] dark:bg-gray-800 p-2 rounded-md shadow-sm">
      <div class="flex items-center gap-2">
        <label for="rowsPerPage" class="text-xs">Filas por página:</label>
        <select id="rowsPerPage" v-model.number="rowsPerPage"
          class="border dark:border-gray-600 rounded px-2 py-1 text-xs sm:text-sm bg-white dark:bg-gray-700">
          <option v-for="n in [5, 10, 25, 50, 100]" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>

      <div class="flex items-center gap-1 sm:gap-2">
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1"
          class="px-2 py-1 rounded border border-gray-400 dark:border-gray-600 disabled:opacity-40 hover:bg-[#ff6600] hover:text-white transition">
          <SvgIcon name="chevron-left" class="w-4 h-4" />
        </button>

        <span class="px-2">Página {{ currentPage }} / {{ totalPages }}</span>

        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages"
          class="px-2 py-1 rounded border border-gray-400 dark:border-gray-600 disabled:opacity-40 hover:bg-[#ff6600] hover:text-white transition">
          <SvgIcon name="chevron-right" class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

### Script (Logic)

```javascript
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
    };
  },
  computed: {
    filteredData() {
      if (!this.debouncedSearch) return this.mantenciones;
      return this.mantenciones.filter((item) =>
        item.patente.toLowerCase().includes(this.debouncedSearch)
      );
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
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) this.currentPage = page;
    },
    formatOdometro(valor) {
      const num = parseFloat(valor);
      return isNaN(num) ? '0.00' : num.toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    clearSearch() {
      this.search = "";
      this.debouncedSearch = "";
    },
  },
};
</script>

### Style (CSS)

```css
<style scoped>
.mini-kpi {
  /* Estilo Sutil: Eliminamos sombra y borde. Usamos un padding más pequeño. */
  @apply flex flex-col items-center justify-center 
         rounded-lg px-4 py-2 
         text-center 
         transition duration-200; /* Transición suave sin el hover:shadow-xl */
  min-width: 90px; 
}

/* Colores de Fondo y Texto Sutiles, basados en la paleta de alertas */
.kpi-green {
  /* Fondo muy claro, borde suave (opcional), texto del color primario */
  @apply bg-emerald-50 dark:bg-gray-700 border border-emerald-200 dark:border-emerald-600 text-emerald-700 dark:text-emerald-400;
}

.kpi-yellow {
  @apply bg-amber-50 dark:bg-gray-700 border border-amber-200 dark:border-amber-600 text-amber-700 dark:text-amber-400;
}

.kpi-red {
  @apply bg-red-50 dark:bg-gray-700 border border-red-200 dark:border-red-600 text-red-700 dark:text-red-400;
}
</style>