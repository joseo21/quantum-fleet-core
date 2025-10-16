<template>
  <div>
    <!-- Overlay móvil -->
    <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
      @click="$emit('update:isOpen', false)"></div>

    <aside :class="[
      'fixed md:relative top-0 left-0 h-full bg-[#162d38] text-white border-r border-gray-700 flex flex-col transform transition-transform duration-300 z-50',
      isOpen ? 'translate-x-0' : '-translate-x-full',
      'md:translate-x-0 w-64'
    ]">
      <!-- Header -->
      <header class="p-4 flex justify-end items-center bg-[#162d38]">
        <!-- Hamburger solo en mobile -->
        <button class="md:hidden text-white text-2xl" @click="$emit('update:isOpen', false)">
          ✕
        </button>
      </header>

      <!-- Menú -->
      <nav class="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
        <ul class="space-y-1">
          <li v-for="item in menuItems" :key="item.text">
            <router-link v-if="item.route" :to="item.route"
              class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm hover:bg-[#ff6600]">
              {{ item.text }}
            </router-link>
            <a v-else :href="item.href"
              class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm hover:bg-[#ff6600]">
              {{ item.text }}
            </a>
          </li>

        </ul>
      </nav>
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
        { text: "Dashboard", route: "/" },
        { text: "Dispositivos", route: "/dispositivos" },
        { text: "Alertas", route: "/alertas" },
        { text: "Motor de Reglas", route: "/motor" },
        { text: "Fuentes de Datos", route: "/fuentes" },
        { text: "Usuarios", route: "/usuarios" },
        { text: "Empresas", route: "/empresas" },
        { text: "Reportes/Informes", route: "/reportes" },
        { text: "Mantenciones", route: "/mantenciones" },
        { text: "Configuración", route: "/configuracion" }
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
