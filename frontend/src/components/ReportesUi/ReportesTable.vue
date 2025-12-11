<template>
  <div class="bg-white border border-gray-200 rounded-xl shadow-xl overflow-hidden">

    <!-- TÍTULO -->
    <div class="px-5 py-3 bg-gradient-to-r from-[#102372] to-[#233c9b] text-white font-semibold text-sm">
      Telemetría Reciente del Dispositivo
    </div>

    <!-- TABLA CON SCROLL -->
    <div class="max-h-[380px] overflow-y-auto custom-scroll">

      <table class="w-full text-sm">

        <!-- ===========================
             HEADER DINÁMICO
        ============================ -->
        <thead class="bg-[#102372] text-white text-xs uppercase font-bold sticky top-0 shadow-md">
          <tr>

            <!-- DISPOSITIVO -->
            <th class="th-sort px-5 py-3 text-left cursor-pointer" @click="sortBy('dispositivo')">
              <span>Dispositivo</span>

              <span class="sort-arrow">
                {{ sort.key === 'dispositivo'
                    ? (sort.order === 'asc' ? '▲' : '▼')
                    : '▼'
                }}
              </span>
            </th>

            <!-- FECHA -->
            <th class="th-sort px-5 py-3 text-left cursor-pointer" @click="sortBy('fecha')">
              <span>Fecha</span>

              <span class="sort-arrow">
                {{ sort.key === 'fecha'
                    ? (sort.order === 'asc' ? '▲' : '▼')
                    : '▼'
                }}
              </span>
            </th>

            <!-- COLUMNAS DINÁMICAS -->
            <th
              v-for="col in props.variables"
              :key="col"
              class="px-5 py-3 text-left"
            >
              {{ col.replace(/_/g, ' ') }}
            </th>

          </tr>
        </thead>

        <!-- ===========================
             CUERPO PIVOTEADO
        ============================ -->
        <tbody>
          <tr
            v-for="row in sortedRows"
            :key="row.__id"
            class="border-b hover:bg-gray-50 odd:bg-gray-50 even:bg-white transition"
          >
            <td class="px-5 py-3 font-semibold text-gray-900">{{ row.dispositivo }}</td>
            <td class="px-5 py-3 text-gray-700">{{ row.fecha }}</td>

            <!-- CELDAS GENERADAS -->
            <td
              v-for="col in props.variables"
              :key="col"
              class="px-5 py-3"
            >
              <span
                v-if="row[col] !== undefined"
                class="px-2 py-1 rounded-md text-xs font-bold"
                :class="badgeColor(row[col])"
              >
                {{ row[col] }}
              </span>

              <span v-else class="text-gray-400 text-xs">—</span>
            </td>
          </tr>

          <!-- SIN DATOS -->
          <tr v-if="sortedRows.length === 0">
            <td :colspan="2 + props.variables.length" class="py-8 text-center text-gray-500">
              No hay datos para el filtro seleccionado.
            </td>
          </tr>
        </tbody>

      </table>

    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from "vue"

const props = defineProps({
  items: Array,
  variables: Array,
  dateRange: Object
})

/* ===========================
   ORDENAMIENTO
=========================== */
const sort = reactive({
  key: "fecha",
  order: "desc"
})

function sortBy(key) {
  if (sort.key === key) {
    sort.order = sort.order === "asc" ? "desc" : "asc"
  } else {
    sort.key = key
    sort.order = "asc"
  }
}

function parseFecha(f) {
  if (!f) return null
  const d = new Date(f.replace(" ", "T"))
  return isNaN(d) ? null : d
}

/* ===========================
   FILTRO POR FECHA
=========================== */
function isInRange(f) {
  const fecha = parseFecha(f)
  if (!fecha) return true

  const now = new Date()
  const r = props.dateRange

  if (r?.type === "preset") {
    const H = {
      last_1h: 1,
      last_12h: 12,
      last_24h: 24,
      last_7d: 24 * 7,
      last_30d: 24 * 30,
      last_180d: 24 * 180
    }

    const hours = H[r.value]
    if (!hours) return true

    const from = new Date(now - hours * 3600 * 1000)
    return fecha >= from
  }

  if (r?.type === "custom") {
    return fecha >= new Date(r.from) && fecha <= new Date(r.to)
  }

  return true
}

/* ===========================
   PIVOTEAR
=========================== */
const rows = computed(() => {
  const out = {}

  for (const device of props.items || []) {
    for (const dato of device.datos || []) {
      if (props.variables.length && !props.variables.includes(dato.clave)) continue
      if (!isInRange(dato.fecha)) continue

      const id = `${device.id}-${dato.fecha}`

      if (!out[id]) {
        out[id] = {
          __id: id,
          dispositivo: device.nombre ?? `ID ${device.id}`,
          fecha: dato.fecha
        }
      }

      out[id][dato.clave] = dato.valor
    }
  }

  return Object.values(out)
})

/* ===========================
   ORDENAMIENTO FINAL
=========================== */
const sortedRows = computed(() => {
  return [...rows.value].sort((a, b) => {
    const A = sort.key === "fecha" ? parseFecha(a.fecha) : a[sort.key]
    const B = sort.key === "fecha" ? parseFecha(b.fecha) : b[sort.key]

    if (sort.order === "asc") return A > B ? 1 : -1
    return A < B ? 1 : -1
  })
})

/* ===========================
   COLORES BADGE
=========================== */
function badgeColor(valor) {
  if (!isNaN(valor)) {
    if (valor > 80) return "bg-red-100 text-red-700"
    if (valor > 40) return "bg-yellow-100 text-yellow-700"
    return "bg-green-100 text-green-700"
  }
  return "bg-gray-200 text-gray-700"
}
</script>

<style>
/* Scroll Pro */
.custom-scroll::-webkit-scrollbar {
  width: 8px;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background: #c7c7c7;
  border-radius: 4px;
}
.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: #9f9f9f;
}

/* ===========================
   ➤ FLECHAS DE ORDENAMIENTO
=========================== */

/* Ocultas SIEMPRE, incluso si la columna está activa */
.sort-arrow {
  opacity: 0 !important;
  margin-left: 4px;
  transition: opacity 0.15s ease;
}

/* Mostrar SOLO al pasar el mouse */
.th-sort:hover .sort-arrow {
  opacity: 1 !important;
}
</style>
