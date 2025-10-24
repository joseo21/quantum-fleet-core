<template>
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4 overflow-auto">
        <div
            class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-lg relative w-full max-w-6xl h-auto p-4 sm:p-6 border border-gray-300 dark:border-gray-700 shadow-xl">

            <!-- Header -->
            <h2 class="text-xl sm:text-2xl font-bold mb-4 text-center text-[#102372] dark:text-[#ff6600]">
                Mantenciones Vehículo {{ patente }}
            </h2>

            <!-- Botón cerrar -->
            <button @click="$emit('close')"
                class="absolute top-3 right-3 p-1 sm:p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                title="Cerrar">
                <SvgIcon name="close" class="w-5 h-5 sm:w-6 sm:h-6" />
            </button>

            <!-- Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="(m, idx) in mantencionesConEstado" :key="idx"
                    class="bg-gray-100 dark:bg-gray-800 rounded-lg shadow p-3 sm:p-4 flex flex-col gap-2 border border-gray-300 dark:border-gray-700 text-sm">

                    <!-- Nombre y tipo -->
                    <div class="flex justify-between items-center mb-1">
                        <span class="font-semibold text-sm sm:text-base truncate">{{ m.nombre || m.name }}</span>
                        <span class="text-xs px-2 py-0.5 rounded bg-blue-600 text-white">{{ m.tipo || m.type }}</span>
                    </div>

                    <!-- Datos principales -->
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <span class="text-gray-500 text-xs">Intervalo</span>
                            <div class="font-medium">{{ m.intervalo }}</div>
                        </div>
                        <div>
                            <span class="text-gray-500 text-xs">Último</span>
                            <div class="font-medium">{{ m.ultimo }}</div>
                        </div>
                        <div>
                            <span class="text-gray-500 text-xs">Umbral</span>
                            <div class="font-medium">{{ m.umbral }}</div>
                        </div>
                        <div>
                            <span class="text-gray-500 text-xs">Actual</span>
                            <div class="font-medium">{{ m.actual }}</div>
                        </div>
                        <div>
                            <span class="text-gray-500 text-xs">Faltante</span>
                            <div class="font-medium">{{ m.faltante }}</div>
                        </div>
                        <div>
                            <span class="text-gray-500 text-xs">Alerta</span>
                            <div class="font-medium">{{ m.alerta || 0 }}</div>
                        </div>
                        <div class="col-span-2">
                            <span class="text-gray-500 text-xs">Email</span>
                            <div class="font-medium truncate">{{ m.email || m.correo || 'N/A' }}</div>
                        </div>
                        <div class="col-span-2">
                            <span class="text-gray-500 text-xs">Creación</span>
                            <div class="font-medium">{{ formatFecha(m.fechaCreacion) }}</div>
                        </div>
                    </div>

                    <!-- Estado e imágenes -->
                    <div class="flex items-center justify-between mt-2">
                        <div>
                            <img v-if="m.estado === 'OK'" src="https://sinergygroup.cl/Mantenciones/img/verde.png"
                                class="w-10 h-10 sm:w-12 sm:h-12 object-contain" />
                            <img v-else-if="m.estado === 'Próxima mantención'"
                                src="https://sinergygroup.cl/Mantenciones/img/amarillo.png"
                                class="w-10 h-10 sm:w-12 sm:h-12 object-contain" />
                            <img v-else-if="m.estado === 'Requiere mantención'"
                                src="https://sinergygroup.cl/Mantenciones/img/rojo.png"
                                class="w-10 h-10 sm:w-12 sm:h-12 object-contain" />
                        </div>

                        <!-- Botones -->
                        <div class="flex gap-2 sm:gap-3">
                            <button @click="$emit('editar', idx)"
                                class="bg-yellow-500 hover:bg-yellow-600 text-white px-2 py-1 rounded text-xs sm:text-sm">Editar</button>
                            <button @click="$emit('eliminar', idx)"
                                class="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded text-xs sm:text-sm">Eliminar</button>
                        </div>
                    </div>
                </div>

                <!-- Si no hay mantenciones -->
                <div v-if="!mantenciones || mantenciones.length === 0"
                    class="col-span-full text-center py-6 text-gray-500 dark:text-gray-400">
                    No hay mantenciones registradas
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
        patente: { type: String, required: true },
        mantenciones: { type: Array, required: true },
        horometrosActuales: { type: Object, default: () => ({}) }
    },
    methods: {
        formatFecha(fechaStr) {
            const f = new Date(fechaStr)
            return f.toLocaleString()
        }
    },
    computed: {
        mantencionesConEstado() {
            return this.mantenciones.map((m) => {
                const tipo = (m.tipo || m.type || '').toString().trim()
                const intervalo = Number(m.intervalo || 0)
                const alerta = Number(m.alerta || 0)

                let umbral = null
                let faltante = null
                let estado = 'Desconocido'
                let actual = 0
                let horaRegistro = m.horaRegistro || null

                // Odómetro
                if (tipo === 'Por Odómetro') {
                    // Obtener odómetro actual real del vehículo
                    const vehiculo = this.$parent.mantenciones.find(v => v.patente === this.patente)
                    actual = vehiculo ? Number(vehiculo.odometro) : Number(m.actual || 0)

                    const ultimo = Number(m.ultimo || 0)
                    const siguiente = ultimo + intervalo
                    umbral = siguiente
                    faltante = siguiente - actual

                    if (faltante <= 0) estado = 'Requiere mantención'
                    else if (faltante <= alerta) estado = 'Próxima mantención'
                    else estado = 'OK'
                }

                // Horómetro
                else if (tipo === 'Por Horómetro') {
                    actual = this.horometrosActuales[this.patente] ?? Number(m.actual || 0)

                    const ultimo = Number(m.ultimo || 0)
                    const siguiente = ultimo + intervalo
                    umbral = siguiente
                    faltante = siguiente - actual

                    if (faltante <= 0) estado = 'Requiere mantención'
                    else if (faltante <= alerta) estado = 'Próxima mantención'
                    else estado = 'OK'
                }

                // Por Tiempo
                else if (tipo === 'Por Tiempo') {
                    let ultimaFecha
                    if (typeof m.ultimo === 'string') {
                        const parts = m.ultimo.split('-')
                        if (parts.length === 3 && parts[0].length === 4) {
                            // Formato YYYY-MM-DD
                            ultimaFecha = new Date(m.ultimo)
                        } else if (parts.length === 3) {
                            // Formato DD-MM-YYYY
                            const [dd, mm, yyyy] = parts
                            ultimaFecha = new Date(Number(yyyy), Number(mm) - 1, Number(dd))
                        } else {
                            ultimaFecha = new Date(m.ultimo)
                        }
                    } else {
                        ultimaFecha = new Date()
                    }

                    if (!isNaN(ultimaFecha.getTime())) {
                        const umbralDate = new Date(ultimaFecha)
                        umbralDate.setDate(umbralDate.getDate() + intervalo)
                        const hoy = new Date()
                        faltante = Math.ceil((umbralDate - new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate())) / (1000 * 60 * 60 * 24))
                        umbral = umbralDate.toISOString().split('T')[0]

                        if (faltante <= 0) estado = 'Requiere mantención'
                        else if (faltante <= alerta) estado = 'Próxima mantención'
                        else estado = 'OK'

                        actual = new Date().toISOString().split('T')[0]
                    }
                }

                return { ...m, umbral, faltante, estado, actual, horaRegistro }
            })
        }
    }


}
</script>
