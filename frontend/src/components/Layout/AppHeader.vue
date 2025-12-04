<template>
  <header class="bg-[#1f2937] border-b border-gray-700 flex justify-between items-center px-3 py-2">
    <div class="flex items-center gap-2">
      <button class="md:hidden text-white text-2xl px-6" @click="$emit('toggle-sidebar')">☰</button>
      <img alt="Logo" src="https://www.gpsenchile.com/wp-content/uploads/2023/06/logowebblanco.png" class="w-36 h-15" />
    </div>

    <div class="flex items-center gap-2 text-white">
      <div class="relative w-10 h-10">
        <img :src="profileImage" alt="Perfil" class="w-full h-full rounded-full object-cover" />
        <button @click="selectFile"
          class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white rounded-full opacity-0 hover:opacity-100 transition-opacity"
          title="Editar foto">
          ✎
        </button>
        <input type="file" ref="fileInput" accept="image/*" class="hidden" @change="previewImage" />
      </div>

      <div class="relative">
        <button @click="showDropdown = !showDropdown"
          class="flex flex-col items-start px-2 py-1 rounded hover:bg-[#2a3748] transition-colors group">
          <div class="flex items-center gap-1">
            <strong class="font-medium">{{ userName }}</strong>
            <span class="transition-transform duration-200 text-[10px] hidden group-hover:inline" 
                  :class="{ 'rotate-180 inline': showDropdown }">
                ▼
            </span>
          </div>
          <span class="text-gray-400 text-xs">{{ userRole }}</span>
        </button>

        <div v-if="showDropdown" class="absolute right-0 mt-1 w-40 bg-[#1f2937] text-white rounded-lg shadow-lg z-50">
          <ul class="list-none p-2">
            <li>
              <hr class="border-t my-1 border-gray-600" />
            </li>
            <li>
              <a @click.prevent="logout"
                class="w-full group relative inline-flex items-center overflow-hidden gap-x-3.5 py-2 px-2.5 rounded-lg text-sm hover:bg-[#ff6600] cursor-pointer">
                <span class="absolute -start-full transition-all group-hover:start-2">
                  <SvgIcon name="logout" class="w-4 h-4" />
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SvgIcon from '@/components/icons/SvgIcon.vue'

const router = useRouter()
const user = ref({})
const profileImage = ref('')
const fileInput = ref(null)
const showDropdown = ref(false)

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  console.log('AppHeader - usuario cargado de localStorage:', storedUser)
  user.value = storedUser ? JSON.parse(storedUser) : {}
  profileImage.value = user.value.profileImage || 'https://img.freepik.com/vector-premium/perfil-hombre_1083548-15963.jpg'
  console.log('AppHeader - profileImage inicial:', profileImage.value)
})

const userName = computed(() => user.value.name || 'Invitado')
const userRole = computed(() => user.value.role || 'Invitado')

const selectFile = () => fileInput.value.click()

const previewImage = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = () => {
    const dataUrl = reader.result
    console.log('Imagen seleccionada:', dataUrl.length, 'bytes')

    profileImage.value = dataUrl
    const updatedUser = { ...user.value, profileImage: dataUrl }
    user.value = updatedUser

    localStorage.setItem('user', JSON.stringify(updatedUser))
    console.log('Imagen guardada en localStorage:', JSON.parse(localStorage.getItem('user')).profileImage.length, 'bytes')
  }
  reader.readAsDataURL(file)
}

const logout = () => {
  localStorage.removeItem('user')
  user.value = {}
  profileImage.value = 'https://img.freepik.com/vector-premium/perfil-hombre_1083548-15963.jpg'
  console.log('Logout - usuario eliminado')
  router.push('/')
}
</script>