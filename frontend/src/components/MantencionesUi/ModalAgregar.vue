<template>
  <!-- Modal multi-paso -->
  <div v-if="showAddModal"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-2 sm:p-4">
    <div
      class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-lg relative flex flex-col w-full max-w-full sm:max-w-3xl h-auto p-4 sm:p-6 border border-gray-300 dark:border-gray-700 shadow-xl overflow-auto max-h-[90vh]">
      <button @click="$emit('close')"
        class="absolute top-4 right-4 p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition" title="Cerrar">
        <SvgIcon name="close" class="w-6 h-6" />
      </button>
      <!-- Botón volver paso 2 -> 1 -->
      <button v-if="step === 2" @click="step = 1"
        class="absolute top-4 left-4 p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition" title="Volver">
        <SvgIcon name="arrow-left" class="w-6 h-6" />
      </button>

      <h2 class="text-2xl font-bold mb-4 text-center text-[#102372] dark:text-[#ff6600]">
        {{ step === 1 ? "Seleccionar Template" : `Agregar Mantención Vehículo (${selectedPatente})` }}
      </h2>

      <span class="h-px bg-gray-300 dark:bg-gray-700 mb-4"></span>

      <!-- Paso 1: Seleccionar Template -->
      <div v-if="step === 1" class="flex flex-col items-center gap-4 py-4 w-full">



        <!-- Templates visibles -->
        <div class="flex justify-center gap-4 flex-wrap w-full">
          <div v-for="template in paginatedTemplates" :key="template.id" @click="selectTemplate(template)" :class="[
            'relative group p-4 sm:p-6 w-full sm:w-48 md:w-56 rounded-lg border cursor-pointer text-center transition-all',
            template.used
              ? 'border-gray-500 bg-gray-200 dark:bg-gray-800 opacity-60 cursor-not-allowed'
              : selectedTemplate?.id === template.id
                ? 'border-[#ff6600] bg-orange-50 dark:bg-[#ff6600]/20 dark:border-[#ff6600]'
                : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800'
          ]">
            <h3 class="text-lg font-semibold mb-2">{{ template.name }}</h3>
            <p class="text-gray-600 dark:text-gray-300 text-sm mb-2">{{ template.description }}</p>

            <!-- Botón eliminar (solo SVG, estético y minimalista) -->
            <button @click.stop="eliminarTemplate(template.id)"
              class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-gray-700 dark:text-gray-300 hover:text-black dark:hover:text-white transition-all duration-200"
              title="Eliminar tipo de mantención">
              <SvgIcon name="trash" class="w-5 h-5" />
            </button>


            <!-- Overlay si ya está usada -->
            <div v-if="template.used"
              class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white rounded-lg text-sm font-semibold">
              Este vehículo ya tiene este tipo de mantención
            </div>
          </div>

          <!-- Card para agregar nuevo tipo -->
          <div @click="abrirModalAgregarTipo"
            class="relative group p-4 sm:p-6 w-full sm:w-48 md:w-56 rounded-lg border border-gray-300 dark:border-gray-600 bg-green-50 dark:bg-green-800 cursor-pointer text-center hover:bg-green-100 dark:hover:bg-green-700 transition-all">
            <h3 class="text-lg font-semibold mb-2">+ Agregar Mantención</h3>
            <p class="text-gray-600 dark:text-gray-300 text-sm">Crea un nuevo tipo de mantención</p>
          </div>
        </div>

        <!-- Botones de paginación -->
        <div v-if="totalPages > 1" class="flex justify-center items-center gap-3 mt-4">
          <button @click="prevPage" :disabled="currentPage === 1"
            class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition disabled:opacity-50">
            <SvgIcon name="chevron-left" class="w-6 h-6" />
          </button>

          <span class="text-sm text-gray-700 dark:text-gray-300">
            Página {{ currentPage }} de {{ totalPages }}
          </span>

          <button @click="nextPage" :disabled="currentPage === totalPages"
            class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition disabled:opacity-50">
            <SvgIcon name="chevron-right" class="w-6 h-6" />
          </button>
        </div>

      </div>


      <!-- Paso 2: Formulario -->
      <form v-else @submit.prevent="saveMaintenance"
        class="grid grid-cols-1 sm:grid-cols-2 gap-4 py-2 overflow-y-auto w-full">

        <div>
          <label class="block text-sm mb-1">Nombre de la Mantención</label>
          <input type="text"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
            v-model="maintenance.name" disabled />
        </div>

        <div>
          <label class="block text-sm mb-1">Tipo de Mantención</label>
          <input type="text"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
            v-model="maintenance.type" disabled />
        </div>

        <div>
          <label class="block text-sm mb-1">Intervalo</label>
          <input type="number" placeholder="Ej: 30 días o 5000 km"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 required"
            v-model="maintenance.intervalo" @keypress="onlyNumber($event)" min="1" />
        </div>

        <div>
          <label class="block text-sm mb-1">Email de contacto</label>
          <input type="email" placeholder="Ej: contacto@empresa.cl"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
            v-model="maintenance.email" required />

        </div>

        <div>
          <label class="block text-sm mb-1">Alerta</label>
          <input type="number" placeholder="Ej: 5 días antes o 200 km antes"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 required"
            v-model="maintenance.alerta" @keypress="onlyNumber($event)" min="1" />
        </div>

        <div>
          <label class="block text-sm mb-1">{{ ultimoCampoLabel }}</label>
          <input v-model="ultimoCampoValue"
            :type="selectedTemplate?.type === 'Por Odómetro' || selectedTemplate?.type === 'Por Horómetro' ? 'number' : 'date'"
            placeholder="Ej: 45000"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 required"
            @keypress="(selectedTemplate?.type === 'Por Odómetro' || selectedTemplate?.type === 'Por Horómetro') ? onlyNumber($event) : null"
            :min="selectedTemplate?.type === 'Por Odómetro' ? 1 : null" />
        </div>

      </form>

      <!-- Botones del modal -->
      <div class="flex flex-col sm:flex-row justify-between mt-6 gap-2 w-full">
        <button @click="cancel"
          class="w-full sm:w-[48%] bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600 text-gray-900 dark:text-white px-4 py-2 rounded transition">
          Cancelar
        </button>

        <button v-if="step === 1" @click="goToNextStep" :disabled="!selectedTemplate" :class="[
          'w-full sm:w-[48%] px-4 py-2 rounded font-semibold transition',
          selectedTemplate
            ? 'bg-[#102372] hover:bg-[#0d1c5a] text-white'
            : 'bg-[#102372] opacity-50 cursor-not-allowed text-white'
        ]">
          Siguiente
        </button>

        <button v-else type="button" @click="saveMaintenance" :disabled="isModalButtonDisabled" :class="[
          'w-full sm:w-[48%] px-4 py-2 rounded font-semibold transition',
          isModalButtonDisabled
            ? 'bg-[#102372] opacity-50 cursor-not-allowed text-white'
            : 'bg-[#102372] hover:bg-[#0d1c5a] text-white'
        ]">
          Guardar
        </button>
      </div>

    </div>
  </div>
  <ModalMantencionType v-if="showModalAgregarTipo" @close="showModalAgregarTipo = false" @save="agregarNuevoTipo" />

