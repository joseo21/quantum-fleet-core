<template>
  <!-- Modal multi-paso -->
  <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4">
    <div
      class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-lg relative flex flex-col w-full max-w-full sm:max-w-3xl h-auto p-4 sm:p-6 border border-gray-300 dark:border-gray-700 shadow-xl overflow-auto max-h-[90vh]">

      <!-- Botón volver paso 2 -> 1 -->
      <button v-if="step === 2" @click="step = 1"
        class="absolute top-4 left-4 p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        title="Volver">
        <SvgIcon name="arrow-left" class="w-6 h-6" />
      </button>

      <h2 class="text-2xl font-bold mb-4 text-center text-[#102372] dark:text-[#ff6600]">
        {{ step === 1 ? "Seleccionar Template" : `Agregar Mantención Vehículo (${selectedPatente})` }}
      </h2>

      <span class="h-px bg-gray-300 dark:bg-gray-700 mb-4"></span>

      <!-- Paso 1: Seleccionar Template -->
      <div v-if="step === 1" class="flex flex-col items-center gap-4 py-4 w-full">
        <div class="flex justify-center gap-4 flex-wrap w-full">
          <div v-for="template in templates" :key="template.id" @click="selectTemplate(template)"
            :class="[
              'relative p-4 sm:p-6 w-full sm:w-48 rounded-lg border cursor-pointer text-center transition-all',
              template.used
                ? 'border-gray-500 bg-gray-200 dark:bg-gray-800 opacity-60 cursor-not-allowed'
                : selectedTemplate?.id === template.id
                  ? 'border-[#ff6600] bg-orange-50 dark:bg-[#ff6600]/20 dark:border-[#ff6600]'
                  : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800'
            ]">
            <h3 class="text-lg font-semibold mb-2">{{ template.name }}</h3>
            <p class="text-gray-600 dark:text-gray-300 text-sm mb-2">{{ template.description }}</p>

            <div v-if="template.used"
              class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white rounded-lg text-sm font-semibold">
              Este vehículo ya tiene este tipo de mantención
            </div>
          </div>
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
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
            v-model="maintenance.intervalo" @keypress="onlyNumber($event)" />
        </div>

        <div>
          <label class="block text-sm mb-1">Email de contacto</label>
          <input type="email" placeholder="Ej: contacto@empresa.cl"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
            v-model="maintenance.email" />
        </div>

        <div>
          <label class="block text-sm mb-1">Alerta</label>
          <input type="number" placeholder="Ej: 5 días antes o 200 km antes"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
            v-model="maintenance.alerta" @keypress="onlyNumber($event)" />
        </div>

        <div>
          <label class="block text-sm mb-1">{{ ultimoCampoLabel }}</label>
          <input v-model="ultimoCampoValue" :type="selectedTemplate?.type === 'Por Odómetro' ? 'number' : 'date'"
            placeholder="Ej: 45000"
            class="w-full p-2 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600"
            @keypress="selectedTemplate?.type === 'Por Odómetro' ? onlyNumber($event) : null" />
        </div>

      </form>

      <!-- Botones del modal -->
      <div class="flex flex-col sm:flex-row justify-between mt-6 gap-2 w-full">
        <button @click="cancel"
          class="w-full sm:w-[48%] bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600 text-gray-900 dark:text-white px-4 py-2 rounded transition">
          Cancelar
        </button>

        <button v-if="step === 1" @click="goToNextStep" :disabled="!selectedTemplate"
          :class="[
            'w-full sm:w-[48%] px-4 py-2 rounded font-semibold transition',
            selectedTemplate
              ? 'bg-[#102372] hover:bg-[#0d1c5a] text-white'
              : 'bg-[#102372] opacity-50 cursor-not-allowed text-white'
          ]">
          Siguiente
        </button>

        <button v-else type="button" @click="saveMaintenance" :disabled="isModalButtonDisabled"
          :class="[
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
</template>

<script>
import SvgIcon from '@/components/icons/SvgIcon.vue'

