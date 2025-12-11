<template>
  <div ref="wrapper" class="relative w-full dropdown-trigger">

    <!-- INPUT + TAGS (YA NO HACE TOGGLE, SOLO ABRE) -->
    <div
      class="w-full h-[46px] border border-gray-300 rounded-xl px-4 bg-white shadow-sm
             flex items-center gap-2 cursor-text relative"
      @click="openDropdown"
    >

      <!-- INPUT -->
      <input
        ref="inputRef"
        v-model="search"
        @focus="open = true"
        type="text"
        placeholder="Buscar dispositivos..."
        class="flex-1 bg-transparent outline-none text-sm text-gray-700 min-w-[150px]"
      />

      <!-- TAGS + SCROLL -->
      <div
        class="flex items-center gap-2 max-w-[55%] overflow-x-auto whitespace-nowrap scrollbar-tags pb-3 mr-6"
      >
        <span
          v-for="d in selectedDevices"
          :key="d.id"
          class="px-2 py-0.5 text-xs rounded-full bg-[#102372]/10 text-[#102372]
                 flex items-center gap-1 shrink-0"
        >
          {{ d.nombre }}
          <button class="text-xs leading-none" @click.stop="remove(d.id)">✕</button>
        </span>
      </div>

      <!-- FLECHA — SOLO ESTA HACE TOGGLE -->
      <span
        class="absolute right-3 text-gray-400 text-xs dropdown-arrow cursor-pointer
               transition-transform duration-200"
        :class="{ 'rotate-180': open }"
        @click.stop="toggleDropdown"
      >
        ▼
      </span>

    </div>



    <!-- DROPDOWN -->
    <transition name="fade">
      <div
        v-if="open"
        class="absolute w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden"
      >
        <div class="max-h-60 overflow-y-auto">

          <div
            v-for="d in filtered"
            :key="d.id"
            class="flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-gray-50"
            @click="toggle(d.id)"
          >
            <input type="checkbox" class="w-4 h-4" :checked="temp.includes(d.id)" />
            <span class="text-sm text-gray-800">{{ d.nombre }}</span>
          </div>

          <div v-if="filtered.length === 0" class="px-3 py-3 text-sm text-gray-500">
            Sin resultados
          </div>
        </div>

        <!-- BOTONES -->
        <div class="p-3 border-t bg-gray-50 flex justify-between">
          <button class="px-3 py-1 text-sm bg-gray-200 rounded-lg" @click="clear">
            Limpiar
          </button>
          <button class="px-3 py-1 text-sm bg-[#102372] text-white rounded-lg" @click="apply">
            Aceptar
          </button>
        </div>

      </div>
    </transition>

  </div>
</template>



<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue"

const props = defineProps({ dispositivos: Array })
const emit = defineEmits(["update:selected"])

const open = ref(false)
const search = ref("")
const temp = ref([])
const confirmed = ref([])

const wrapper = ref(null)
const inputRef = ref(null)



// =============================
// ABRIR SOLO (sin toggle)
// =============================
function openDropdown() {
  open.value = true
  inputRef.value?.focus()
}

// =============================
// FLECHA HACE EL TOGGLE REAL
// =============================
function toggleDropdown() {
  open.value = !open.value
  if (open.value) inputRef.value?.focus()
}



// =============================
// FILTRADO
// =============================
const filtered = computed(() =>
  props.dispositivos.filter(d =>
    d.nombre.toLowerCase().includes(search.value.toLowerCase())
  )
)

const selectedDevices = computed(() =>
  props.dispositivos.filter(d => confirmed.value.includes(d.id))
)



// =============================
// LOGICA DE SELECCION
// =============================
function toggle(id) {
  temp.value = temp.value.includes(id)
    ? temp.value.filter(x => x !== id)
    : [...temp.value, id]
}

function clear() {
  temp.value = []
  confirmed.value = []
  emit("update:selected", [])
}

function apply() {
  confirmed.value = [...temp.value]
  emit("update:selected", confirmed.value)
  open.value = false
}

function remove(id) {
  confirmed.value = confirmed.value.filter(x => x !== id)
  temp.value = temp.value.filter(x => x !== id)
  emit("update:selected", confirmed.value)
}



// =============================
// CLICK FUERA → CERRAR
// =============================
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

/* SCROLL PERFECTO */
.scrollbar-tags::-webkit-scrollbar {
  height: 6px;
}
.scrollbar-tags::-webkit-scrollbar-thumb {
  background: #999;
  border-radius: 4px;
}

/* FLECHA: aparece en hover como el resto */
.dropdown-arrow {
  opacity: 0;
}
.dropdown-trigger:hover .dropdown-arrow {
  opacity: 1;
}

/* Giro suave */
.rotate-180 {
  transform: rotate(180deg);
}
</style>
