<!-- TelemetriaTable.vue -->
<template>
  <div class="space-y-3">

    <!-- HEADER -->
    <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">
      Telemetría Reciente
    </h3>

    <div class="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
      
      <!-- CABECERA DE TABLA -->
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 text-xs uppercase">
          <tr>
            <th class="px-3 py-2">Hora última actualización</th>
            <th class="px-3 py-2">Clave</th>
            <th class="px-3 py-2">Valor</th>
            <th class="px-3 py-2 w-10"></th>
          </tr>
        </thead>

        <!-- CUERPO -->
        <tbody>
          <tr v-for="(item, index) in data" :key="index"
              class="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition">
            
            <td class="px-3 py-2 text-gray-800 dark:text-gray-200">
              {{ formatDate(item.ts) }}
            </td>

            <td class="px-3 py-2 text-gray-800 dark:text-gray-200">
              {{ item.key }}
            </td>

            <td class="px-3 py-2 text-gray-800 dark:text-gray-200">
              {{ item.value }}
            </td>

            <td class="px-3 py-2 text-right">
              <button @click="$emit('delete', item)"
                      class="text-gray-500 hover:text-red-500 transition">
                <SvgIcon name="trash" class="w-4 h-4" />
              </button>
            </td>
          </tr>

          <!-- SI NO HAY DATOS -->
          <tr v-if="data.length === 0">
            <td colspan="4" class="px-3 py-4 text-center text-gray-500 dark:text-gray-400">
              No hay datos de telemetría disponibles.
            </td>
          </tr>
        </tbody>
      </table>

    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

defineProps({
  data: {
    type: Array,
    default: () => []
  }
});

function formatDate(ts) {
  if (!ts) return "—";
  const d = new Date(ts);
  return d.toLocaleString("es-CL");
}
</script>
