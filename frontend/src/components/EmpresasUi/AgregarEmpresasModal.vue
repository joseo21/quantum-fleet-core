<template>
  <transition name="modal-fade">
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div
        class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white rounded-lg relative flex flex-col w-full max-w-lg h-auto p-6 border border-gray-300 dark:border-gray-700 shadow-xl">

        <button v-if="step === 2" @click="step = 1"
          class="absolute top-4 left-4 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition" title="Volver">
          <SvgIcon name="arrow-left" class="w-6 h-6" />
        </button>

        <h2 class="text-2xl font-bold mb-4 text-center text-[#102372] dark:text-[#ff6600]">
          {{ step === 1 ? 'Agregar Empresa' : 'Seleccionar Template' }}
        </h2>

        <span class="h-px bg-gray-300 dark:bg-gray-700 mb-4"></span>

        <form v-if="step === 1" @submit.prevent="goToNextStep" class="flex-1 flex flex-col gap-3 py-2 overflow-y-auto">
          <input v-model="newCompany.name" type="text" placeholder="Nombre de la empresa"
            class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
            required />

          <input v-model="newCompany.rut" type="text" placeholder="RUT de la empresa"
            class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
            required @input="formatRut" />

          <input v-model="newCompany.contact" type="text" placeholder="Contacto"
            class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
            required />

          <input v-model="newCompany.city" type="text" placeholder="Ciudad de la empresa"
            class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
            required />
        </form>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4">
          <div v-for="template in templates" :key="template.id" @click="selectedTemplate = template.id" :class="[
            'p-6 rounded-lg border cursor-pointer text-center transition',
            selectedTemplate === template.id
              ? 'border-[#ff6600] bg-orange-100 dark:bg-[#e65500]/30'
              : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
          ]">
            <h3 class="text-lg font-semibold mb-2">{{ template.name }}</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm">{{ template.description }}</p>
          </div>
        </div>

        <div class="flex justify-between mt-6">
          <button @click="$emit('close')" class="bg-gray-500 hover:bg-gray-600 px-4 py-2 rounded w-[48%] text-white">
            Cancelar
          </button>

          <button v-if="step === 1" @click="goToNextStep" :disabled="!isStep1Valid"
            :class="['px-4 py-2 rounded w-[48%] text-white font-medium', isStep1Valid ? 'bg-[#102372] hover:bg-[#0c1a5b]' : 'bg-[#102372]/50 cursor-not-allowed']">
            {{ modalButtonText }}
          </button>

          <button v-else @click="submitAddCompany" :disabled="isModalButtonDisabled"
            :class="['px-4 py-2 rounded w-[48%] text-white font-medium', isModalButtonDisabled ? 'bg-[#ff6600]/50 cursor-not-allowed' : 'bg-[#ff6600] hover:bg-[#e65500]']">
            {{ modalButtonText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'

// eslint-disable-next-line no-undef
const props = defineProps({
  showAddModal: { type: Boolean, required: true },
  templates: { type: Array, required: true }
})

// eslint-disable-next-line no-undef
const emit = defineEmits(['close', 'add-company'])

// Estado interno del modal
const step = ref(1)
const selectedTemplate = ref(null)
const newCompany = ref({ name: '', rut: '', contact: '', city: '' })

// Lógica de validación de RUT (necesaria para el paso 1)
const isValidRut = (rut) => /^(\d{1,2}\.\d{3}\.\d{3}-[\dkK])$/.test(rut)

// Formateo automático RUT mientras se escribe
const formatRut = () => {
  let rut = newCompany.value.rut.replace(/[^0-9kK]/g, '')
  if (rut.length > 9) rut = rut.slice(0, 9)

  if (rut.length > 1) {
    const body = rut.slice(0, -1)
    const dv = rut.slice(-1)
    const reversed = body.split('').reverse()
    const withDots = []
    reversed.forEach((char, i) => { if (i > 0 && i % 3 === 0) withDots.push('.'); withDots.push(char) })
    newCompany.value.rut = withDots.reverse().join('') + '-' + dv
  } else {
    newCompany.value.rut = rut
  }
}

// Validación paso 1: todos los campos requeridos + RUT válido
const isStep1Valid = computed(() => {
  const { name, rut, contact, city } = newCompany.value
  return name.trim() && rut.trim() && contact.trim() && city.trim() && isValidRut(rut)
})

// Navegación
const goToNextStep = () => {
  if (isStep1Valid.value) step.value = 2
  else alert('Completa todos los campos correctamente antes de continuar.')
}

// Envío de la nueva empresa
const submitAddCompany = () => {
  if (!selectedTemplate.value) return 

  // Enviamos los datos al padre para que él se encargue de la lógica de guardado y manejo de array
  emit('add-company', { ...newCompany.value, templateId: selectedTemplate.value })
  
  // Resetear el estado del modal (simula el 'cancel' del padre)
  step.value = 1
  selectedTemplate.value = null
  newCompany.value = { name: '', rut: '', contact: '', city: '' }
}

// Lógica para cerrar con ESCAPE
const handleEscape = (e) => {
  if (props.showAddModal && e.key === 'Escape') {
    emit('close')
  }
}

// Añadir y remover el listener al montar/desmontar el componente
onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})

// Computed para texto dinámico de botones en modal
const modalButtonText = computed(() => step.value === 1 ? 'Siguiente' : 'Crear Empresa')
const isModalButtonDisabled = computed(() => step.value === 2 && !selectedTemplate.value)

// Watcher para resetear el estado del modal cuando se oculta
watch(() => props.showAddModal, (newValue) => {
  if (!newValue) {
    // Resetear el estado al cerrar
    step.value = 1
    selectedTemplate.value = null
    newCompany.value = { name: '', rut: '', contact: '', city: '' }
  }
})
</script>

<style scoped>
/* 🔴 ESTILOS DE TRANSICIÓN AÑADIDOS */
.modal-fade-enter-active,
.modal-fade-leave-active {
  /* Duración y tipo de transición */
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  /* Estado inicial (oculto) y final (saliendo) */
  opacity: 0;
}
/* Opcionalmente, puedes añadir un ligero efecto de escala para el contenido del modal */
.modal-fade-enter-active > div,
.modal-fade-leave-active > div {
  transition: transform 0.3s cubic-bezier(0.3, 0.7, 0.4, 1.5);
}

.modal-fade-enter-from > div,
.modal-fade-leave-to > div {
  transform: scale(0.95);
}
</style>