<template>
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[70] p-4">
        <div
            class="relative bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-lg w-full max-w-md p-6 border border-gray-300 dark:border-gray-700 shadow-xl">

            <!-- Botón cerrar -->
            <button @click="$emit('close')"
                class="absolute top-4 right-4 p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                title="Cerrar">
                <SvgIcon name="close" class="w-6 h-6" />
            </button>

            <h2 class="text-2xl font-bold mb-4 text-center text-[#102372] dark:text-[#ff6600]">
                Agregar Nuevo Tipo de Mantención
            </h2>

            <form @submit.prevent="guardarTipo" class="flex flex-col gap-4">
                <!-- Nombre -->
                <div>
                    <label class="block text-sm mb-1">Nombre del Tipo</label>
                    <input type="text" v-model="nuevoTipo.name" placeholder="Ej: Cambio de Pastillas"
                        class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
                        required />
                </div>

                <!-- Tipo -->
                <div>
                    <label class="block text-sm mb-1">Tipo de Mantención</label>
                    <select v-model="nuevoTipo.type"
                        class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
                        required>
                        <option value="">Seleccione...</option>
                        <option value="Por Odómetro">Por Odómetro</option>
                        <option value="Por Tiempo">Por Tiempo</option>
                        <option value="Por Horómetro">Por Horómetro</option>
                    </select>
                </div>

                <!-- Descripción -->
                <div>
                    <label class="block text-sm mb-1">Descripción</label>
                    <textarea v-model="nuevoTipo.description" placeholder="Descripción del tipo de mantención"
                        class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
                        rows="3"></textarea>
                </div>

                <!-- Botón Guardar -->
                <button type="submit"
                    class="w-full bg-[#102372] hover:bg-[#0d1c5a] text-white px-4 py-2 rounded font-semibold transition">
                    Guardar
                </button>
            </form>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'

export default {
    name: 'ModalMantencionType',
    components: { SvgIcon },
    emits: ['close', 'save'],
    setup(props, { emit }) {
        const nuevoTipo = ref({
            name: '',
            type: '',
            description: ''
        })

        function guardarTipo() {
            if (!nuevoTipo.value.name || !nuevoTipo.value.type) return
            emit('save', { ...nuevoTipo.value })
            nuevoTipo.value = { name: '', type: '', description: '' } // reset
        }

        return { nuevoTipo, guardarTipo }
    }
}
</script>

<style scoped>
button {
    transition: all 0.2s ease-in-out;
}

input::placeholder,
textarea::placeholder {
    color: #9ca3af;
}
</style>