</template>
<script>
import SvgIcon from '@/components/icons/SvgIcon.vue'
import ModalMantencionType from '@/components/MantencionesUi/ModalMantencionType.vue'
import { nextTick } from 'vue'

export default {
  name: 'ModalAgregar',
  components: { SvgIcon, ModalMantencionType },
  props: {
    showAddModal: { type: Boolean, required: true },
    selectedPatente: { type: String, required: true },
    mantenciones: { type: Array, required: true },
    selectedMantencion: { type: [Object, Number], default: null },
    kmActual: { type: Number, default: 0 },

  },
  data() {
    return {
      step: 1,
      templatesPerPage: 5,      // Número de templates por página
      currentPage: 1,            // Página actual
      templates: [
        { id: 1, name: 'Revisión Tecnica', type: 'Por Tiempo', description: 'Verificación completa del vehículo según normativa', used: false },
        { id: 2, name: 'Permiso de Circulación', type: 'Por Tiempo', description: 'Gestión y pago del permiso de circulación anual', used: false },
        { id: 3, name: 'Cambio de Neumáticos', type: 'Por Odómetro', description: 'Rotación, balanceo y revisión del desgaste de neumáticos', used: false },
        { id: 4, name: 'Cambio de Aceite', type: 'Por Odómetro', description: 'Sustitución de aceite y filtro para mantener motor óptimo', used: false },
        { id: 5, name: 'Cambio de Filtro de Aire', type: 'Por Odómetro', description: 'Reemplazo del filtro de aire para mejorar eficiencia del motor', used: false },
      ],
      selectedTemplate: null,
      maintenance: { name: '', type: '', date: '', km: '', details: '', intervalo: '', email: '', alerta: '', fechaUltima: '' },

      originalMantencion: null,
      showModalAgregarTipo: false
    }
  },
  methods: {
    // Seleccionar plantilla de mantención
    selectTemplate(template) {
      if (template.used && this.selectedMantencion === null) return
      this.selectedTemplate = template

      if (this.selectedMantencion === null) {
        // Caso: nueva mantención
        this.maintenance.name = template.name
        this.maintenance.type = template.type
        this.maintenance.km = ''
        this.maintenance.fechaUltima = ''
      } else {
        // Caso: edición de una mantención existente
        if (this.originalMantencion) {
          if (template.type === 'Por Odómetro') {
            const val = Number(this.originalMantencion.ultimo)
            this.maintenance.km = isNaN(val) ? '' : val
            this.maintenance.fechaUltima = ''
          } else {
            const val = this.originalMantencion.ultimo
            this.maintenance.fechaUltima = typeof val === 'string' ? val : ''
            this.maintenance.km = ''
          }
        } else {
          this.maintenance.name = template.name
          this.maintenance.type = template.type
        }
        this.maintenance.name = template.name
        this.maintenance.type = template.type
      }
    },
    eliminarTemplate(id) {
      const index = this.templates.findIndex(t => t.id === id)
      if (index !== -1) {
        if (confirm('¿Seguro quieres eliminar este tipo de mantención?')) {
          this.templates.splice(index, 1)
        }
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) this.currentPage++
    },
    prevPage() {
      if (this.currentPage > 1) this.currentPage--
    },

    abrirModalAgregarTipo() {
      this.showModalAgregarTipo = true
    },

    agregarNuevoTipo(nuevoTemplate) {
      this.templates.push({
        id: this.templates.length + 1,
        name: nuevoTemplate.name,
        type: nuevoTemplate.type,
        description: nuevoTemplate.description,
        used: false
      })
      this.showModalAgregarTipo = false
      this.selectedTemplate = null

      // Ajustar paginación si se necesita
      this.currentPage = this.totalPages
    },

    // Avanzar al siguiente paso del modal
    goToNextStep() {
      if (this.selectedTemplate) this.step = 2
    },

    // Cerrar modal y limpiar datos
    cancel() {
      this.$emit('close')
      this.step = 1
      this.selectedTemplate = null
      this.originalMantencion = null
      this.maintenance = { name: '', type: '', date: '', km: '', details: '', intervalo: '', email: '', alerta: '', fechaUltima: '' }
    },

    // Guardar mantención nueva o editada
    saveMaintenance() {
      if (!this.maintenance) return

      // === 🔎 Validaciones previas ===
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      const errores = []

      if (!this.maintenance.name?.trim()) errores.push("El nombre de la mantención es obligatorio.")
      if (!this.maintenance.type?.trim() && !this.selectedTemplate?.type) errores.push("Debes seleccionar un tipo de mantención.")
      if (!this.maintenance.intervalo || isNaN(this.maintenance.intervalo)) errores.push("El intervalo debe ser un número válido.")
      if (!this.maintenance.alerta || isNaN(this.maintenance.alerta)) errores.push("El valor de alerta debe ser un número válido.")
      if (!emailRegex.test(this.maintenance.email || '')) errores.push("El correo electrónico no es válido.")

      // Si hay errores, mostramos una alerta y detenemos la ejecución
      if (errores.length > 0) {
        alert(errores.join('\n'))
        return
      }

      // === 🧩 Construcción del objeto mantención ===
      const tipo = this.maintenance.type || this.selectedTemplate?.type || ''

      const nuevaMantencion = {
        nombre: this.maintenance.name || this.selectedTemplate?.name || '',
        tipo,
        intervalo: Number(this.maintenance.intervalo || 0),
        alerta: Number(this.maintenance.alerta || 0),
        email: this.maintenance.email || '',
        fechaCreacion: new Date().toISOString(),
      }

      if (tipo === 'Por Odómetro' || tipo === 'Por Horómetro') {
        nuevaMantencion.ultimo = Number(this.maintenance.km || 0)
        nuevaMantencion.actual = Number(this.kmActual || 0)

        const diferencia = nuevaMantencion.actual - nuevaMantencion.ultimo
        if (diferencia < nuevaMantencion.intervalo - nuevaMantencion.alerta) {
          nuevaMantencion.estado = 'OK'
        } else if (diferencia >= nuevaMantencion.intervalo - nuevaMantencion.alerta && diferencia < nuevaMantencion.intervalo) {
          nuevaMantencion.estado = 'Próxima mantención'
        } else {
          nuevaMantencion.estado = 'Requiere mantención'
        }
      } else if (tipo === 'Por Tiempo') {
        nuevaMantencion.ultimo = this.maintenance.fechaUltima || new Date().toISOString().split('T')[0]
        nuevaMantencion.actual = new Date().toISOString().split('T')[0]

        const ultima = new Date(nuevaMantencion.ultimo)
        const hoy = new Date()
        const diffDias = Math.floor((hoy - ultima) / (1000 * 60 * 60 * 24))

        if (diffDias < nuevaMantencion.intervalo - nuevaMantencion.alerta) {
          nuevaMantencion.estado = 'OK'
        } else if (diffDias >= nuevaMantencion.intervalo - nuevaMantencion.alerta && diffDias < nuevaMantencion.intervalo) {
          nuevaMantencion.estado = 'Próxima mantención'
        } else {
          nuevaMantencion.estado = 'Requiere mantención'
        }
      }

      // === 🚀 Emitir y cerrar modal ===
      this.$emit('save', nuevaMantencion)

      if (this.selectedTemplate) {
        const index = this.templates.findIndex(t => t.id === this.selectedTemplate.id)
        if (index !== -1) this.templates[index].used = true
      }

      this.cancel()
    },


    // Permitir solo números en inputs específicos
    onlyNumber(e) {
      const char = String.fromCharCode(e.keyCode)
      if (!/[0-9]/.test(char)) e.preventDefault()
    }
  },

  computed: {
    templatesConEstado() {
      const mantencionesVehiculo = this.mantenciones || []
      const nombresUsados = mantencionesVehiculo
        .filter((m, idx) => idx !== this.selectedMantencion)
        .map(m => ((m.nombre || m.name) || '').toString().toLowerCase().trim())

      return this.templates.map(t => ({ ...t, used: nombresUsados.includes(t.name.toLowerCase()) }))
    },

    totalPages() {
      return Math.ceil(this.templatesConEstado.length / this.templatesPerPage)
    },

    paginatedTemplates() {
      const start = (this.currentPage - 1) * this.templatesPerPage
      return this.templatesConEstado.slice(start, start + this.templatesPerPage)
    },

    ultimoCampoLabel() {
      if (!this.selectedTemplate) return ''
      return (this.selectedTemplate.type === 'Por Odómetro' || this.selectedTemplate.type === 'Por Horómetro')
        ? 'Último Kilometraje/Horómetro'
        : 'Fecha Última Mantención'
    },

    ultimoCampoValue: {
      get() {
        return (this.selectedTemplate?.type === 'Por Odómetro' || this.selectedTemplate?.type === 'Por Horómetro')
          ? this.maintenance.km
          : this.maintenance.fechaUltima
      },
      set(value) {
        if (this.selectedTemplate?.type === 'Por Odómetro' || this.selectedTemplate?.type === 'Por Horómetro')
          this.maintenance.km = value
        else
          this.maintenance.fechaUltima = value
      }
    },
    isModalButtonDisabled() {
      if (!this.maintenance.email) return true
      if (!this.maintenance.intervalo || Number(this.maintenance.intervalo) <= 0) return true
      if (!this.maintenance.alerta || Number(this.maintenance.alerta) <= 0) return true

      if (this.selectedTemplate?.type === 'Por Odómetro' || this.selectedTemplate?.type === 'Por Horómetro') {
        if (!this.maintenance.km || Number(this.maintenance.km) <= 0) return true
      } else {
        if (!this.maintenance.fechaUltima) return true
      }

      return false
    }

  },

  watch: {
    // Cargar correctamente los datos al editar una mantención
    selectedMantencion: {
      immediate: true,
      async handler(val) {
        if (val !== null && typeof val === 'number') {
          const m = this.mantenciones[val]
          if (m) {
            this.originalMantencion = { ...m }

            // Buscar plantilla correspondiente
            this.selectedTemplate = this.templates.find(
              t => t.name.toLowerCase().trim() === (m.nombre || m.name || '').toString().toLowerCase().trim()
            ) || null

            await nextTick()

            // Mapear datos del objeto al formulario
            this.maintenance = {
              name: m.nombre || m.name || this.selectedTemplate?.name || '',
              type: m.tipo || m.type || this.selectedTemplate?.type || '',
              intervalo: m.intervalo || '',
              alerta: m.alerta || '',
              email: m.email || '',
              details: m.details || '',
              km: (this.selectedTemplate?.type === 'Por Odómetro') ? (Number(m.ultimo) || '') : '',
              fechaUltima: (this.selectedTemplate?.type === 'Por Tiempo') ? (typeof m.ultimo === 'string' ? m.ultimo : '') : ''
            }

            this.step = 2
          }
        } else {
          // Reset si no hay selección
          this.originalMantencion = null
          this.maintenance = { name: '', type: '', date: '', km: '', details: '', intervalo: '', email: '', alerta: '', fechaUltima: '' }
          this.step = 1
          this.selectedTemplate = null
        }
      }
    },

    // Actualizar valores al cambiar plantilla mientras se edita
    selectedTemplate(newVal) {
      if (!newVal) return
      if (this.originalMantencion && this.selectedMantencion !== null) {
        if (newVal.type === 'Por Odómetro') {
          const num = Number(this.originalMantencion.ultimo)
          this.maintenance.km = isNaN(num) ? '' : num
          this.maintenance.fechaUltima = ''
        } else {
          const fecha = this.originalMantencion.ultimo
          this.maintenance.fechaUltima = typeof fecha === 'string' ? fecha : ''
          this.maintenance.km = ''
        }
        this.maintenance.name = newVal.name
        this.maintenance.type = newVal.type
      }
    },

    // Reiniciar el modal al abrirlo
    showAddModal(val) {
      if (val) {
        this.step = 1
        this.selectedTemplate = null
        this.originalMantencion = null
        nextTick(() => {
          const nombresUsados = (this.mantenciones || []).map(m =>
            ((m.nombre || m.name) || '').toString().trim().toLowerCase()
          )
          this.templates.forEach(t =>
            t.used = nombresUsados.includes((t.name || '').toString().trim().toLowerCase())
          )
        })
      }
    }
  }
}
</script>



<style scoped>
button {
  transition: all 0.2s ease-in-out;
}

input::placeholder,
textarea::placeholder {
  color: #9ca3af;
}
</style>