export default {
  name: 'ModalAgregar',
  components: { SvgIcon },
  props: {
    showAddModal: { type: Boolean, required: true },
    selectedPatente: { type: String, required: true },
    mantenciones: { type: Array, required: true },
    selectedMantencion: { type: [Object, Number], default: null }
  },
  data() {
    return {
      step: 1,
      templates: [
        { id: 1, name: 'Revisión Tecnica', type: 'Por Tiempo', description: 'Verificación completa del vehículo según normativa', used: false },
        { id: 2, name: 'Permiso de Circulación', type: 'Por Tiempo', description: 'Gestión y pago del permiso de circulación anual', used: false },
        { id: 3, name: 'Cambio de Neumáticos', type: 'Por Odómetro', description: 'Rotación, balanceo y revisión del desgaste de neumáticos', used: false },
        { id: 4, name: 'Cambio de Aceite', type: 'Por Odómetro', description: 'Sustitución de aceite y filtro para mantener motor óptimo', used: false },
        { id: 5, name: 'Cambio de Filtro de Aire', type: 'Por Odómetro', description: 'Reemplazo del filtro de aire para mejorar eficiencia del motor', used: false },
      ],
      selectedTemplate: null,
      maintenance: { name: '', type: '', date: '', km: '', details: '', intervalo: '', email: '', alerta: '', fechaUltima: '' },
      isModalButtonDisabled: false
    }
  },
  methods: {
    selectTemplate(template) { if (template.used) return; this.selectedTemplate = template; this.maintenance.name = template.name; this.maintenance.type = template.type },
    goToNextStep() { if (this.selectedTemplate) this.step = 2 },
    cancel() { this.$emit('close'); this.step = 1; this.selectedTemplate = null; this.maintenance = { name: '', type: '', date: '', km: '', details: '', intervalo: '', email: '', alerta: '', fechaUltima: '' } },
    saveMaintenance() {
      if (!this.maintenance) return
      const nuevaMantencion = {
        nombre: this.maintenance.name,
        tipo: this.maintenance.type,
        intervalo: Number(this.maintenance.intervalo || 0),
        ultimo: this.selectedTemplate?.type === 'Por Odómetro' ? Number(this.maintenance.km || 0) : this.maintenance.fechaUltima,
        actual: this.selectedTemplate?.type === 'Por Odómetro' ? Number(this.maintenance.km || 0) : new Date().toISOString().split('T')[0],
        alerta: Number(this.maintenance.alerta || 0),
        email: this.maintenance.email || '',
        fechaCreacion: new Date().toISOString()
      }
      this.$emit('save', nuevaMantencion)
      if (!this.selectedMantencion) this.selectedTemplate.used = true
      this.cancel()
    },
    onlyNumber(e) { const char = String.fromCharCode(e.keyCode); if (!/[0-9]/.test(char)) e.preventDefault() }
  },
  computed: {
    ultimoCampoLabel() { if (!this.selectedTemplate) return ''; return this.selectedTemplate.type === 'Por Odómetro' ? 'Último Kilometraje' : 'Fecha Última Mantención' },
    ultimoCampoValue: {
      get() { return this.selectedTemplate?.type === 'Por Odómetro' ? this.maintenance.km : this.maintenance.fechaUltima },
      set(value) { if (this.selectedTemplate?.type === 'Por Odómetro') this.maintenance.km = value; else this.maintenance.fechaUltima = value }
    }
  },
  watch: {
    selectedMantencion: {
      immediate: true,
      handler(val) {
        if (val !== null) {
          if (typeof val === 'number') {
            const m = this.mantenciones[val]
            if (m) this.maintenance = { ...m }
            this.step = 2
          } else this.step = 1
        } else this.maintenance = { name: '', type: '', date: '', km: '', details: '', intervalo: '', email: '', alerta: '', fechaUltima: '' }; this.step = 1
      }
    }
  }
}
</script>

<style scoped>
button { transition: all 0.2s ease-in-out; }
input::placeholder, textarea::placeholder { color: #9ca3af; }
</style>
