<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-900 p-4">
    <div class="bg-gray-800 shadow-lg rounded-2xl p-8 w-full max-w-md flex flex-col items-center">

      <!-- Logo -->
      <img src="https://www.gpsenchile.com/wp-content/uploads/2023/06/logowebblanco.png" alt="Logo"
        class="w-32 sm:w-40 mb-6" />

      <h2 class="text-3xl font-semibold text-center mb-8 text-gray-100">
        Bienvenido
      </h2>

      <form @submit.prevent="login" class="w-full space-y-6">

        <!-- Usuario -->
        <div>
          <label class="block text-sm text-gray-300 mb-2">Usuario</label>
          <input v-model="username" type="text" placeholder="Usuario"
            class="w-full border border-gray-600 bg-gray-700 rounded-md px-4 py-3 focus:ring-2 focus:ring-teal-500 focus:outline-none text-gray-100"
            required />
        </div>


        <!-- Contraseña -->
        <div class="flex flex-col w-full">
          <div class="flex justify-between items-center mb-2">
            <label class="text-sm text-gray-300">Contraseña</label>
            <a href="#" @click.prevent="showForgot = true" class="text-teal-600 hover:text-teal-500 text-sm">
              ¿Olvidaste tu contraseña?
            </a>
          </div>
          <input v-model="password" type="password" placeholder="••••••••••••"
            class="w-full border border-gray-600 bg-gray-700 rounded-md px-4 py-3 focus:ring-2 focus:ring-teal-500 focus:outline-none text-gray-100"
            required />
        </div>

        <!-- Botón -->
        <button type="submit"
          class="w-full bg-teal-600 hover:bg-teal-500 text-white font-medium py-3 rounded-md transition-all text-lg">
          Ingresar
        </button>

        <!-- Error -->
        <p v-if="error" class="text-red-500 text-center text-sm mt-2">{{ error }}</p>

        <!-- Links -->
        <div class="flex justify-center items-center gap-2 text-sm mt-2">
          <span class="text-white">Contáctanos:</span>
          <a href="#" @click.prevent="showContact = true" class="text-teal-600 hover:text-teal-500">
            informatica@sinergygroup.cl
          </a>
        </div>
      </form>

      <!-- Modal Olvidé contraseña  -->
      <div v-if="showForgot" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4"
        @click.self="showForgot = false">
        <div class="w-full max-w-md rounded-lg bg-gray-800 dark:bg-gray-900 p-6 relative space-y-6">

          <!-- Botón cerrar -->
          <button @click="showForgot = false"
            class="absolute top-2 right-2 text-gray-300 hover:text-red-500 font-bold text-2xl">
            &times;
          </button>

          <!-- Icono superior -->
          <div class="flex justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-yellow-500" fill="none" viewBox="0 0 24 24"
              stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M12 11c.828 0 1.5.672 1.5 1.5V15a1.5 1.5 0 01-3 0v-2.5c0-.828.672-1.5 1.5-1.5z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 11V8a6 6 0 1112 0v3" />
              <rect x="6" y="11" width="12" height="10" rx="2" ry="2" />
            </svg>
          </div>

          <h2 class="text-center text-2xl font-semibold text-gray-100">Forgot Password?</h2>

          <!-- Formulario / Mensaje de éxito -->
          <div class="space-y-4">
            <template v-if="successForgot">
              <div class="flex flex-col items-center justify-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <p class="text-green-500 font-semibold text-center">Se ha enviado correctamente al sistema de Tickets,
                  favor de esperar su respuesta.</p>
              </div>
            </template>

            <template v-else>
              <form @submit.prevent="handleForgot" class="space-y-4">
                <!-- Email Input -->
                <div class="relative">
                  <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                      stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round"
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </span>
                  <input id="email" type="email" v-model="emailForgot" placeholder="Enter your email"
                    class="w-full rounded-lg border border-gray-600 bg-gray-700 text-gray-100 px-4 py-2.5 pl-10 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required />
                </div>

                <!-- Botones centrados -->
                <div class="flex justify-center gap-4">
                  <button type="submit"
                    class="flex h-10 items-center justify-center rounded-lg bg-teal-600 text-white hover:bg-teal-500 px-6 py-2 transition">
                    Send Reset
                  </button>
                  <button @click="showForgot = false" type="button"
                    class="px-6 py-2 rounded border text-gray-100 hover:border-teal-500 hover:text-teal-500 transition">
                    Cancel
                  </button>
                </div>
              </form>
            </template>
          </div>
        </div>
      </div>



      <!-- Modal Contáctanos -->
      <div v-if="showContact" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
        @click.self="showContact = false">
        <div class="bg-gray-800 dark:bg-gray-900 p-6 rounded-lg shadow-lg w-full max-w-md relative space-y-6">

          <!-- Botón cerrar -->
          <button @click="showContact = false"
            class="absolute top-2 right-2 text-gray-300 hover:text-red-500 font-bold text-2xl">
            &times;
          </button>

          <h2 class="text-2xl font-semibold mb-4 text-center text-gray-100">Contáctanos</h2>

          <!-- Formulario / Mensaje de éxito -->
          <div class="space-y-4">
            <template v-if="successContact">
              <div class="flex flex-col items-center justify-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <p class="text-green-500 font-semibold text-center">Mensaje enviado correctamente al nuestro sistema de Tickets, favor de esperar su respuesta.</p>
              </div>
            </template>

            <template v-else>
              <form @submit.prevent="handleContact" class="space-y-4">
                <input v-model="nombre" type="text" placeholder="Nombre"
                  class="w-full border border-gray-600 bg-gray-700 text-gray-100 rounded px-2 py-1 focus:outline-none focus:border-teal-500"
                  required />
                <input v-model="email" type="email" placeholder="Email"
                  class="w-full border border-gray-600 bg-gray-700 text-gray-100 rounded px-2 py-1 focus:outline-none focus:border-teal-500"
                  required />
                <textarea v-model="mensaje" placeholder="Mensaje" rows="4"
                  class="w-full border border-gray-600 bg-gray-700 text-gray-100 rounded px-2 py-1 focus:outline-none focus:border-teal-500"
                  required></textarea>

                <button type="submit"
                  class="w-full bg-teal-600 hover:bg-teal-500 text-white font-bold py-2 rounded transition">
                  Enviar
                </button>
              </form>
            </template>
          </div>
        </div>
      </div>



    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import users from '@/data/users.json'

