<template>
    <transition name="fade">
        <div v-if="show" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[999] flex items-center justify-center"
             @click.self="$emit('cancel')">

            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 w-full max-w-lg border border-gray-300 dark:border-gray-700 animate-scale-in">

                <!-- HEADER -->
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-[#102372] dark:text-[#ff6600]">
                        Confirmar restauración
                    </h2>

                    <button @click="$emit('cancel')" class="text-gray-600 hover:text-gray-800 dark:hover:text-gray-300">
                        <SvgIcon name="close" class="w-5 h-5" />
                    </button>
                </div>

                <!-- MENSAJE -->
                <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
                    Estás por restaurar el dispositivo a la 
                    <strong>Versión {{ version?.version }}</strong> registrada por 
                    <strong>{{ version?.user }}</strong>.
                </p>

                <p class="text-sm mb-4 text-gray-700 dark:text-gray-300">
                    Se revertirán los siguientes parámetros:
                </p>

                <!-- LISTA DE PARÁMETROS -->
                <ul class="list-disc ml-6 text-sm text-gray-700 dark:text-gray-300 mb-4">
                    <li v-for="(p, index) in changedParams" :key="index">{{ p.label }}</li>
                </ul>

                <!-- TABLA COMPARATIVA -->
                <div class="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 border border-gray-300 dark:border-gray-700 mb-6">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="text-left text-gray-600 dark:text-gray-400 text-xs">
                                <th class="pb-2">Parámetro</th>
                                <th class="pb-2">Actual</th>
                                <th class="pb-2">Restaurado</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="p in changedParams" :key="p.key" class="border-t border-gray-200 dark:border-gray-700">
                                <td class="py-2 font-semibold text-gray-700 dark:text-gray-300">{{ p.label }}</td>
                                <td class="py-2 text-gray-600 dark:text-gray-400">{{ p.current }}</td>
                                <td class="py-2 text-[#102372] dark:text-[#ff6600] font-medium">{{ p.restored }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- BOTONES -->
                <div class="flex justify-end gap-3">
                    <button
                        @click="$emit('cancel')"
                        class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                        Cancelar
                    </button>

                    <button
                        @click="$emit('confirm', version)"
                        class="px-4 py-2 rounded-md text-sm text-white bg-[#102372] hover:bg-[#ff6600]">
                        Restaurar versión
                    </button>
                </div>

            </div>
        </div>
    </transition>
</template>

<script setup>
import { computed } from "vue"
import SvgIcon from "@/components/icons/SvgIcon.vue"

const props = defineProps({
    show: Boolean,
    version: Object,
    device: Object,
})

/* Detectar parámetros modificados */
const changedParams = computed(() => {
    if (!props.version?.snapshot || !props.device) return []

    const params = []

    const fields = {
        name: "Nombre",
        iccid: "ICCID",
        identifier: "Identificador / IMEI",
        token: "Token"
    }

    for (const key in fields) {
        if (props.version.snapshot[key] !== props.device[key]) {
            params.push({
                key,
                label: fields[key],
                current: props.device[key] ?? "—",
                restored: props.version.snapshot[key] ?? "—"
            })
        }
    }

    return params
})
</script>

<style>
.fade-enter-active, .fade-leave-active {
    transition: opacity .25s ease;
}
.fade-enter-from, .fade-leave-to {
    opacity: 0;
}

@keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}
.animate-scale-in {
    animation: scaleIn .25s ease;
}
</style>
