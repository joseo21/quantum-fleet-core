<template>
  <div>
    <!-- Overlay móvil -->
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
      @click="$emit('update:isOpen', false)"
    ></div>

    <aside
      :class="[
        'fixed md:relative top-0 left-0 h-full bg-[#162d38] text-white border-r border-gray-700 flex flex-col transform transition-transform duration-300 z-50',
        isOpen ? 'translate-x-0' : '-translate-x-full',
        'md:translate-x-0 w-64'
      ]"
    >
      <!-- Header -->
      <header class="p-4 flex justify-between items-center bg-gray-800">
        <img
          alt="Logo"
          src="https://www.gpsenchile.com/wp-content/uploads/2023/06/logowebblanco.png"
          class="w-36 h-15"
        />

        <!-- Hamburger solo en mobile -->
        <button class="md:hidden text-white text-2xl" @click="$emit('update:isOpen', false)">
          ✕
        </button>
      </header>

      <!-- Perfil -->
      <div class="flex items-center gap-2 p-4 border-b border-gray-700">
        <div class="relative w-10 h-10 group">
          <img :src="profileImage" alt="Perfil" class="w-full h-full rounded-full object-cover" />
          <button
            @click="selectFile"
            class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            title="Editar foto"
          >
            ✎
          </button>
          <input type="file" ref="fileInput" accept="image/*" class="hidden" @change="previewImage" />
        </div>
        <div>
          <p class="text-xs">
            <strong class="block font-medium">Sebastián Suazo</strong>
            <span class="text-gray-400 text-xs">suazosebastian68@gmail.com</span>
          </p>
        </div>
      </div>

      <!-- Menú -->
      <nav class="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
        <ul class="space-y-1">
          <li v-for="item in menuItems" :key="item.text">
            <a
              :href="item.href"
              class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm hover:bg-[#ff6600]"
            >
              {{ item.text }}
            </a>
          </li>
        </ul>
      </nav>

      <!-- Botón Cerrar Sesión animado -->
      <div class="px-2 py-2 border-t border-gray-700">
        <a
          @click.prevent="logout"
          class="w-full group relative inline-flex items-center overflow-hidden gap-x-3.5 py-2 px-2.5 rounded-lg text-sm hover:bg-[#ff6600] cursor-pointer"
        >
          <!-- Flecha animada -->
          <span class="absolute -start-full transition-all group-hover:start-2">
            <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </span>
          <span class="transition-all group-hover:ms-4">Cerrar sesión</span>
        </a>
      </div>
    </aside>
  </div>
</template>

<script>
export default {
  name: "AppSidebar",
  props: { isOpen: { type: Boolean, default: false } },
  data() {
    return {
      profileImage:
        localStorage.getItem("profileImage") ||
        "https://img.freepik.com/vector-premium/perfil-hombre_1083548-15963.jpg",
      menuItems: [
        { text: "Dashboard", href: "#" },
        { text: "Dispositivos", href: "#" },
        { text: "Alertas", href: "#" },
        { text: "Motor de Reglas", href: "#" },
        { text: "Fuentes de Datos", href: "#" },
        { text: "Analytics", href: "#" },
        { text: "Usuarios/Clientes", href: "#" },
        { text: "Reportes/Informes", href: "#" },
        { text: "Mantenciones", href: "#" },
        { text: "Configuración", href: "#" }
      ]
    };
  },
  methods: {
    selectFile() { this.$refs.fileInput.click(); },
    previewImage(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        this.profileImage = reader.result;
        localStorage.setItem("profileImage", reader.result);
      };
      reader.readAsDataURL(file);
    },
    logout() {
      console.log("Cerrar sesión");
    }
  }
};
</script>
