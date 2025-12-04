<template>
  <div class="p-4 bg-white rounded-xl shadow border border-[#E7E7E9]">

    <!-- HEADER -->
    <div class="flex justify-end items-center mb-4">

      <button @click="$emit('nuevaFactura')"
        class="flex items-center gap-2 bg-[#102372] hover:bg-[#FF6600] text-white text-xs px-4 py-2 rounded-lg shadow transition">
        <SvgIcon name="plus" class="w-4 h-4" />
        Ingresar Factura
      </button>

    </div>


    <!-- BUSCADOR + FILAS -->
    <div class="flex flex-col sm:flex-row justify-between items-center mb-3 gap-3">

      <!-- Buscador -->
      <div class="flex w-full sm:w-2/3 gap-2">
        <div class="flex flex-1 border border-[#E7E7E9] rounded-lg overflow-hidden bg-white shadow-sm">
          <div class="flex items-center justify-center px-3 bg-[#E7E7E9] text-[#1D292F]">
            <SvgIcon name="search" class="w-4 h-4" />
          </div>
          <input v-model="search" placeholder="Buscar..."
            class="flex-1 p-2 text-sm text-[#1D292F] placeholder-gray-400 focus:outline-none" />
          <button v-if="search" @click="search = ''"
            class="px-3 bg-[#FF6600] hover:bg-[#d95400] text-white text-xs transition">
            Limpiar
          </button>
        </div>
      </div>

      <!-- Filas -->
      <div class="flex items-center gap-2 text-xs text-[#54595F]">
        <span class="font-semibold">Filas:</span>
        <select v-model.number="rows"
          class="border border-[#E7E7E9] bg-white rounded px-2 py-1 text-xs focus:ring-1 focus:ring-[#6EC1E4]">
          <option v-for="n in [5, 10, 25, 50, 100]" :key="n">{{ n }}</option>
        </select>
      </div>
    </div>

    <!-- CONTADOR -->
    <div class="flex justify-end mb-2">
      <div class="text-xs font-semibold text-[#102372] bg-[#6EC1E4]/20 p-1.5 rounded-md">
        Mostrando <span class="font-bold">{{ paginated.length }}</span> de
        <span class="font-bold">{{ filtradas.length }}</span> facturas
      </div>
    </div>

    <!-- TABLE DESKTOP -->
    <div class="hidden sm:block overflow-x-auto max-h-[60vh] border border-[#E7E7E9] rounded-lg shadow-sm">
      <table class="min-w-full text-sm">
        <thead class="bg-[#172F3F] text-white uppercase text-xs sticky top-0 z-20">
          <tr>
            <th class="px-4 py-3">
              <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
            </th>

            <th v-for="col in props.columns" :key="col"
              class="px-4 py-3 text-left cursor-pointer hover:bg-[#1D292F] transition" @click="toggleSort(col)">
              <div class="flex items-center gap-1">
                {{ col }}
                <span v-if="ordenCampo === col">
                  {{ ordenDir === 'asc' ? '▲' : '▼' }}
                </span>
              </div>
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="f in paginated" :key="f.id" class="border-b border-[#E7E7E9] hover:bg-[#E7E7E9] transition">
            <td class="px-4 py-2">
              <input type="checkbox" :value="f.id" v-model="selected" />
            </td>

            <td v-for="col in props.columns" :key="col + f.id" class="px-4 py-2 whitespace-nowrap text-[#1D292F]">
              {{ formatValue(f[col], col) }}
            </td>
          </tr>

          <tr v-if="paginated.length === 0">
            <td :colspan="props.columns.length + 1" class="text-center py-6 text-[#54595F]">
              No hay facturas para mostrar
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MOBILE CARDS -->
    <div class="sm:hidden max-h-[60vh] overflow-y-auto space-y-4 p-1">
      <div v-for="f in paginated" :key="f.id"
        class="border border-[#E7E7E9] rounded-2xl p-4 shadow-sm bg-white hover:shadow-lg hover:-translate-y-1 transition-all">
        <div class="flex justify-between items-center mb-3">
          <input type="checkbox" :value="f.id" v-model="selected" />

          <span class="px-2 py-0.5 text-[10px] rounded-full bg-[#6EC1E4]/25 text-[#102372] font-semibold">
            Factura
          </span>
        </div>

        <div class="space-y-2 text-[12px]">
          <div v-for="col in props.columns" :key="col"
            class="flex justify-between py-1 border-b border-[#E7E7E9] last:border-b-0">
            <span class="text-[#54595F] font-medium">{{ col }}:</span>
            <span class="font-semibold">{{ formatValue(f[col], col) }}</span>
          </div>
        </div>
      </div>

      <p v-if="paginated.length === 0" class="text-center text-[#54595F] text-xs py-4">
        No hay facturas para mostrar
      </p>
    </div>

    <!-- PAGINACIÓN -->
    <div
      class="flex justify-between items-center mt-3 text-xs bg-white p-3 rounded-lg shadow-inner border border-[#E7E7E9]">
      <button @click="prevPage" :disabled="page === 1"
        class="px-2 py-1 border border-[#E7E7E9] rounded bg-[#F3F3F3] disabled:opacity-50 hover:bg-[#102372] hover:text-white transition">
        <SvgIcon name="chevron-left" class="w-3 h-3" />
      </button>

      <span class="text-[#1D292F]">
        Pág. <span class="text-[#102372] font-bold">{{ page }}</span> / {{ totalPages }}
      </span>

      <button @click="nextPage" :disabled="page === totalPages"
        class="px-2 py-1 border border-[#E7E7E9] rounded bg-[#F3F3F3] disabled:opacity-50 hover:bg-[#102372] hover:text-white transition">
        <SvgIcon name="chevron-right" class="w-3 h-3" />
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import SvgIcon from "@/components/icons/SvgIcon.vue";

