<template>
  <div class="mx-auto bg-gray-400 min-h-screen flex flex-col">
    <!-- Header -->

    <!-- Body -->
    <div class="flex flex-1">
      <!-- Sidebar -->
      <aside
        v-show="showSidebar"
        class="bg-gray-800 text-white w-1/5 p-4 hidden md:block"
      >
        <ul>
          <li class="py-2 hover:bg-gray-700 px-2 rounded">Dashboard</li>
          <li class="py-2 hover:bg-gray-700 px-2 rounded">Users</li>
          <li class="py-2 hover:bg-gray-700 px-2 rounded">Reports</li>
        </ul>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 bg-gray-100 p-4">
        <h2 class="text-xl font-bold mb-4">Resumen General</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-blue-600 text-white rounded-lg p-4 shadow">
            <h3 class="text-2xl font-bold">$244</h3>
            <p>Total Sales</p>
          </div>
          <div class="bg-green-600 text-white rounded-lg p-4 shadow">
            <h3 class="text-2xl font-bold">$199.4</h3>
            <p>Total Cost</p>
          </div>
          <div class="bg-yellow-500 text-white rounded-lg p-4 shadow">
            <h3 class="text-2xl font-bold">900</h3>
            <p>Total Users</p>
          </div>
          <div class="bg-red-600 text-white rounded-lg p-4 shadow">
            <h3 class="text-2xl font-bold">500</h3>
            <p>Total Products</p>
          </div>
        </div>
      </main>
    </div>

  </div>
</template>

<script setup>


</script>
