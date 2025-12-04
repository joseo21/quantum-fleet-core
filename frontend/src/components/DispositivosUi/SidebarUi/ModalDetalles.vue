<template>
    <transition name="fade">
        <div v-if="show" 
             class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[999] flex items-center justify-center"
             @click.self="$emit('close')">

            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 w-full max-w-lg
                        border border-gray-300 dark:border-gray-700 animate-scale-in">

                <!-- HEADER -->
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-[#102372] dark:text-[#ff6600]">
                        Detalles de la Versión {{ version?.version }}
                    </h2>

                    <button @click="$emit('close')" 
                        class="text-gray-600 hover:text-gray-800 dark:hover:text-gray-300">
                        <SvgIcon name="close" class="w-5 h-5" />
                    </button>
                </div>

                <!-- INFO PRINCIPAL -->
                <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
                    Registrada por <strong>{{ version?.user }}</strong>
                    el <strong>{{ formatDate(version?.date) }}</strong>.
                </p>

                <!-- DESCRIPCIÓN -->
                <p v-if="version?.changes" class="text-sm mb-4 text-gray-700 dark:text-gray-300 whitespace-pre-line">
                    <strong>Descripción:</strong><br>
                    {{ version.changes }}
                </p>

                <!-- TABLA DE CAMBIOS -->
                <div v-if="rows.length" class="mt-4">
                    <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        Cambios realizados:
                    </p>

                    <table class="w-full text-sm border-collapse">
                        <thead>
                            <tr class="text-left border-b border-gray-300 dark:border-gray-600">
                                <th class="py-1">Parámetro</th>
                                <th class="py-1">Antes</th>
                                <th class="py-1">Después</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="r in rows" :key="r.key"
                                class="border-b border-gray-200 dark:border-gray-700">
                                <td class="py-1 font-medium">{{ r.label }}</td>
                                <td class="py-1 text-gray-500">{{ r.before }}</td>
                                <td class="py-1 text-gray-900 dark:text-white">{{ r.after }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- BOTÓN -->
                <div class="flex justify-end mt-6">
                    <button
                        @click="$emit('close')"
                        class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 
                               text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700">
                        Cerrar
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
    version: Object
})

/* ===============================
   CAMPOS A MOSTRAR
================================ */
const fieldLabels = {
    name: "Nombre",
    iccid: "ICCID",
    identifier: "Identificador / IMEI",
    token: "Token"
}

/* ===============================
   GENERAR FILAS DE CAMBIOS
================================ */
const rows = computed(() => {
    const v = props.version

    if (!v || !v.before || !v.after) return []

    const out = []

    for (const key in fieldLabels) {
        if (v.before[key] !== v.after[key]) {
            out.push({
                key,
                label: fieldLabels[key],
                before: v.before[key] ?? "—",
                after: v.after[key] ?? "—"
            })
        }
    }

    return out
})

/* ===============================
   FECHA FORMATEADA
================================ */
function formatDate(dateStr) {
    return new Date(dateStr).toLocaleString("es-CL", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    })
}
</script>
