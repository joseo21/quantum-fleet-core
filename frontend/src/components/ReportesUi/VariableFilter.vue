<template>
  <div ref="wrapper" class="relative w-full dropdown-trigger">

    <!-- BOTÓN PRINCIPAL -->
    <button
      @click="open = !open"
      class="w-full h-[46px] border border-gray-300 rounded-xl px-4 bg-white shadow-sm
             flex items-center justify-between text-sm text-gray-700 disabled:opacity-50
             transition"
      :disabled="props.variables.length === 0"
    >
      <!-- BLOQUE DE TEXTO -->
      <div class="flex flex-col justify-center leading-[1.1] text-left">
        
        <!-- TÍTULO -->
        <span class="text-[13px] font-medium text-gray-700">
          <template v-if="props.variables.length === 0">
            Sin variables disponibles
          </template>

          <template v-else>
            Variables seleccionadas
          </template>
        </span>

        <!-- CONTADOR -->
        <span
          v-if="props.variables.length > 0"
          class="text-[12px] text-gray-500 mt-[1px]"
        >
          {{ temp.length }} seleccionada(s)
        </span>

      </div>

      <!-- FLECHA (solo hover) -->
      <span
        class="dropdown-arrow text-xs text-gray-400 transition-transform duration-200"
        :class="{ 'rotate-180': open }"
      >
        ▼
      </span>
    </button>



    <!-- ===========================
         DROPDOWN
         =========================== -->
    <transition name="fade">
      <div
        v-if="open && props.variables.length > 0"
        class="absolute w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden"
      >

        <div class="max-h-60 overflow-y-auto p-2 text-sm">
          <div
            v-for="v in props.variables"
            :key="v.key"
            class="flex items-center gap-2 px-2 py-2 hover:bg-gray-50 cursor-pointer"
            @click="toggle(v.key)"
          >
            <input type="checkbox" class="w-4 h-4" :checked="temp.includes(v.key)" />
            <span class="text-gray-800">{{ v.label }}</span>
          </div>
        </div>

        <div class="flex justify-between p-3 border-t bg-gray-50">
          <button
            class="px-3 py-1.5 text-xs bg-gray-200 rounded-lg hover:bg-gray-300"
            @click="clear"
          >
            Limpiar
          </button>

          <button
            class="px-3 py-1.5 text-xs bg-[#102372] text-white rounded-lg hover:bg-[#0b1a55]"
            @click="apply"
          >
            Aceptar
          </button>
        </div>

      </div>
    </transition>

  </div>
</template>



<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue"

const props = defineProps({
  variables: { type: Array, default: () => [] }
})

const emit = defineEmits(["update:selected"])

const open = ref(false)
const temp = ref([])
const wrapper = ref(null)


// AUTOSELECCIÓN
watch(
  () => props.variables,
  (nv) => {
    if (nv?.length) {
      temp.value = nv.map((v) => v.key)
      emit("update:selected", [...temp.value])
    } else {
      temp.value = []
      emit("update:selected", [])
    }
  },
  { immediate: true }
)


function toggle(key) {
  temp.value = temp.value.includes(key)
    ? temp.value.filter((x) => x !== key)
    : [...temp.value, key]
}

function clear() {
  temp.value = []
  emit("update:selected", [])
}

function apply() {
  emit("update:selected", [...temp.value])
  open.value = false
}


// CERRAR AL HACER CLICK FUERA
function handleClick(e) {
  if (!wrapper.value?.contains(e.target)) open.value = false
}

onMounted(() => document.addEventListener("mousedown", handleClick))
onBeforeUnmount(() => document.removeEventListener("mousedown", handleClick))
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

/* FLECHA OCULTA POR DEFECTO */
.dropdown-arrow {
  opacity: 0;
}

/* FLECHA SE MUESTRA SOLO EN HOVER */
.dropdown-trigger:hover .dropdown-arrow {
  opacity: 1;
}

/* ROTACIÓN DE FLECHA CUANDO OPEN = TRUE */
.rotate-180 {
  transform: rotate(180deg);
}
</style>
