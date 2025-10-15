<template>
  <div class="flex min-h-screen">
    <!-- Sidebar -->
    <AppSidebar v-model:isOpen="isSidebarOpen" />

    <!-- Contenido principal -->
    <main class="flex-1 p-4 overflow-auto bg-gray-900">
      <!-- Hamburger visible en mobile -->
      <button
        class="md:hidden mb-4 text-2xl text-white justify-center w-8 rounded-md bg-[#152c87] hover:bg-[#ff6600]"
        @click="isSidebarOpen = true"
      >
        ☰
      </button>

      <div class="w-full h-full bg-gray-800 rounded-lg p-4">
        <h1 class="text-xl font-bold text-white">Contenido Principal</h1>
      </div>
    </main>
  </div>
</template>

<script>
import AppSidebar from './components/Sidebar.vue'

export default {
  name: 'App',
  components: { AppSidebar },
  data() {
    return {
      isSidebarOpen: false
    }
  }
}
</script>
