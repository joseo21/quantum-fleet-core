<template>
  <div class="min-h-screen flex flex-col bg-gray-100">
    <!-- Header -->
    <AppHeader :showProfile="showProfile" @toggle-sidebar="toggleSidebar" />

    <!-- Contenido principal -->
    <div class="flex flex-1">
      <!-- Sidebar -->
      <AppSidebar v-model:isOpen="showSidebar" />

      <!-- Main -->
      <main class="flex-1 p-4 overflow-auto bg-gray-900">
        <router-view /> <!-- Aquí se muestran tus vistas -->
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'

const showSidebar = ref(false)
const showProfile = ref(false)

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}
</script>
