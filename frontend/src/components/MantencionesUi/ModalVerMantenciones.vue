<template>
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-2 sm:p-4">
        <div
            class="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-xl relative w-full max-w-5xl p-4 sm:p-6 border border-gray-200 dark:border-gray-700 shadow-2xl transition-all duration-300 overflow-y-auto max-h-[90vh]">

            <!-- Título + cerrar -->
            <h2 class="text-lg sm:text-2xl font-extrabold mb-3 text-center text-[#1A457D] dark:text-[#66B3FF]">
                Mantenciones Vehículo
                <span class="text-[#007BFF] dark:text-[#FDD835]"> {{ patente }} </span>
            </h2>

            <button @click="$emit('close')"
                class="absolute top-3 right-3 p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200"
                title="Cerrar">
                <SvgIcon name="close" class="w-5 h-5 sm:w-6 sm:h-6" />
            </button>

            <!-- CONTENEDOR: siempre mostramos solo las mantenciones paginadas -->
            <div class="w-full">
                <div v-if="!mantenciones || mantenciones.length === 0"
                    class="py-10 text-center text-base sm:text-lg font-medium text-gray-500 dark:text-gray-400">
                    No hay mantenciones registradas para el vehículo {{ patente }}.
                </div>

                <div v-else class="flex flex-col gap-4 items-center">
                    <!-- Grid responsivo que contiene SOLO las mantenciones de la página actual -->
                    <div class="w-full grid gap-5 justify-items-center" :class="gridColsClass">
                        <div v-for="(m, idx) in mantencionesPaginadas" :key="m.id || m.nombre + idx"
                            class="bg-white dark:bg-gray-900 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 p-4 flex flex-col gap-3 border border-gray-200 dark:border-gray-700 text-sm w-full sm:max-w-md">

                            <!-- Encabezado -->
                            <div
                                class="flex flex-wrap justify-between items-start pb-2 border-b border-gray-100 dark:border-gray-700 gap-2">
                                <span
                                    class="font-bold text-base sm:text-lg text-[#1A457D] dark:text-[#66B3FF] truncate flex-1 min-w-0">
                                    {{ m.nombre || m.name }}
                                </span>
                                <span
                                    class="text-xs font-semibold px-3 py-1 rounded-full bg-[#007BFF] text-white dark:bg-[#FDD835] dark:text-gray-900 shadow-md whitespace-nowrap">
                                    {{ m.tipo || m.type }}
                                </span>
                            </div>

                            <!-- Cuerpo -->
                            <div class="grid grid-cols-2 gap-x-4 gap-y-3 text-gray-700 dark:text-gray-300 text-sm">
                                <div v-for="campo in cardCampos(m)" :key="campo.label" class="flex flex-col">
                                    <span
                                        class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                                        {{ campo.label }}
                                    </span>
                                    <div class="font-semibold text-base truncate"
                                        :class="campo.label === 'Faltante' ? faltanteClass(m) : ''">
                                        {{ campo.value }}
                                    </div>
                                </div>

                                <div
                                    class="col-span-2 flex flex-col pt-3 border-t border-gray-100 dark:border-gray-700">
                                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400">Email
                                        Contacto</span>
                                    <div class="font-medium text-sm truncate">{{ m.email || m.correo || 'N/A' }}</div>
                                </div>

                                <div class="col-span-2 flex flex-col">
                                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400">Fecha
                                        Creación</span>
                                    <div class="font-medium text-sm">{{ formatFecha(m.fechaCreacion) }}</div>
                                </div>
                            </div>

                            <!-- Estado y botones -->
                            <div
                                class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3 mt-4 border-t pt-3 border-gray-100 dark:border-gray-700">
                                <div class="flex items-center gap-2">
                                    <img v-if="m.estado === 'OK'"
                                        src="https://sinergygroup.cl/Mantenciones/img/verde.png"
                                        class="w-7 h-7 sm:w-8 sm:h-8 object-contain shadow rounded-full" alt="OK"
                                        title="OK" />
                                    <img v-else-if="m.estado === 'Próxima mantención'"
                                        src="https://sinergygroup.cl/Mantenciones/img/amarillo.png"
                                        class="w-7 h-7 sm:w-8 sm:h-8 object-contain shadow rounded-full" alt="Próxima"
                                        title="Próxima mantención" />
                                    <img v-else-if="m.estado === 'Requiere mantención'"
                                        src="https://sinergygroup.cl/Mantenciones/img/rojo.png"
                                        class="w-7 h-7 sm:w-8 sm:h-8 object-contain shadow rounded-full" alt="Requiere"
                                        title="Requiere mantención" />
                                    <span class="text-sm font-semibold" :class="{
                                        'text-green-600 dark:text-green-400': m.estado === 'OK',
                                        'text-yellow-600 dark:text-yellow-400': m.estado === 'Próxima mantención',
                                        'text-red-500 dark:text-red-400': m.estado === 'Requiere mantención'
                                    }">
                                        {{ m.estado }}
                                    </span>
                                </div>

                                <div class="flex gap-2 justify-end">
                                    <button @click="$emit('editar', absoluteIndex(idx))"
                                        class="bg-yellow-500 hover:bg-yellow-600 text-white font-semibold px-3 py-1.5 rounded-lg text-xs sm:text-sm transition-all shadow-md hover:shadow-lg focus:ring-2 focus:ring-yellow-500 focus:ring-opacity-50">
                                        Editar
                                    </button>
                                    <button @click="$emit('eliminar', absoluteIndex(idx))"
                                        class="bg-red-500 hover:bg-red-600 text-white font-semibold px-3 py-1.5 rounded-lg text-xs sm:text-sm transition-all shadow-md hover:shadow-lg focus:ring-2 focus:ring-red-500 focus:ring-opacity-50">
                                        Eliminar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Paginación: prev / dots / next -->
                    <div v-if="totalPages > 1" class="flex flex-col items-center gap-2 w-full">
                        <div class="flex items-center gap-3">
                            <button @click="prevPage" :disabled="currentPage === 1"
                                class="p-2 text-sm font-medium rounded-lg transition-colors duration-200 flex items-center gap-1"
                                :class="currentPage === 1 ? 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 cursor-not-allowed' : 'bg-[#1A457D] hover:bg-[#007BFF] text-white'">
                                <SvgIcon name="chevron-left" class="w-4 h-4" />
                                Anterior
                            </button>

                            <!-- indicadores (dots) -->
                            <div class="flex items-center gap-2 px-2">
                                <button v-for="p in totalPages" :key="p" @click="goToPage(p)"
                                    :aria-current="p === currentPage"
                                    class="w-2.5 h-2.5 rounded-full transition-transform transform"
                                    :class="p === currentPage ? 'scale-125' : 'opacity-60 bg-gray-400 dark:bg-gray-600'">
                                </button>
                            </div>

                            <button @click="nextPage" :disabled="currentPage === totalPages"
                                class="p-2 text-sm font-medium rounded-lg transition-colors duration-200 flex items-center gap-1"
                                :class="currentPage === totalPages ? 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 cursor-not-allowed' : 'bg-[#1A457D] hover:bg-[#007BFF] text-white'">
                                Siguiente
                                <SvgIcon name="chevron-right" class="w-4 h-4" />
                            </button>
                        </div>

                        <div class="text-sm text-gray-700 dark:text-gray-300">
                            Página <span class="font-bold">{{ currentPage }}</span> de <span class="font-bold">{{
                                totalPages }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import SvgIcon from '@/components/icons/SvgIcon.vue'

export default {
    name: 'ModalVerMantenciones',
    components: { SvgIcon },
    props: {
        patente: { type: String, default: '' },
        mantenciones: { type: Array, default: () => [] },
        horometrosActuales: { type: Object, default: () => ({}) },
        odometroActual: { type: Number, default: 0 }
    },
    data() {
        return {
            currentPage: 1,
            itemsPerPage: 3, // será recalculado según ancho
            resizeObserver: null
        }
    },
    watch: {
        mantenciones() { this.currentPage = 1 }
    },
    computed: {
        // recalcula mantenciones con estado (igual a tu lógica original)
        mantencionesConEstado() {
            return this.mantenciones.map(m => {
                const tipo = (m.tipo || m.type || '').trim()
                const intervalo = Number(m.intervalo || 0)
                const alerta = Number(m.alerta || 0)
                let umbral, faltante, estado = 'Desconocido', actual = 0

                if (tipo === 'Por Odómetro') {
                    actual = Number(this.odometroActual || m.actual || 0)
                    const siguiente = Number(m.ultimo || 0) + intervalo
                    umbral = siguiente
                    faltante = siguiente - actual
                    estado =
                        faltante <= 0
                            ? 'Requiere mantención'
                            : faltante <= alerta
                                ? 'Próxima mantención'
                                : 'OK'

                } else if (tipo === 'Por Horómetro') {
                    actual = this.horometrosActuales[this.patente] ?? Number(m.actual || 0)
                    const siguiente = Number(m.ultimo || 0) + intervalo
                    umbral = siguiente
                    faltante = siguiente - actual
                    estado =
                        faltante <= 0
                            ? 'Requiere mantención'
                            : faltante <= alerta
                                ? 'Próxima mantención'
                                : 'OK'

                } else if (tipo === 'Por Tiempo') {
                    // 🔹 Tomamos la fecha actual del sistema como "actual"
                    const fechaActual = new Date()
                    actual = fechaActual.toISOString().split('T')[0] // formato YYYY-MM-DD

                    const ultima = new Date(m.ultimo)
                    if (!isNaN(ultima)) {
                        const umbralDate = new Date(ultima)
                        umbralDate.setDate(umbralDate.getDate() + intervalo)
                        const diff = Math.ceil((umbralDate - fechaActual) / (1000 * 60 * 60 * 24))
                        faltante = diff
                        umbral = umbralDate.toISOString().split('T')[0]
                        estado =
                            diff <= 0
                                ? 'Requiere mantención'
                                : diff <= alerta
                                    ? 'Próxima mantención'
                                    : 'OK'
                    }
                }

                return { ...m, umbral, faltante, estado, actual }
            })
        },

        totalPages() {
            const len = this.mantencionesConEstado.length
            return Math.max(1, Math.ceil(len / this.itemsPerPage))
        },

        mantencionesPaginadas() {
            const start = (this.currentPage - 1) * this.itemsPerPage
            return this.mantencionesConEstado.slice(start, start + this.itemsPerPage)
        },

        // clase para grid según itemsPerPage (útil para mantener 1/2/3 columnas)
        gridColsClass() {
            if (this.itemsPerPage === 1) return 'grid-cols-1'
            if (this.itemsPerPage === 2) return 'sm:grid-cols-2 grid-cols-1'
            return 'lg:grid-cols-3 sm:grid-cols-2 grid-cols-1'
        }
    },
    methods: {
        formatFecha(f) {
            if (!f) return 'N/A'
            const d = new Date(f)
            return isNaN(d) ? f : d.toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' })
        },
        // campos que se muestran en las cards (para evitar repetir el array literal en template)
        cardCampos(m) {
            return [
                { label: 'Intervalo', value: m.intervalo ?? 'N/A' },
                { label: 'Último', value: m.ultimo ?? 'N/A' },
                { label: 'Umbral', value: m.umbral ?? 'N/A' },
                { label: 'Actual', value: m.actual ?? 'N/A' },
                { label: 'Faltante', value: m.faltante ?? 'N/A' },
                { label: 'Alerta', value: m.alerta ?? 0 }
            ]
        },
        faltanteClass(m) {
            return m.faltante <= 0
                ? 'text-red-500 dark:text-red-400'
                : (m.faltante > 0 && m.faltante <= (m.alerta ?? 0))
                    ? 'text-yellow-600 dark:text-yellow-400'
                    : 'text-green-600 dark:text-green-400'
        },

        prevPage() {
            if (this.currentPage > 1) this.currentPage--
        },
        nextPage() {
            if (this.currentPage < this.totalPages) this.currentPage++
        },
        goToPage(p) {
            if (p >= 1 && p <= this.totalPages) this.currentPage = p
        },

        // devuelve índice absoluto en el array original (para editar/eliminar)
        absoluteIndex(localIdx) {
            return (this.currentPage - 1) * this.itemsPerPage + localIdx
        },

        // recalcula itemsPerPage según ancho del viewport
        recalcItemsPerPage() {
            const w = window.innerWidth
            let newCount = 3
            if (w < 640) newCount = 1         // móviles
            else if (w >= 640 && w < 1024) newCount = 2 // tablet
            else newCount = 3                // escritorio

            if (newCount !== this.itemsPerPage) {
                this.itemsPerPage = newCount
                // ajustar currentPage si excede totalPages después del cambio
                const maxPage = Math.max(1, Math.ceil(this.mantencionesConEstado.length / this.itemsPerPage))
                if (this.currentPage > maxPage) this.currentPage = maxPage
            }
        },

        // manejador de teclado para navegar
        onKeydown(e) {
            if (e.key === 'ArrowLeft') this.prevPage()
            if (e.key === 'ArrowRight') this.nextPage()
        }
    },
    mounted() {
        // inicializar itemsPerPage
        this.recalcItemsPerPage()
        // resize listener
        window.addEventListener('resize', this.recalcItemsPerPage)
        // teclado
        window.addEventListener('keydown', this.onKeydown)
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.recalcItemsPerPage)
        window.removeEventListener('keydown', this.onKeydown)
    }
}
</script>
