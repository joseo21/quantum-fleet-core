<!-- SidebarUi/DetalleView.vue -->
<template>
  <div class="space-y-4">

    <!-- ======================= -->
    <!-- Nombre + botón Editar -->
    <!-- ======================= -->
    <div class="flex items-center justify-between">
      <label class="text-gray-500 text-xs">Nombre del Dispositivo</label>

      <!-- Botón EDITAR -->
      <button
        v-if="!isEditing"
        type="button"
        @click="$emit('edit')"
        class="flex items-center gap-1 px-2 py-1 rounded border border-gray-300 
               text-[11px] hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
      >
        <SvgIcon name="pencil" class="w-4 h-4" />
        Editar
      </button>
    </div>

    <!-- Campo Nombre -->
    <div>
      <input
        :value="name"
        :disabled="!isEditing"
        @input="$emit('update:name', $event.target.value)"
        class="w-full p-2 mt-1 border rounded-md dark:bg-gray-700
               focus:outline-none focus:ring-1 focus:ring-[#102372]
               disabled:bg-gray-200 dark:disabled:bg-gray-800 disabled:text-gray-500"
      />
    </div>

    <!-- ======================= -->
    <!-- ICCID (Editable) -->
    <!-- ======================= -->
    <div>
      <label class="text-gray-500 text-xs">ICCID (SIM Card)</label>

      <input
        :value="iccid"
        :disabled="!isEditing"
        @input="$emit('update:iccid', $event.target.value)"
        class="w-full p-2 mt-1 border rounded-md dark:bg-gray-700
               focus:outline-none focus:ring-1 focus:ring-[#102372]
               disabled:bg-gray-200 dark:disabled:bg-gray-800 disabled:text-gray-500"
        placeholder="Ej: 8955112309876543210"
      />
    </div>

    <!-- ======================= -->
    <!-- Fecha Creación (solo lectura) -->
    <!-- ======================= -->
    <div>
      <label class="text-gray-500 text-xs">Fecha de creación</label>
      <input
        type="date"
        :value="createdAt"
        disabled
        class="w-full p-2 mt-1 border rounded-md bg-gray-200 dark:bg-gray-800
               text-gray-500 cursor-not-allowed"
      />
    </div>

  </div>
</template>

<script setup>
import SvgIcon from '@/components/icons/SvgIcon.vue'

defineProps({
  name: String,
  iccid: String,          // ⭐ NUEVO CAMPO
  createdAt: String,
  isEditing: Boolean
})

defineEmits(['edit', 'update:name', 'update:iccid'])   // ⭐ EMIT NUEVO
</script>
