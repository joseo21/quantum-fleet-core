<template>
    <div class="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-200 dark:border-gray-700 shadow">

        <!-- HEADER DE TABLA + BOTÓN ELIMINAR -->
        <div class="flex items-center justify-between p-2 bg-gray-100 dark:bg-gray-900 rounded-md sticky top-0 z-10">

            <div class="flex items-center gap-2">
                <input
                    type="checkbox"
                    :checked="selectAll"
                    @change="toggleSelectAll($event.target.checked)"
                    class="w-4 h-4 text-[#102372]"
                />
                <h3 class="text-xs font-semibold text-gray-700 dark:text-gray-300">
                    Seleccionar Todo
                </h3>
            </div>

            <button
                v-if="selectedIds.length > 0"
                @click="eliminarSeleccionadosLocal"
                class="flex items-center gap-2 px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-md text-xs transition shadow"
            >
                <SvgIcon name="trash" class="w-4 h-4" />
                Eliminar ({{ selectedIds.length }})
            </button>
        </div>

        <!-- LISTA SCROLLEABLE -->
        <div class="space-y-2 max-h-[420px] overflow-y-auto">

            <div
                v-for="d in paginatedDevices"
                :key="d.id"
                class="bg-white dark:bg-gray-800 rounded-md border border-gray-300 dark:border-gray-700 shadow-sm p-3 hover:shadow"
            >
                <div class="flex items-center gap-3">

                    <!-- CHECKBOX -->
                    <input
                        type="checkbox"
                        :checked="selectedIds.includes(d.id)"
                        @change="toggleItem(d.id)"
                        class="w-4 h-4 text-[#102372]"
                    />

                    <!-- INFO -->
                    <div class="flex-1 grid grid-cols-1 sm:grid-cols-6 gap-2 text-xs">

                        <div>
                            <p class="font-semibold text-[#102372] dark:text-white truncate">{{ d.name }}</p>
                            <p class="text-[10px] text-gray-500">{{ d.company }}</p>
                        </div>

                        <div>
                            <span class="text-gray-400 text-[9px] uppercase block">Identificador</span>
                            <p class="text-gray-700 dark:text-gray-300 truncate">{{ d.imei ?? d.token }}</p>
                        </div>

                        <!-- ⭐ NUEVO CAMPO ICCID -->
                        <div>
                            <span class="text-gray-400 text-[9px] uppercase block">ICCID</span>
                            <p class="text-gray-700 dark:text-gray-300 truncate">{{ d.iccid ?? "—" }}</p>
                        </div>

                        <div>
                            <span class="text-gray-400 text-[9px] uppercase block">Creado</span>
                            <p class="text-gray-700 dark:text-gray-300">{{ d.createdAt }}</p>
                        </div>

                        <div>
                            <span class="text-gray-400 text-[9px] uppercase block">Último reporte</span>
                            <p class="text-gray-700 dark:text-gray-300">{{ d.lastReport }}</p>
                        </div>

                        <div>
                            <span class="text-gray-400 text-[9px] uppercase block">Tipo</span>
                            <p class="text-gray-700 dark:text-gray-300">{{ d.type }}</p>
                        </div>

                    </div>

                    <!-- ⭐ BOTONES ACCIONES -->
                    <div class="flex gap-2 items-center">

                        <!-- BOTÓN EDITAR -->
                        <button
                            @click="emit('edit', d)"
                            title="Ver detalles dispositivo"
                            class="bg-blue-600 hover:bg-blue-700 text-white p-1.5 rounded-full flex items-center justify-center transition"
                        >
                            <SvgIcon name="eye" class="w-4 h-4" />
                        </button>

                        <!-- BOTÓN COPIAR -->
                        <button
                            @click="emit('copy-device', d)"
                            title="Copiar datos"
                            class="p-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded-full relative flex items-center justify-center transition"
                        >
                            <SvgIcon name="copy" class="w-4 h-4" />

                            <!-- Tooltip -->
                            <span
                                v-if="copiedId === d.id"
                                class="fixed bg-gray-700 text-white text-[10px] px-1.5 py-0.5 rounded whitespace-nowrap z-[9999] shadow-lg"
                                :style="tooltipPosition"
                            >
                                Copiado!
                            </span>
                        </button>

                    </div>

                </div>
            </div>

            <div v-if="props.devices.length === 0" class="text-center text-gray-400 py-10">
                No hay dispositivos registrados
            </div>

        </div>

        <!-- FOOTER -->
        <div class="flex flex-col sm:flex-row justify-between items-center mt-3 text-xs sm:text-sm text-gray-700 dark:text-gray-300 gap-3">

            <div class="flex items-center gap-2">
                <span>Filas por página:</span>
                <select
                    v-model.number="rowsPerPage"
                    class="border dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700"
                >
                    <option v-for="n in [5, 10, 20, 50]" :key="n">{{ n }}</option>
                </select>
            </div>

            <div class="flex items-center gap-2">
                <button
                    @click="previousPage"
                    :disabled="currentPage === 1"
                    class="px-2 py-1 border rounded disabled:opacity-40 hover:bg-[#ff6600] hover:text-white"
                >
                    <SvgIcon name="chevron-left" class="w-5 h-5" />
                </button>

                <span>Página {{ currentPage }} / {{ totalPages }}</span>

                <button
                    @click="nextPage"
                    :disabled="currentPage === totalPages"
                    class="px-2 py-1 border rounded disabled:opacity-40 hover:bg-[#ff6600] hover:text-white"
                >
                    <SvgIcon name="chevron-right" class="w-5 h-5" />
                </button>
            </div>

        </div>

    </div>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'

const props = defineProps({
    devices: { type: Array, required: true },
    copiedId: { type: [Number, null], required: true }    
})

const emit = defineEmits([
    'update:selectedIds',
    'update:selectAll',
    'eliminar',
    'edit',
    'copy-device'                                          
])

const selectedIds = ref([])
const selectAll = ref(false)

const rowsPerPage = ref(5)
const currentPage = ref(1)

/* PAGINACIÓN */
const totalPages = computed(() =>
    Math.ceil(props.devices.length / rowsPerPage.value)
)

const paginatedDevices = computed(() => {
    const start = (currentPage.value - 1) * rowsPerPage.value
    return props.devices.slice(start, start + rowsPerPage.value)
})

watch(props.devices, () => {
    currentPage.value = 1
    selectAll.value = false
})

/* ELIMINAR LOCAL + EMITIR */
const eliminarSeleccionadosLocal = () => {
    const ids = [...selectedIds.value]
    if (ids.length === 0) return
    emit('eliminar', ids)
    selectedIds.value = []
    selectAll.value = false
    emit('update:selectedIds', [])
    emit('update:selectAll', false)
}

/* SELECCIÓN */
const toggleItem = (id) => {
    if (selectedIds.value.includes(id)) {
        selectedIds.value = selectedIds.value.filter(x => x !== id)
    } else {
        selectedIds.value.push(id)
    }
    emit('update:selectedIds', selectedIds.value)
}

const toggleSelectAll = (checked) => {
    selectAll.value = checked
    selectedIds.value = checked ? paginatedDevices.value.map(d => d.id) : []
    emit('update:selectAll', checked)
    emit('update:selectedIds', selectedIds.value)
}

/* NAVEGACIÓN */
const nextPage = () => {
    if (currentPage.value < totalPages.value) currentPage.value++
    selectAll.value = false
}

const previousPage = () => {
    if (currentPage.value > 1) currentPage.value--
    selectAll.value = false
}
</script>
