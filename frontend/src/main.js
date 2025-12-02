import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/tailwind.css'

const app = createApp(App)

// ========================================
// ✅ DIRECTIVA GLOBAL v-click-outside (Versión 100% compatible Vue CLI 3.2)
// ========================================
app.directive("click-outside", {
  beforeMount(el, binding) {
    el.__clickOutsideHandler__ = (event) => {
      // Si el click NO es desde el elemento ni desde un hijo →
      // ejecutar la función del v-click-outside
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }

    // 👇 ESTE true ES LA CLAVE PARA QUE FUNCIONE EN Vue CLI
    document.addEventListener("click", el.__clickOutsideHandler__, true)
  },

  unmounted(el) {
    document.removeEventListener("click", el.__clickOutsideHandler__, true)
  }
})

// ========================================
// 🚀 INICIALIZAR APP
// ========================================
app.use(router)
app.mount('#app')
