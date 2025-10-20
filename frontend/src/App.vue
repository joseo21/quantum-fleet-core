<template>
  <div class="min-h-screen flex flex-col bg-gray-100">
    <!-- Si NO estás en LoginAdmin -->
    <template v-if="!isLoginPage">
      <AppHeader :showProfile="showProfile" @toggle-sidebar="toggleSidebar" />

      <div class="flex flex-1">
        <AppSidebar v-model:isOpen="showSidebar" />

        <main class="flex-1 p-4 overflow-auto bg-gray-900">
          <router-view />
        </main>
      </div>
    </template>

    <!-- Si estás en login -->
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'

const route = useRoute()

const showSidebar = ref(false)
const showProfile = ref(false)

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}

// Detecta si estás en la ruta del login
const isLoginPage = computed(() => route.path === '/')
</script>
