<template>
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div
            class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-lg relative w-full max-w-5xl h-auto p-6 border border-gray-300 dark:border-gray-700 shadow-xl overflow-auto">

            <!-- Header -->
            <h2 class="text-2xl font-bold mb-4 text-center text-[#102372] dark:text-[#ff6600]">
                Mantenciones Vehículo {{ patente }}
            </h2>

            <button @click="$emit('close')"
                class="absolute top-4 right-4 p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                title="Cerrar">
                <SvgIcon name="close" class="w-6 h-6" />
            </button>

            <!-- Tabla Mantenciones -->
            <div class="overflow-x-auto">
                <table class="min-w-full text-xs sm:text-sm md:text-base text-center border-collapse">
                    <thead class="bg-[#102372] dark:bg-[#102372] sticky top-0 z-10 text-gray-100">
                        <tr>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Nombre</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Tipo</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Intervalo</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Último</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Umbral</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Actual</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Faltante</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Fecha Creación</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Estado</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Editar</th>
                            <th class="py-2 px-3 border-b border-gray-300 dark:border-gray-600">Eliminar</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="(m, idx) in mantencionesConEstado" :key="idx"
                            class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b dark:border-gray-600">


                            <td class="py-2 px-3">{{ m.nombre || m.name }}</td>
                            <td class="py-2 px-3">{{ m.tipo || m.type }}</td>
                            <td class="py-2 px-3">{{ m.intervalo }}</td>
                            <td class="py-2 px-3">{{ m.ultimo }}</td>
                            <td class="py-2 px-3">{{ m.umbral }}</td>
                            <td class="py-2 px-3">{{ m.actual }}</td>
                            <td class="py-2 px-3">{{ m.faltante }}</td>
                            <td class="py-2 px-3">{{ formatFecha(m.fechaCreacion) }}</td>
                            <td class="py-2 px-3">
                                <div class="flex items-center justify-center">
                                    <img v-if="m.estado === 'OK'"
                                        src="https://sinergygroup.cl/Mantenciones/img/verde.png"
                                        class="w-16 h-16 object-contain" />
                                    <img v-else-if="m.estado === 'Próxima mantención'"
                                        src="https://sinergygroup.cl/Mantenciones/img/amarillo.png"
                                        class="w-16 h-16 object-contain" />
                                    <img v-else-if="m.estado === 'Requiere mantención'"
                                        src="https://sinergygroup.cl/Mantenciones/img/rojo.png"
                                        class="w-16 h-16 object-contain" />
                                </div>
                            </td>



                            <td class="py-2 px-3">
                                <button @click="$emit('editar', idx)"
                                    class="bg-yellow-500 hover:bg-yellow-600 text-white px-2 py-1 rounded text-xs">
                                    Editar
                                </button>
                            </td>

                            <td class="py-2 px-3">
                                <button @click="$emit('eliminar', idx)"
                                    class="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded text-xs">
                                    Eliminar
                                </button>
                            </td>

                        </tr>

                        <tr v-if="!mantenciones || mantenciones.length === 0">
                            <td colspan="11" class="text-center py-4 text-gray-500 dark:text-gray-400">
                                No hay mantenciones registradas
                            </td>
                        </tr>
                    </tbody>
                </table>
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
        mantenciones: { type: Array, required: true }
    },
    methods: {
        formatFecha(fechaStr) {
            const f = new Date(fechaStr)
            return f.toLocaleString()
        }
    },
    computed: {
        mantencionesConEstado() {
            return this.mantenciones.map((m, i) => {
                let umbral;
                let faltante;
                let estado;

                console.log(`--- Mantención ${i} ---`, m);

                if (m.tipo === 'Por Odómetro') {
                    umbral = Number(m.ultimo) + Number(m.intervalo);
                    faltante = umbral - Number(m.actual);
                } else {
                    const [yyyy, mm, dd] = (m.ultimo || '').split('-');
                    const ultimaFecha = new Date(yyyy, mm - 1, dd); // ✅ orden correcto
                    const intervaloDias = Number(m.intervalo) || 0;

                    const umbralDate = new Date(
                        ultimaFecha.getFullYear(),
                        ultimaFecha.getMonth(),
                        ultimaFecha.getDate() + intervaloDias
                    );

                    // ✅ Mostrar formato "dd/mm/yyyy"
                    const dia = String(umbralDate.getDate()).padStart(2, '0');
                    const mes = String(umbralDate.getMonth() + 1).padStart(2, '0');
                    const anio = umbralDate.getFullYear();
                    umbral = `${dia}-${mes}-${anio}`;

                    faltante = Math.ceil((umbralDate - new Date()) / (1000 * 60 * 60 * 24));

                    if (faltante <= 0) estado = 'Requiere mantención';
                    else if (faltante <= Number(m.alerta)) estado = 'Próxima mantención';
                    else estado = 'OK';
                }

                return { ...m, umbral, faltante, estado };
            });
        }


    }

}
</script>

<style scoped>
button {
    transition: all 0.2s ease-in-out;
}
</style>
