<template>
  <div class="h-fit">

    <!-- BOTÓN PRINCIPAL -->
    <button
      class="h-[46px] px-6 rounded-xl bg-[#102372] text-white shadow-sm text-sm font-medium
             flex items-center justify-center gap-2 hover:bg-[#0b1a55]
             transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
      :disabled="!canGenerate"
      @click="open = true"
    >
      Generar reportes
    </button>


    <!-- ===========================
         MODAL PRINCIPAL
    =========================== -->
    <transition name="fade">
      <div v-if="open" class="overlay">

        <div class="modal">

          <!-- HEADER -->
          <div class="modal-header">
            <h2 class="header-title">Generar reportes</h2>
            <p class="header-subtitle">Selecciona el formato que deseas exportar.</p>
          </div>

          <!-- BOTONES CENTRADOS -->
          <div class="options-grid">

            <!-- PDF -->
            <button class="option-btn pdf" @click="confirm('pdf')">
              <span class="icon" v-html="icons.pdf"></span>
              Exportar como PDF
            </button>

            <!-- EXCEL -->
            <button class="option-btn excel" @click="confirm('excel')">
              <span class="icon" v-html="icons.excel"></span>
              Exportar como Excel
            </button>

            <!-- CSV -->
            <button class="option-btn csv" @click="confirm('csv')">
              <span class="icon" v-html="icons.csv"></span>
              Exportar como CSV
            </button>

          </div>

          <button class="cancel-btn" @click="open = false">Cancelar</button>

        </div>
      </div>
    </transition>



    <!-- ===========================
         CONFIRMACIÓN
    =========================== -->
    <transition name="fade">
      <div v-if="confirmOpen" class="overlay">

        <div class="modal">

          <h2 class="header-title">Confirmación</h2>
          <p class="header-subtitle">
            ¿Deseas generar el archivo en formato <strong>{{ formatLabel }}</strong>?
          </p>

          <div class="confirm-actions">
            <button class="option-btn pdf" @click="generate">Sí, continuar</button>
            <button class="cancel-btn" @click="confirmOpen = false">Cancelar</button>
          </div>

        </div>
      </div>
    </transition>



    <!-- ===========================
         LOADING
    =========================== -->
    <transition name="fade">
      <div v-if="loading" class="overlay">

        <div class="modal text-center">
          <h2 class="header-title">Generando reporte...</h2>

          <div class="progress-bar">
            <div class="progress" :style="{ width: progress + '%' }"></div>
          </div>

          <p class="header-subtitle mt-3">Por favor espera unos segundos…</p>
        </div>

      </div>
    </transition>



    <!-- ===========================
         ÉXITO
    =========================== -->
    <transition name="fade">
      <div v-if="success" class="overlay">

        <div class="modal text-center">
          <h2 class="header-title text-green-600">✔ Reporte generado con éxito</h2>

          <button class="option-btn pdf mt-5" @click="closeSuccess">
            Cerrar
          </button>
        </div>

      </div>
    </transition>

  </div>
</template>



<script setup>
import { ref, computed } from "vue"

const props = defineProps({
  devices: Array,
  variables: Array
})

const emit = defineEmits(["export:pdf", "export:excel", "export:csv"])

const open = ref(false)
const confirmOpen = ref(false)
const loading = ref(false)
const success = ref(false)
const selectedFormat = ref(null)
const progress = ref(0)

const canGenerate = computed(() =>
  props.devices?.length && props.variables?.length
)

const formatLabel = computed(() => ({
  pdf: "PDF",
  excel: "Excel",
  csv: "CSV"
}[selectedFormat.value]))


/* ===========================
   SVG CORREGIDOS (colores visibles)
=========================== */
const icons = {
  pdf: `
<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F">
  <path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/>
</svg>
`,
  excel: `
<svg width="20" height="20" viewBox="0 0 24 24" fill="#1F8F3A">
  <rect x="3" y="2" width="14" height="20" rx="2"/>
  <text x="7" y="15" font-size="9" fill="white">X</text>
</svg>
`,
  csv: `
<svg width="20" height="20" viewBox="0 0 24 24" fill="#1F2937">
  <rect x="3" y="2" width="14" height="20" rx="2"/>
  <text x="5" y="15" font-size="8" fill="white">CSV</text>
</svg>
`
}


/* ===========================
   FLUJO DEL MODAL
=========================== */
function confirm(type) {
  selectedFormat.value = type
  confirmOpen.value = true
}

function generate() {
  confirmOpen.value = false
  loading.value = true
  progress.value = 0

  const interval = setInterval(() => {
    progress.value += 10

    if (progress.value >= 100) {
      clearInterval(interval)

      // Emitir descarga
      if (selectedFormat.value === "pdf") emit("export:pdf")
      if (selectedFormat.value === "excel") emit("export:excel")
      if (selectedFormat.value === "csv") emit("export:csv")

      loading.value = false
      success.value = true

      // Ocultar automáticamente
      setTimeout(() => {
        closeSuccess()
      }, 1200)
    }
  }, 120)
}

function closeSuccess() {
  success.value = false
  open.value = false
  selectedFormat.value = null
}
</script>



<style scoped>
/* Overlay */
.overlay {
  position: fixed;
  inset: 0;
  background: #00000066;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  z-index: 999;
}

/* Modal */
.modal {
  background: white;
  width: 380px;
  border-radius: 18px;
  padding: 26px;
  animation: fadeIn .22s ease-out;
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  border: 1px solid #e5e7eb;
}

/* Header */
.header-title {
  color: #102372;
  font-size: 1.1rem;
  font-weight: 700;
}
.header-subtitle {
  margin-top: 4px;
  color: #6b7280;
  font-size: 0.9rem;
}

/* Botones */
.options-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 18px;
}

.option-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  font-size: .9rem;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  transition: .15s;
}

.icon { display: flex; }

.option-btn.pdf { background: #102372; }
.option-btn.pdf:hover { background: #0b1a55; }

.option-btn.excel { background: #FF6600; }
.option-btn.excel:hover { background: #e25500; }

.option-btn.csv { background: #1f2937; }
.option-btn.csv:hover { background: #111827; }

.cancel-btn {
  margin-top: 10px;
  text-align: center;
  color: #6b7280;
  font-size: .9rem;
  transition: .2s;
}
.cancel-btn:hover {
  color: #374151;
}

/* Progress bar */
.progress-bar {
  width: 100%;
  height: 10px;
  background: #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
.progress {
  height: 10px;
  background: #102372;
  transition: width .15s linear;
}

/* Animación */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-enter-active, .fade-leave-active { transition: opacity .15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
