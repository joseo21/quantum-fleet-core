<template>
  <div class="space-y-3 max-h-[500px] overflow-y-auto p-1">

    <div class="hidden sm:flex items-center p-2 bg-gray-100 dark:bg-gray-800 rounded-md shadow-sm sticky top-0 z-10">
      <div class="w-8">
        <input type="checkbox" :checked="selectAll" @change="$emit('update:selectAll', $event.target.checked)"
          class="text-[#102372] focus:ring-[#102372] dark:focus:ring-[#ff6600] w-4 h-4" />
      </div>
      <h3 class="flex-1 text-xs font-semibold text-gray-700 dark:text-gray-200 ml-2">Seleccionar Todo</h3>
      <div class="w-20"></div>
    </div>

    <div v-for="customer in customers" :key="customer.id"
      class="bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700 shadow-sm p-3 transition duration-150 hover:shadow-md">

      <div class="flex items-center gap-3">

        <div class="flex-shrink-0">
          <input type="checkbox" :checked="selectedIds.includes(customer.id)" @change="toggleSelection(customer.id)"
            class="text-[#102372] focus:ring-[#102372] dark:focus:ring-[#ff6600] w-4 h-4" />
        </div>

        <div class="flex-1 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 text-xs">

          <div class="flex-shrink-0 w-full sm:w-1/3">
            <p class="text-sm font-semibold text-[#102372] dark:text-white truncate" title="Nombre de la empresa">{{
              customer.name }}</p>
            <p class="text-[10px] text-gray-500 dark:text-gray-400 truncate" title="Contacto">{{ customer.contact }}</p>
          </div>

          <div class="flex gap-4 flex-wrap sm:flex-nowrap sm:w-2/3">
            <div class="flex flex-col w-1/3 min-w-[80px]">
              <span class="text-gray-400 dark:text-gray-500 text-[9px] uppercase">RUT</span>
              <p class="font-medium text-gray-700 dark:text-gray-300 truncate">{{ customer.rut }}</p>
            </div>
            <div class="flex flex-col w-1/3 min-w-[80px]">
              <span class="text-gray-400 dark:text-gray-500 text-[9px] uppercase">Ciudad</span>
              <p class="font-medium text-gray-700 dark:text-gray-300 truncate">{{ customer.city }}</p>
            </div>
            <div class="flex-col w-1/3 min-w-[100px] hidden md:flex"> <span
                class="text-gray-400 dark:text-gray-500 text-[9px] uppercase">Creado el</span>
              <p class="text-xs text-gray-600 dark:text-gray-400">{{ customer.createdAt }}</p>
            </div>
          </div>

        </div>

        <div class="flex gap-1 flex-shrink-0">

          <button @click="$emit('edit-customer', customer)" title="Editar"
            class="bg-blue-600 hover:bg-blue-700 text-white p-1.5 rounded-full flex items-center justify-center transition">
            <SvgIcon name="pencil" class="w-4 h-4" />
          </button>

          <button @click="$emit('copy-customer-data', customer)" title="Copiar"
            class="p-1.5 bg-gray-800 text-white rounded-full hover:bg-gray-700 relative flex items-center justify-center transition">
            <SvgIcon name="copy" class="w-4 h-4" />
            <span v-if="copiedId === customer.id"
              class="absolute top-8 right-0 transform translate-x-1/2 bg-gray-700 text-white text-[10px] px-1.5 py-0.5 rounded whitespace-nowrap z-20">
              Copiado!
            </span>
          </button>

        </div>
      </div>
    </div>

    <div v-if="customers.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
      No hay empresas registradas
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'

const props = defineProps({
  customers: { type: Array, required: true },
  selectedIds: { type: Array, required: true },
  selectAll: { type: Boolean, required: true },
  copiedId: { type: [Number, null], required: true },
})

const emit = defineEmits(['update:selectedIds', 'update:selectAll', 'edit-customer', 'copy-customer-data'])

// Función para manejar la selección individual y emitir el array actualizado
const toggleSelection = (id) => {
  const newSelectedIds = [...props.selectedIds]
  const index = newSelectedIds.indexOf(id)

  if (index === -1) {
    newSelectedIds.push(id)
  } else {
    newSelectedIds.splice(index, 1)
  }
  emit('update:selectedIds', newSelectedIds)
}
</script>

<style scoped>
/* No se necesitan estilos con la implementación de Tailwind CSS */
</style>