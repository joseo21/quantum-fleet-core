<template>
  <div class="space-y-6">

    <!-- HEADER -->
    <div class="flex items-center gap-2">
      <div class="p-2 rounded-xl bg-[#102372]/10 dark:bg-[#ff6600]/10">
        <SvgIcon name="script" class="w-5 h-5 text-[#102372] dark:text-[#ff6600]" />
      </div>

      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
        Modificar Variables (Python)
      </h3>
    </div>

    <p class="text-sm text-gray-600 dark:text-gray-400">
      Ejecuta scripts Python para modificar parámetros del dispositivo.
    </p>

    <!-- VARIABLES DISPONIBLES -->
    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 shadow-sm">
      <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        Variables del Dispositivo
      </h4>

      <div class="grid grid-cols-2 gap-y-1 text-sm">
        <div v-for="v in variableList" :key="v.key" class="flex justify-between pr-4">
          <span class="font-medium text-gray-700 dark:text-gray-300">{{ v.key }}</span>
          <span class="font-mono text-gray-500 dark:text-gray-400">{{ v.value }}</span>
        </div>
      </div>
    </div>

    <!-- EDITOR -->
    <div class="space-y-2">
      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Script Python</label>

      <div class="relative bg-[#1e1e1e] rounded-xl shadow-lg overflow-hidden">

        <!-- LINE NUMBERS -->
        <div
          ref="lineBox"
          class="absolute left-0 top-0 bottom-0 w-12 bg-[#252526] text-gray-400 text-sm font-mono py-3 px-2 select-none overflow-hidden"
        >
          <div v-for="n in lineCount" :key="n" class="leading-6">
            {{ n }}
          </div>
        </div>

        <!-- TEXTAREA -->
        <textarea
          v-model="script"
          ref="editor"
          class="w-full h-[300px] bg-transparent text-sm font-mono leading-6 resize-none pl-14 pr-3 py-3 text-white
                 focus:outline-none caret-orange-400 overflow-auto"
          @input="updateLines"
          @scroll="syncScroll"
          placeholder="# variables['litros_totales'] = 500"
        ></textarea>
      </div>
    </div>

    <!-- BOTÓN EJECUTAR -->
    <button
      @click="executeScript"
      :disabled="running"
      class="w-full py-3 rounded-xl text-white font-semibold flex items-center justify-center gap-2
             bg-[#102372] hover:bg-[#143ba7] disabled:opacity-50 disabled:cursor-not-allowed
             dark:bg-[#ff6600] dark:hover:bg-[#ff7d26]"
    >
      <span v-if="!running">Ejecutar Script</span>
      <span v-else>Ejecutando…</span>
    </button>

    <!-- OUTPUT -->
    <div
      v-if="output"
      class="bg-black text-green-400 font-mono text-sm p-4 rounded-xl shadow-inner whitespace-pre-wrap"
    >
      {{ output }}
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import SvgIcon from "@/components/icons/SvgIcon.vue"

const props = defineProps({ device: Object })

/* ===========================
   LIMPIAMOS VARIABLES
=========================== */
const variableList = computed(() => {
  if (!props.device) return []

  const clean = []

  // VARIABLES BÁSICAS
  if (props.device.name) clean.push({ key: "nombre", value: props.device.name })
  if (props.device.imei) clean.push({ key: "imei", value: props.device.imei })
  if (props.device.iccid) clean.push({ key: "iccid", value: props.device.iccid })
  if (props.device.token) clean.push({ key: "token", value: props.device.token })

  // ULTIMO DATO DE TELEMETRÍA
  const data = props.device.data
  if (Array.isArray(data) && data.length > 0) {
    const last = data[0] // el más reciente

    clean.push({ key: "nivel_estanque", value: last.value || "—" })

    const search = (k) =>
      data.find((x) => x.key === k)?.value ?? "—"

    const varsToAdd = [
      "litros_totales",
      "voltaje",
      "gps_lat",
      "gps_lng",
      "rpm_motor",
      "temperatura_motor",
      "velocidad",
    ]

    varsToAdd.forEach((k) => clean.push({ key: k, value: search(k) }))
  }

  return clean
})

/* ==================================
   EDITOR
================================== */
const script = ref(`# variables['nivel_estanque'] = 80
# variables['litros_totales'] = 15000`)

const editor = ref(null)
const lineBox = ref(null)

const lineCount = ref(3)

const updateLines = () => {
  lineCount.value = script.value.split("\n").length
}

const syncScroll = () => {
  lineBox.value.scrollTop = editor.value.scrollTop
}

/* ==================================
   EJECUTAR (SIMULADO)
================================== */
const running = ref(false)
const output = ref(null)

const executeScript = async () => {
  running.value = true
  output.value = null

  await new Promise((r) => setTimeout(r, 1200))

  output.value =
`> Script recibido:
---------------------------
${script.value}

✔ Script enviado al backend.
✔ Validación simulada OK.`

  running.value = false
}
</script>

<style scoped>
textarea::-webkit-scrollbar {
  width: 8px;
}
textarea::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}
textarea::-webkit-scrollbar-track {
  background: #1e1e1e;
}
</style>
