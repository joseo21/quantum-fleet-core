<template>
  <div class="p-2 sm:p-2 w-full flex flex-col">
    <!-- 🔍 Barra de búsqueda + KPIs -->
    <div class="flex flex-col sm:flex-row justify-between items-center mb-4 gap-3">
      <!-- 🟠 Barra de búsqueda -->
      <div class="flex w-full sm:w-2/3 md:w-1/2">
        <div class="flex w-full border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
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
      </div>

      <!-- 🟢 Pequeños KPIs -->
      <div class="flex gap-2">
        <div class="mini-kpi kpi-green">
          <span class="text-xs font-medium">Mantención al Día</span>
          <span class="font-bold text-sm">{{ totalVerde }}</span>
        </div>

        <div class="mini-kpi kpi-yellow">
          <span class="text-xs font-medium">Proximo a Mantención</span>
          <span class="font-bold text-sm">{{ totalAmarillo }}</span>
        </div>

        <div class="mini-kpi kpi-red">
          <span class="text-xs font-medium">Mantención Vencida</span>
          <span class="font-bold text-sm">{{ totalRojo }}</span>
        </div>
      </div>
    </div>

    <!-- 📋 Tabla con scroll -->
    <div class="border border-gray-300 dark:border-gray-700 rounded-lg shadow-sm overflow-y-auto max-h-[500px]">
      <table class="min-w-full text-xs sm:text-sm md:text-base text-center border-collapse">
        <thead class="bg-[#102372] dark:bg-[#102372] sticky top-0 z-10 text-gray-100">
          <tr>
            <th v-for="col in columns" :key="col"
              class="font-semibold py-2 px-3 border-b border-gray-300 dark:border-gray-600">
              {{ col }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(item, idx) in paginatedData" :key="idx"
            class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b dark:border-gray-600">
            <td class="py-2 px-3">{{ item.patente }}</td>
            <td class="py-2 px-3">{{ formatOdometro(item.odometro) }}</td>
            <td class="py-2 px-3 text-center">
              <div class="flex flex-col items-center justify-center gap-2">
                <!-- Imagen -->
                <img v-if="item.estado === 'OK'" src="https://sinergygroup.cl/Mantenciones/img/verde.png" alt="OK"
                  class="w-24 sm:w-28 md:w-32 h-auto object-contain" />
                <img v-else-if="item.estado === 'Próxima mantención'"
                  src="https://sinergygroup.cl/Mantenciones/img/amarillo.png" alt="Próxima mantención"
                  class="w-24 sm:w-28 md:w-32 h-auto object-contain" />
                <img v-else-if="item.estado === 'Requiere mantención'"
                  src="https://sinergygroup.cl/Mantenciones/img/rojo.png" alt="Mantención vencida"
                  class="w-24 sm:w-28 md:w-32 h-auto object-contain" />

                <!-- Etiquetas tipo badge -->
                <span v-if="item.estado === 'OK'"
                  class="inline-flex items-center gap-1 sm:gap-2 justify-center rounded-full bg-emerald-100 px-3 py-1 text-emerald-700 text-xs sm:text-sm font-medium">
                  <SvgIcon name="ok" class="w-4 h-4 sm:w-5 sm:h-5" />
                  <span>Vehículo al día</span>
                </span>

                <span v-else-if="item.estado === 'Próxima mantención'"
                  class="inline-flex items-center gap-1 sm:gap-2 justify-center rounded-full bg-amber-100 px-3 py-1 text-amber-700 text-xs sm:text-sm font-medium">
                  <SvgIcon name="proxima" class="w-4 h-4 sm:w-5 sm:h-5" />
                  <span>Proximo a Mantención</span>
                </span>

                <span v-else-if="item.estado === 'Requiere mantención'"
                  class="inline-flex items-center gap-1 sm:gap-2 justify-center rounded-full bg-red-100 px-3 py-1 text-red-700 text-xs sm:text-sm font-medium">
                  <SvgIcon name="vencida" class="w-4 h-4 sm:w-5 sm:h-5" />
                  <span>Mantención vencida</span>
                </span>

                <span v-else class="text-gray-500 text-xs">{{ item.estado }}</span>
              </div>
            </td>

            <td class="py-2 px-3">
              <button @click="$emit('ver-mantenciones', item)"
                class="flex items-center justify-center gap-1 sm:gap-2 mx-auto px-2 sm:px-6 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-medium transition">
                <SvgIcon name="eye" class="w-4 h-4 sm:w-5 sm:h-5" />
                <span class="hidden sm:inline">Ver</span>
              </button>
            </td>
            <td class="py-2 px-3">
              <button @click="$emit('agregar-mantencion', item)"
                class="flex items-center justify-center gap-1 sm:gap-2 mx-auto px-2 sm:px-6 py-2 rounded bg-[#ff6600] hover:bg-[#e65500] text-white text-xs sm:text-sm font-medium transition">
                <SvgIcon name="plus" class="w-4 h-4 sm:w-5 sm:h-5" />
                <span class="hidden sm:inline">Agregar</span>
              </button>

            </td>
          </tr>

          <tr v-if="filteredData.length === 0">
            <td colspan="5" class="text-center py-4 text-gray-500 dark:text-gray-400">
              No hay registros de mantenciones
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 📑 Controles de paginación -->
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

<script>
import SvgIcon from '@/components/icons/SvgIcon.vue'

export default {
  name: "MantencionesTable",
  components: { SvgIcon },
  props: { mantenciones: { type: Array, default: () => [] } },
  data() {
    return {
      search: "",
      debouncedSearch: "",
      currentPage: 1,
      rowsPerPage: 5,
      columns: [
        "Patente",
        "Odómetro (Km)",
        "Estado de mantención",
        "Ver Mantenciones",
        "Agregar Mantención",
      ],
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
  },
  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) this.currentPage = page;
    },
    formatOdometro(valor) {
      const num = parseFloat(valor);
      return isNaN(num) ? '0.00' : num.toFixed(2);
    },
    clearSearch() {
      this.search = "";
      this.debouncedSearch = "";
    },
  },
};
</script>

<style scoped>
.mini-kpi {
  @apply flex flex-col items-center justify-center rounded-md px-9 py-5 border text-center shadow-sm;
  min-width: 60px;
}

.kpi-green {
  @apply bg-green-50 border-green-200 text-green-700;
}

.kpi-yellow {
  @apply bg-yellow-50 border-yellow-200 text-yellow-700;
}

.kpi-red {
  @apply bg-red-50 border-red-200 text-red-700;
}
</style>
