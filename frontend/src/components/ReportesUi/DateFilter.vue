<template>
  <div ref="wrapper" class="relative w-full dropdown-trigger">

    <!-- BOTÓN PRINCIPAL -->
    <button
      @click="open = !open"
      class="w-full h-[46px] border border-gray-300 rounded-xl px-4 bg-white shadow-sm
             flex items-center justify-between text-sm text-gray-700 transition"
    >
      <span class="font-medium">
        {{ currentLabel }}
      </span>

      <span
        class="dropdown-arrow text-xs text-gray-400 transition-transform duration-200"
        :class="{ 'rotate-180': open }"
      >
        ▼
      </span>
    </button>

    <!-- DROPDOWN -->
    <transition name="fade">
      <div
        v-if="open"
        class="absolute w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg z-[999] overflow-hidden"
      >
        <div class="max-h-96 overflow-y-auto text-sm">

          <!-- RANGOS RÁPIDOS -->
          <button
            @click="quickOpen = !quickOpen"
            class="w-full px-4 py-2 flex items-center justify-between text-xs font-semibold
                   uppercase border-b bg-[#e5e7ff] text-[#102372]"
          >
            <span>Rangos rápidos</span>
            <span class="text-[10px]">
              {{ quickOpen ? '▲' : '▼' }}
            </span>
          </button>

          <transition name="fade">
            <div v-if="quickOpen" class="py-2">
              <button
                v-for="opt in presetOptions"
                :key="opt.value"
                class="w-full text-left px-6 py-2 hover:bg-gray-50 flex items-center gap-2"
                @click="selectPreset(opt.value)"
              >
                <span
                  class="inline-block w-2 h-2 rounded-full"
                  :class="selectedPreset === opt.value ? 'bg-[#102372]' : 'bg-gray-300'"
                />
                <span class="text-gray-800">{{ opt.label }}</span>
              </button>
            </div>
          </transition>

          <!-- RANGO PERSONALIZADO -->
          <div class="bg-gray-50 px-4 py-2 text-xs font-semibold text-gray-600 uppercase border-t">
            Rango personalizado
          </div>

          <div class="px-4 pb-4 pt-3 space-y-3">

            <div class="flex flex-col gap-1">
              <span class="text-xs text-gray-600">Desde</span>
              <input
                v-model="customFrom"
                type="date"
                class="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-sm
                       focus:ring-2 focus:ring-[#102372] focus:outline-none"
              />
            </div>

            <div class="flex flex-col gap-1">
              <span class="text-xs text-gray-600">Hasta</span>
              <input
                v-model="customTo"
                type="date"
                class="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-sm
                       focus:ring-2 focus:ring-[#102372] focus:outline-none"
              />
            </div>

            <!-- BOTONES -->
            <div class="grid grid-cols-2 gap-2 pt-2">
              <button
                class="px-3 py-2 rounded-lg bg-gray-200 text-gray-700 text-sm font-medium
                       hover:bg-gray-300"
                @click="clearRange"
              >
                Limpiar
              </button>

              <button
                class="px-3 py-2 rounded-lg bg-[#102372] text-white text-sm font-medium
                       disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#0b1a55]"
                :disabled="!customFrom || !customTo"
                @click="applyCustom"
              >
                Aplicar
              </button>
            </div>

          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue"

const emit = defineEmits(["update:range"])

const open = ref(false)
const quickOpen = ref(true)
const wrapper = ref(null)

const selectedPreset = ref("last_24h")
const customFrom = ref("")
const customTo = ref("")

const presetOptions = [
  { value: "last_1h", label: "Última hora" },
  { value: "last_12h", label: "Últimas 12 horas" },
  { value: "last_24h", label: "Últimas 24 horas" },
  { value: "last_7d", label: "Última semana" },
  { value: "last_30d", label: "Último mes" },
  { value: "last_180d", label: "Últimos 6 meses" }
]

const currentLabel = computed(() => {
  if (customFrom.value && customTo.value) return "Rango personalizado"
  const f = presetOptions.find(p => p.value === selectedPreset.value)
  return f ? f.label : "Rango de fecha"
})

function selectPreset(value) {
  selectedPreset.value = value
  customFrom.value = ""
  customTo.value = ""
  emit("update:range", { type: "preset", value })
  open.value = false
}

function applyCustom() {
  emit("update:range", {
    type: "custom",
    from: customFrom.value,
    to: customTo.value
  })
  open.value = false
}

function clearRange() {
  customFrom.value = ""
  customTo.value = ""
  selectedPreset.value = "last_24h"

  emit("update:range", {
    type: "preset",
    value: selectedPreset.value
  })

  open.value = false
}

function handleClick(e) {
  if (wrapper.value && !wrapper.value.contains(e.target)) open.value = false
}

onMounted(() => {
  emit("update:range", { type: "preset", value: selectedPreset.value })
  document.addEventListener("mousedown", handleClick)
})

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", handleClick)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity .15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.dropdown-arrow {
  opacity: 0;
}
.dropdown-trigger:hover .dropdown-arrow {
  opacity: 1;
}
.rotate-180 {
  transform: rotate(180deg);
}
</style>
