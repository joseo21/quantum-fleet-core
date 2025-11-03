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
        <h2>Completar lo de Safco</h2>
        <h2>Dispositivos :
          Nombre<br>
          empresa<br>
          petente 
          Id token
          GPS 
          DATALOGUER
          CREDENCIALES POR MQTT Y HTTP

          tabla que diga si es que tomo datos de un min o mas que tire si es que ya no tira se pase a offline 

          generar un token id unica con el dispositivo para asociar si es lataloguer y si es gps tu le das el imei 

        </h2>
        <h2>Modificar visual combustible</h2>
      </main>
    </div>

  </div>
</template>

<script setup>


</script>
