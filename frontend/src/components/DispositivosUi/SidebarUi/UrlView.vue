<template>
    <div
        class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-8">

        <!-- ========================== -->
        <!-- 🟦 OPCIONES -->
        <!-- ========================== -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

            <!-- PROTOCOLO -->
            <div class="space-y-3">
                <p class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                    <SvgIcon name="protocol" class="w-4 h-4" /> Protocolo
                </p>

                <div class="flex flex-wrap gap-3">
                    <button
                        v-for="p in protocols"
                        :key="p"
                        disabled
                        class="px-4 py-2 rounded-lg border text-sm font-medium transition-all cursor-default select-none"
                        :class="[
                            activeProtocol === p
                                ? 'bg-[#102372] text-white border-[#102372] dark:bg-[#ff6600] dark:border-[#ff6600]'
                                : 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-500 dark:text-gray-500 opacity-50'
                        ]">
                        {{ p }}
                    </button>
                </div>
            </div>

            <!-- SISTEMA OPERATIVO -->
            <div class="space-y-3">
                <p class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                    <SvgIcon name="computer" class="w-4 h-4" /> Sistema Operativo
                </p>

                <div class="flex flex-wrap gap-3">
                    <button
                        v-for="tab in osList"
                        :key="tab.value"
                        @click="activeOs = tab.value"
                        class="px-4 py-2 rounded-lg border flex items-center gap-2 text-sm transition"
                        :class="activeOs === tab.value
                            ? 'border-[#102372] text-[#102372] dark:text-[#ff6600] dark:border-[#ff6600]'
                            : 'border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'">
                        <SvgIcon :name="tab.icon" class="w-4 h-4" />
                        {{ tab.label }}
                    </button>
                </div>
            </div>

        </div>

        <!-- ========================== -->
        <!-- 🟦 COMANDO GENERADO -->
        <!-- ========================== -->
        <div class="space-y-3">
            <div class="flex items-center justify-between">
                <p class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                    <SvgIcon name="terminal" class="w-4 h-4" /> Comando Generado
                </p>

                <button @click="copyCommand"
                    class="flex items-center gap-2 text-xs px-3 py-1.5 rounded-md border transition"
                    :class="copied
                        ? 'bg-green-100 border-green-300 text-green-700 dark:bg-green-900 dark:border-green-700 dark:text-green-300'
                        : 'bg-gray-100 border-gray-300 dark:bg-gray-800 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'">
                    <SvgIcon :name="copied ? 'check' : 'copy'" class="w- h-5" />
                    {{ copied ? 'Copiado' : 'Copiar' }}
                </button>
            </div>

            <div
                class="relative bg-gray-900 dark:bg-black border border-gray-800 dark:border-gray-700 rounded-lg p-4 overflow-x-auto shadow-inner">
                <pre
                    class="text-gray-100 text-xs font-mono whitespace-nowrap break-normal leading-relaxed overflow-x-auto px-4 py-3">
                    {{ command }}
                </pre>

                <div
                    class="absolute top-3 right-3 px-2 py-0.5 text-[10px] rounded-full border border-blue-800/60 text-blue-300 bg-blue-900/30">
                    {{ activeProtocol }}
                </div>
            </div>

            <!-- INFO -->
            <p class="text-xs text-gray-500 dark:text-gray-400 italic">
                {{ getInstructionText() }}
            </p>
        </div>

    </div>
</template>

<script setup>
import { computed, ref, watch } from "vue"
import SvgIcon from "@/components/icons/SvgIcon.vue"

const props = defineProps({
    deviceId: Number,
    token: String,
    tipo: { type: String } // 👈 VIENE DEL DISPOSITIVO: "TCP", "HTTP", "MQTT"
})

/* === PROTOCOLOS === */
const protocols = ["TCP", "HTTP", "MQTT"]

// 🔥 Se establece según el dispositivo y NO se puede cambiar
const activeProtocol = ref("HTTP")

watch(
    () => props.tipo,
    (nuevo) => {
        if (protocols.includes(nuevo)) activeProtocol.value = nuevo
    },
    { immediate: true }
)

/* === SISTEMAS OPERATIVOS === */
const osList = [
    { value: "windows", label: "Windows", icon: "windows" },
    { value: "mac", label: "MacOS", icon: "apple" },
    { value: "linux", label: "Linux", icon: "linux" }
]
const activeOs = ref("windows")

/* === COMANDOS === */
const command = computed(() => {
    const baseUrl = `https://api.safco.cl/device/${props.deviceId}/push/${props.token || ""}`
    const host = baseUrl.replace("https://", "")

    if (activeOs.value === "windows") {
        if (activeProtocol.value === "TCP") return `nc64.exe ${host} 9000`
        if (activeProtocol.value === "MQTT")
            return `mosquitto_pub.exe -h api.safco.cl -t "device/${props.deviceId}" -m "{\\"dato\\":123}"`
        return `curl -Method POST -Uri "${baseUrl}" -Body "{\\"dato\\":123}" -ContentType "application/json"`
    }

    if (activeProtocol.value === "TCP") return `nc ${host} 9000`
    if (activeProtocol.value === "MQTT")
        return `mosquitto_pub -h api.safco.cl -t "device/${props.deviceId}" -m '{"dato":123}'`

    return `curl -X POST "${baseUrl}" -d '{"dato":123}' -H "Content-Type: application/json"`
})

/* INFO */
const getInstructionText = () => {
    if (activeProtocol.value === "TCP") return "Ejecuta el comando correspondiente a tu sistema operativo."
    if (activeProtocol.value === "MQTT") return "Asegúrate de tener mosquitto instalado."
    return "Pega este comando en tu terminal."
}

/* COPIAR */
const copied = ref(false)
const copyCommand = () => {
    navigator.clipboard.writeText(command.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 1200)
}
</script>
    