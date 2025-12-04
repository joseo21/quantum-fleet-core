<template>
    <div class="space-y-6">

        <!-- LISTA DE VERSIONES -->
        <div class="space-y-4 max-h-[400px] overflow-y-auto pr-1">

            <div
                v-for="v in formattedVersions"
                :key="v.version"
                class="border border-gray-200 dark:border-gray-700 rounded-xl p-4 bg-white dark:bg-gray-800 shadow-md hover:shadow-lg transition"
            >

                <div class="flex justify-between items-start">

                    <div class="space-y-1">

                        <!-- TÍTULO -->
                        <p class="text-sm font-bold text-[#102372] dark:text-[#ff6600]">
                            {{ v.title }}
                        </p>

                        <!-- FECHA -->
                        <p class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                            <SvgIcon name="calendar" class="w-3 h-3" /> 
                            {{ formatDate(v.date) }}
                        </p>

                        <!-- USUARIO -->
                        <p class="text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1">
                            <SvgIcon name="user" class="w-3 h-3" />
                            Registrado por: <span class="font-medium">{{ v.user }}</span>
                        </p>

                        <!-- PARÁMETROS MODIFICADOS -->
                        <div v-if="v.paramsChanged.length" class="mt-2">
                            <p class="text-xs font-semibold text-gray-700 dark:text-gray-300">
                                Parámetros afectados:
                            </p>

                            <ul class="list-disc ml-5 text-xs text-gray-600 dark:text-gray-400">
                                <li v-for="p in v.paramsChanged" :key="p">{{ p }}</li>
                            </ul>
                        </div>

                    </div>

                    <!-- BOTONES -->
                    <button
                        v-if="!v.isRollback"
                        @click="$emit('confirm-rollback', v)"
                        class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-500
                               text-xs font-medium flex items-center gap-1
                               hover:bg-gray-100 dark:hover:bg-gray-700 transition"
                    >
                        <SvgIcon name="rotate-left" class="w-4 h-4" />
                        Restaurar
                    </button>

                    <button
                        v-else
                        @click="$emit('show-details', v)"
                        class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-500
                               text-xs font-medium flex items-center gap-1
                               hover:bg-gray-100 dark:hover:bg-gray-700 transition"
                    >
                        <SvgIcon name="info" class="w-4 h-4" />
                        Ver detalles
                    </button>

                </div>

                <!-- DESCRIPCIÓN -->
                <p 
                    v-if="v.changes"
                    class="text-sm text-gray-600 dark:text-gray-300 mt-3 whitespace-pre-line leading-relaxed"
                >
                    {{ v.changes }}
                </p>

            </div>

            <p v-if="!formattedVersions.length"
                class="text-center text-sm text-gray-500 dark:text-gray-400 py-4">
                No hay versiones registradas para este dispositivo.
            </p>

        </div>
    </div>
</template>

<script setup>
import { computed } from "vue"
import SvgIcon from "@/components/icons/SvgIcon.vue"

const props = defineProps({
    versions: Array
})

/* ============================================
   LABELS
============================================ */
const FIELD_LABELS = {
    name: "Nombre",
    iccid: "ICCID",
    identifier: "Identificador / IMEI",
    token: "Token"
}

/* ============================================
   FORMATEAR LISTA Y LOGS
============================================ */
const formattedVersions = computed(() => {
    console.log("🟦 Versions recibidas:", props.versions)

    const list = [...props.versions]
        .sort((a, b) => b.version - a.version)
        .map(v => {
            console.log("––––––––––––––––––––––––––––––")
            console.log("🟧 Procesando versión:", v.version)
            console.log("Contenido:", v)

            const isRollback = v.changes?.toLowerCase().includes("rollback")
            console.log("➡ ¿Es rollback?", isRollback)

            const paramsChanged = extractParams(v)
            console.log("➡ Parámetros detectados como cambiados:", paramsChanged)

            const finalChanges = v.changes || generateRollbackDescription(v)
            console.log("➡ Texto final de 'changes':", finalChanges)

            return {
                ...v,
                isRollback,
                title: generateTitle(v),
                paramsChanged,
                changes: finalChanges
            }
        })

    console.log("🟩 LISTA FORMATEADA FINAL:", list)
    return list
})

/* ============================================
   DETECTAR CAMBIOS Y LOGS
============================================ */
function extractParams(v) {
    let params = []

    const fields = {
        name: "Nombre",
        iccid: "ICCID",
        identifier: "Identificador / IMEI",
        token: "Token"
    }

    // -------------------------------
    // CASO NORMAL (actualización)
    // -------------------------------
    if (!v.isRollback) {
        if (v.before && v.after) {
            for (const key in fields) {
                if (v.before[key] !== v.after[key]) {
                    params.push(
                        `${fields[key]}: "${v.before[key] ?? "—"}" → "${v.after[key] ?? "—"}"`
                    )
                }
            }
        }
        return params
    }

    // -------------------------------
    // CASO ROLLBACK
    // -------------------------------
    if (v.before && v.after) {
        for (const key in fields) {
            if (v.before[key] !== v.after[key]) {
                params.push(
                    `${fields[key]}: "${v.before[key] ?? "—"}" → "${v.after[key] ?? "—"}"`
                )
            }
        }
    }

    return params
}

/* ============================================
   GENERAR DESCRIPCIÓN Y LOGS
============================================ */
function generateRollbackDescription(v) {
    console.log("🟣 generateRollbackDescription() para versión", v.version)

    if (!v.snapshot || !v.beforeSnapshot) {
        console.log("   ❌ No se puede generar descripción: faltan datos.")
        return v.changes
    }

    console.log("   snapshot:", v.snapshot)
    console.log("   beforeSnapshot:", v.beforeSnapshot)

    let text = v.changes || `Rollback aplicado`

    text += "\n\n"

    for (const key in FIELD_LABELS) {
        const before = v.beforeSnapshot[key]
        const after = v.snapshot[key]

        console.log(`   🔍 Campo ${key}: BEFORE="${before}" AFTER="${after}"`)

        if (before !== after) {
            text += `• ${FIELD_LABELS[key]}: "${before}" → "${after}"\n`
            console.log("   ✔ Registrado en descripción")
        } else {
            console.log("   ✘ No se registra (no cambió)")
        }
    }

    console.log("   📝 Descripción generada:", text)
    return text.trim()
}

/* ============================================
   TITULO Y LOGS
============================================ */
function generateTitle(v) {
    console.log("🟩 generateTitle() versión", v.version)

    const text = v.changes?.toLowerCase() || ""

    if (text.includes("rollback")) {
        const match = v.changes.match(/versi[oó]n\s*#?(\d+)/i)
        const restoredVersion = match ? match[1] : null

        console.log("   ↳ Restored version encontrada:", restoredVersion)

        return restoredVersion
            ? `Versión ${v.version} — Punto de Restauración (restaurado desde Versión ${restoredVersion})`
            : `Versión ${v.version} — Punto de Restauración`
    }

    return `Versión ${v.version} — Actualización de Parámetros`
}

/* ============================================
   FORMATEAR FECHA
============================================ */
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
