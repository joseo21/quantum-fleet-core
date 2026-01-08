<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[10000] flex items-center justify-center bg-black/50"
    >
      <div
        class="bg-white dark:bg-gray-900 rounded-xl w-full max-w-md shadow-xl"
      >

        <!-- HEADER -->
        <div class="px-4 py-3 border-b dark:border-gray-700 flex justify-between items-center">
          <h4 class="font-semibold text-gray-800 dark:text-gray-200">
            Insertar Script
          </h4>

          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ✕
          </button>
        </div>

        <!-- BODY -->
        <div class="p-6 text-sm text-gray-500 dark:text-gray-400 text-center">
          <!-- Modal vacío por ahora -->
        </div>

        <!-- FOOTER -->
        <div class="px-4 py-3 border-t dark:border-gray-700 flex justify-end">
          <button
            @click="$emit('close')"
            class="px-4 py-1.5 text-sm rounded-lg
                   bg-gray-200 hover:bg-gray-300
                   dark:bg-gray-700 dark:hover:bg-gray-600
                   text-gray-800 dark:text-gray-200 transition"
          >
            Cerrar
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    required: true
  }
});

defineEmits(["close"]);
</script>