const showForgot = ref(false)
const showContact = ref(false)

const successForgot = ref(false)
const successContact = ref(false)

// Campos Olvidé contraseña
const emailForgot = ref('')

// Campos Contáctanos
const nombre = ref('')
const email = ref('')
const mensaje = ref('')



const handleForgot = () => {
  console.log('Recuperar contraseña:', emailForgot.value)
  // Aquí podrías llamar a tu API si hubiera
  successForgot.value = true
  emailForgot.value = ''
}

const handleContact = () => {
  console.log('Mensaje enviado:', { nombre: nombre.value, email: email.value, mensaje: mensaje.value })
  successContact.value = true
  nombre.value = ''
  email.value = ''
  mensaje.value = ''
}



const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const login = () => {
  console.log('Intentando login:', username.value)

  const userFound = users.find(u => u.username === username.value && u.password === password.value)
  console.log('Usuario encontrado en JSON:', userFound)

  if (!userFound) {
    error.value = 'Usuario o contraseña incorrectos'
    return
  }

  const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
  const profileImage = storedUser.username === userFound.username && storedUser.profileImage
    ? storedUser.profileImage
    : userFound.profileImage

  const finalUser = { ...userFound, profileImage }
  localStorage.setItem('user', JSON.stringify(finalUser))

  router.push('/AdminDashboard')
}
</script>
