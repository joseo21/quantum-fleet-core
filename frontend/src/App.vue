<template>
  <div class="flex min-h-screen">
    <!-- Sidebar -->
    <AppSidebar />

    <!-- Contenido principal -->
    <main class="flex-1 p-4 overflow-auto bg-white">
      <div class="w-full h-full bg-slate-100 rounded-lg">

      </div>
    </main>
  </div>
</template>

<script>


import AppSidebar from './components/Sidebar.vue'  // Nombre multi-word

export default {
  name: 'App',
  components: {
    AppSidebar

  }
}
</script>
<style></style>