const props = defineProps({
  facturas: Array,
  modelValue: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] }
});

const emit = defineEmits(["update:modelValue", "nuevaFactura", "eliminarSeleccionadas"]);

const selected = ref([...props.modelValue]);

// --- mantención de v-model ---
function arraysIguales(a, b) {
  if (a.length !== b.length) return false;
  return a.every(v => b.includes(v));
}

watch(selected, (val) => {
  if (!arraysIguales(val, props.modelValue)) {
    emit("update:modelValue", val);
  }
});

watch(() => props.modelValue, (val) => {
  if (!arraysIguales(val, selected.value)) {
    selected.value = [...val];
  }
});

// --- tabla ---
const search = ref("");
const rows = ref(5);
const page = ref(1);

const ordenCampo = ref("");
const ordenDir = ref("asc");

function toggleSort(campo) {
  if (ordenCampo.value === campo) {
    ordenDir.value = ordenDir.value === "asc" ? "desc" : "asc";
  } else {
    ordenCampo.value = campo;
    ordenDir.value = "asc";
  }
}

// format helper
function formatValue(value, col) {
  if (col === "litros") return Math.round(value).toLocaleString("es-CL");
  if (col === "total") return "$" + value.toLocaleString("es-CL");
  return value ?? "-";
}

const filtradas = computed(() => {
  let list = [...props.facturas];

  if (search.value.trim()) {
    const q = search.value.toLowerCase();
    list = list.filter(f =>
      props.columns.some(col =>
        String(f[col] ?? "").toLowerCase().includes(q)
      )
    );
  }

  if (ordenCampo.value) {
    list.sort((a, b) => {
      let A = a[ordenCampo.value];
      let B = b[ordenCampo.value];

      if (ordenCampo.value === "fecha") {
        A = new Date(a.fecha);
        B = new Date(b.fecha);
      }

      return ordenDir.value === "asc" ? A - B : B - A;
    });
  }

  return list;
});

const isAllSelected = computed(() =>
  filtradas.value.length > 0 &&
  filtradas.value.every(f => selected.value.includes(f.id))
);

const toggleSelectAll = () => {
  if (isAllSelected.value) selected.value = [];
  else selected.value = filtradas.value.map(f => f.id);
};

const totalPages = computed(() => Math.ceil(filtradas.value.length / rows.value));

const paginated = computed(() => {
  const start = (page.value - 1) * rows.value;
  return filtradas.value.slice(start, start + rows.value);
});

watch([rows, filtradas], () => page.value = 1);

const nextPage = () => page.value < totalPages.value && page.value++;
const prevPage = () => page.value > 1 && page.value--;
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity .25s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
