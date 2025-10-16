<template>
  <header class="bg-nav bg-[#1f2937] border-b border-gray-700 flex justify-between items-center px-3 py-2">
    <!-- Logo -->
    <div class="flex items-center gap-2">
      <!-- Hamburger visible solo en sm -->
      <button 
        class="md:hidden text-white text-2xl"
        @click="$emit('toggle-sidebar')"
      >
        ☰
      </button>

      <img alt="Logo" src="https://www.gpsenchile.com/wp-content/uploads/2023/06/logowebblanco.png"
        class="w-36 h-15" />
    </div>

    <!-- Perfil -->
    <div class="flex items-center gap-2 text-white">
      <!-- Imagen editable -->
      <div class="relative w-10 h-10">
        <img :src="profileImage" alt="Perfil" class="w-full h-full rounded-full object-cover" />
        <button @click="selectFile"
          class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white rounded-full opacity-0 hover:opacity-100 transition-opacity"
          title="Editar foto">
          ✎
        </button>
        <input type="file" ref="fileInput" accept="image/*" class="hidden" @change="previewImage" />
      </div>

      <!-- Texto + flecha -->
      <div class="relative">
        <button @click="showDropdown = !showDropdown"
          class="flex flex-col items-start px-2 py-1 rounded hover:bg-[#2a3748] transition-colors">
          <div class="flex items-center gap-1">
            <strong class="font-medium">Sebastián Suazo</strong>
            <span class="transition-transform duration-200 text-[10px]"
              :class="{ 'rotate-180': showDropdown }">▼</span>
          </div>
          <span class="text-gray-400 text-xs">Administrador</span>
        </button>

        <!-- Dropdown -->
        <div v-if="showDropdown" class="absolute right-0 mt-1 w-40 bg-[#1f2937] text-white rounded shadow-lg z-50">
          <ul class="list-none p-2">
            <li class="px-2 py-1 hover:bg-[#ff6600] cursor-pointer">My account</li>
            <li class="px-2 py-1 hover:bg-[#ff6600] cursor-pointer">Notifications</li>
            <li>
              <hr class="border-t my-1 border-gray-600" />
            </li>
            <li>
              <a @click.prevent="logout"
                class="w-full group relative inline-flex items-center overflow-hidden gap-x-3.5 py-2 px-2.5 rounded-lg text-sm hover:bg-[#ff6600] cursor-pointer">
                <span class="absolute -start-full transition-all group-hover:start-2">
                  <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </span>
                <span class="transition-all group-hover:ms-4">Cerrar sesión</span>
              </a>
            </li>
          </ul>
        </div>

      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const profileImage = ref(localStorage.getItem("profileImage") || "https://img.freepik.com/vector-premium/perfil-hombre_1083548-15963.jpg")
const fileInput = ref(null)
const showDropdown = ref(false)

const selectFile = () => fileInput.value.click()
const previewImage = (event) => {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    profileImage.value = reader.result
    localStorage.setItem("profileImage", reader.result)
  }
  reader.readAsDataURL(file)
}

const logout = () => {
  console.log("Cerrar sesión")
}
</script>
