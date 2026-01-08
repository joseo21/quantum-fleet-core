<template>
  <div class="space-y-4">

    <!-- HEADER + BOTÓN -->
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
        <SvgIcon name="signal" class="w-4 h-4 text-[#102372] dark:text-[#ff6600]" />
        Telemetría Reciente
      </h3>

      <button
        @click="showScriptModal = true"
        class="px-3 py-1.5 text-sm rounded-lg
               bg-[#102372] hover:bg-[#102372]/90
               dark:bg-[#ff6600] dark:hover:bg-[#ff6600]/90
               text-white transition"
      >
        Insertar script
      </button>
    </div>

    <div class="rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">

      <!-- CABECERA -->
      <div class="bg-[#102372] dark:bg-[#ff6600] text-white text-xs uppercase font-semibold tracking-wide">
        <div class="grid grid-cols-[1.2fr_1fr_1fr_0.4fr] px-4 py-3">
          <span>Hora actualización</span>
          <span>Clave</span>
          <span>Valor</span>
          <span class="text-right">Acciones</span>
        </div>
      </div>

      <!-- CONTENEDOR -->
      <div
        class="divide-y divide-gray-200 dark:divide-gray-700 overflow-y-auto"
        style="max-height: 250px;"
      >
        <div
          v-for="(item, index) in visibleData"
          :key="index"
          class="grid grid-cols-[1.2fr_1fr_1fr_0.4fr] px-4 py-3 text-sm
                 text-gray-800 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
        >
          <span class="truncate">{{ formatDate(item.ts) }}</span>
          <span class="font-medium truncate">{{ item.key }}</span>
          <span class="truncate">{{ item.value }}</span>

          <span class="text-right">
            <button
              @click="$emit('delete', item)"
              class="p-1 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 transition"
            >
              <SvgIcon name="trash" class="w-4 h-4" />
            </button>
          </span>
        </div>

        <div
          v-if="data.length === 0"
          class="px-4 py-6 text-center text-gray-500 dark:text-gray-400"
        >
          No hay datos de telemetría disponibles.
        </div>
      </div>
    </div>

    <!-- CONTADOR -->
    <div class="text-sm text-gray-600 dark:text-gray-300 text-right">
      Mostrando {{ visibleData.length }} de {{ data.length }} datos
    </div>

    <!-- SELECTOR -->
    <div class="flex items-center gap-2 text-sm select-none">
      <span class="text-gray-600 dark:text-gray-300">Mostrar:</span>
      <select
        v-model.number="itemsLimit"
        class="border rounded-md px-2 py-1 text-sm
               bg-white dark:bg-gray-900
               border-gray-300 dark:border-gray-600
               text-gray-700 dark:text-gray-200"
      >
        <option value="5">5</option>
        <option value="10">10</option>
        <option value="20">20</option>
        <option value="50">50</option>
      </select>
    </div>

    <!-- MODAL EXTERNO -->
    <InsertScriptModal
      :open="showScriptModal"
      @close="showScriptModal = false"
    />

  </div>
</template>

<script setup>
import { defineProps, ref, computed } from "vue";
import SvgIcon from "@/components/icons/SvgIcon.vue";
import InsertScriptModal from "@/components/DispositivosUi/SidebarUi/InsertScriptModal.vue";

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
});

const itemsLimit = ref(5);
const showScriptModal = ref(false);

const visibleData = computed(() =>
  props.data.slice(0, itemsLimit.value)
);

function formatDate(ts) {
  if (!ts) return "—";
  return new Date(ts).toLocaleString("es-CL");
}
</script>
