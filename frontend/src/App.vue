<template>
  <div class="fixed inset-0 flex flex-col bg-gray-50 overflow-hidden font-sans">
    <!-- Si NO estás en LoginAdmin -->
    <template v-if="!isLoginPage">
      <AppHeader :showProfile="showProfile" @toggle-sidebar="toggleSidebar" />


      <div class="flex flex-1 overflow-hidden">
        <AppSidebar v-model:isOpen="showSidebar" />

        <main class="flex-1 p-6 overflow-auto bg-[#f3f3f3]">
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
import AppHeader from './components/Layout/AppHeader.vue'
import AppSidebar from './components/Layout/AppSidebar.vue'

const route = useRoute()

const showSidebar = ref(false)
const showProfile = ref(false)

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}

// Detecta si estás en la ruta del login
const isLoginPage = computed(() => route.path === '/')
</script>
