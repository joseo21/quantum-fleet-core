<template>
  <transition name="slide-right">
    <div v-if="showEditSidebar" class="fixed inset-0 z-50 flex justify-end">
      <div @click="$emit('close')" class="absolute inset-0 bg-black bg-opacity-50"></div>

      <div
        class="relative w-full max-w-md sm:w-96 bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-xl flex flex-col h-full">
        <div class="flex-1 overflow-y-auto p-6">
          <button @click="$emit('close')"
            class="self-end p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition mb-2">
            <SvgIcon name="close" class="w-6 h-6" />
          </button>
          <h2 class="text-2xl font-bold mb-4 text-[#102372] dark:text-[#ff6600]">Editar Empresa</h2>

          <form @submit.prevent="submitUpdateCompany" class="flex flex-col gap-3">
            <input v-model="localCompany.name" type="text" placeholder="Nombre de la empresa"
              class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              required />

            <input v-model="localCompany.rut" type="text" placeholder="RUT de la empresa"
              class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              required @input="formatRut" />

            <input v-model="localCompany.contact" type="text" placeholder="Contacto"
              class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              required />

            <input v-model="localCompany.city" type="text" placeholder="Ciudad de la empresa"
              class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none"
              required />

            <div class="mt-4">
              <label class="block mb-1 text-sm font-semibold text-[#102372] dark:text-[#ff6600]">Plantilla /
                Permisos:</label>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div v-for="template in templates" :key="template.id" @click="localCompany.templateId = template.id"
                  :class="[
                    'p-3 rounded-lg border cursor-pointer text-center transition',
                    localCompany.templateId === template.id
                      ? 'border-[#ff6600] bg-orange-100 dark:bg-[#e65500]/30'
                      : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                  ]">
                  <h3 class="font-semibold">{{ template.name }}</h3>
                  <p class="text-gray-500 dark:text-gray-400 text-sm">{{ template.description }}</p>
                </div>
              </div>
            </div>
          </form>
        </div>

        <div
          class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-center gap-2 bg-gray-50 dark:bg-gray-900">
          <button @click="submitUpdateCompany"
            class="bg-[#ff6600] hover:bg-[#e65500] px-4 py-2 rounded text-white font-medium">
            Guardar Cambios
          </button>
          <button @click="$emit('close')" class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded text-white">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'

const props = defineProps({
  showEditSidebar: { type: Boolean, required: true },
  editingCompany: { type: Object, required: true },
  templates: { type: Array, required: true }
})

const emit = defineEmits(['close', 'update-company'])

// Usamos una copia local para evitar modificar la prop directamente antes de guardar
const localCompany = ref({ ...props.editingCompany })

// Sincronizar localCompany cuando la prop editingCompany cambia
watch(() => props.editingCompany, (newVal) => {
  localCompany.value = { ...newVal }
}, { deep: true })


// Lógica de validación de RUT (necesaria para guardar)
const isValidRut = (rut) => /^(\d{1,2}\.\d{3}\.\d{3}-[\dkK])$/.test(rut)

// Formateo automático RUT mientras se escribe
const formatRut = () => {
  let rut = localCompany.value.rut.replace(/[^0-9kK]/g, '')
  if (rut.length > 9) rut = rut.slice(0, 9)

  if (rut.length > 1) {
    const body = rut.slice(0, -1)
    const dv = rut.slice(-1)
    const reversed = body.split('').reverse()
    const withDots = []
    reversed.forEach((char, i) => { if (i > 0 && i % 3 === 0) withDots.push('.'); withDots.push(char) })
    localCompany.value.rut = withDots.reverse().join('') + '-' + dv
  } else {
    localCompany.value.rut = rut
  }
}

// Guardar cambios
const submitUpdateCompany = () => {
  if (!isValidRut(localCompany.value.rut)) {
    alert('RUT inválido. Formato esperado: xx.xxx.xxx-x')
    return
  }

  // Enviamos la copia modificada al padre para su actualización
  emit('update-company', localCompany.value)
}
</script>

<style scoped>
/* Transiciones de la barra lateral (Se ha renombrado a 'slide-right' para claridad) */
/* El componente de la sidebar a animar es el que tiene la clase `w-full max-w-md sm:w-96 ...` */
.slide-right-enter-active {
  /* Aplicamos la transición solo al transform */
  transition: transform 0.3s ease-out; 
}

.slide-right-leave-active {
  /* Aplicamos la transición solo al transform */
  transition: transform 0.3s ease-in;
}

.slide-right-enter-from,
.slide-right-leave-to {
  /* Mueve la sidebar completamente fuera de la vista hacia la derecha (100% de su propio ancho) */
  transform: translateX(100%);
}

.slide-right-enter-to,
.slide-right-leave-from {
  /* Posición normal */
  transform: translateX(0);
}
</style>