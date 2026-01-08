<template>
  <transition name="fade">
    <div class="overlay">
      <div class="modal">

        <h2 class="modal-title">Enviar reporte</h2>
        <p class="modal-subtitle">
          Formato seleccionado: <strong>{{ formatLabel }}</strong>
        </p>

        <!-- FORMATO -->
        <div class="format-switch">
          <button
            v-for="f in formats"
            :key="f"
            class="format-pill"
            :class="{ active: format === f }"
            @click="format = f"
          >
            {{ f.toUpperCase() }}
          </button>
        </div>

        <!-- CANAL -->
        <div class="channel-switch">
          <button
            class="channel-pill"
            :class="{ active: channel === 'email' }"
            @click="channel = 'email'"
          >
            Correo electrónico
          </button>
          <button
            class="channel-pill"
            :class="{ active: channel === 'whatsapp' }"
            @click="channel = 'whatsapp'"
          >
            WhatsApp
          </button>
        </div>

        <!-- DESTINO -->
        <input
          v-if="channel"
          v-model="destination"
          :placeholder="channel === 'email'
            ? 'correo@empresa.cl'
            : '+569XXXXXXXX'"
          class="destination-input"
        />

        <!-- ACCIONES -->
        <div class="actions">
          <button class="cancel-link" @click="$emit('close')">
            Cancelar
          </button>

          <button
            class="primary-btn"
            :disabled="!destination"
            @click="send"
          >
            Enviar reporte
          </button>
        </div>

      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed } from "vue"

const props = defineProps({
  defaultFormat: {
    type: String,
    default: "csv"
  }
})

const emit = defineEmits(["send", "close"])

const formats = ["pdf", "excel", "csv"]
const format = ref(props.defaultFormat)
const channel = ref(null)
const destination = ref("")

const formatLabel = computed(() => format.value.toUpperCase())

function send() {
  emit("send", {
    format: format.value,
    channel: channel.value,
    destination: destination.value
  })
}
</script>

<style scoped>
/* overlay y modal */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.4);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(3px);
  z-index: 999;
}

.modal {
  background: white;
  border-radius: 18px;
  padding: 28px;
  width: 420px;
  box-shadow: 0 20px 45px rgba(0,0,0,.25);
}

/* textos */
.modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #102372;
}
.modal-subtitle {
  margin-top: 6px;
  font-size: .9rem;
  color: #6b7280;
}

/* switches */
.format-switch,
.channel-switch {
  display: flex;
  gap: 10px;
  margin-top: 18px;
}

.format-pill,
.channel-pill {
  flex: 1;
  height: 40px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  background: white;
  font-size: .85rem;
  cursor: pointer;
}
.format-pill.active,
.channel-pill.active {
  background: #102372;
  color: white;
  border-color: #102372;
}

/* input */
.destination-input {
  margin-top: 14px;
  width: 100%;
  height: 42px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  padding: 0 12px;
  font-size: .85rem;
}

/* acciones */
.actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.primary-btn {
  height: 42px;
  padding: 0 20px;
  border-radius: 10px;
  background: #102372;
  color: white;
  font-size: .85rem;
  font-weight: 600;
}
.primary-btn:disabled {
  opacity: .5;
}

.cancel-link {
  background: none;
  font-size: .85rem;
  color: #6b7280;
}
.cancel-link:hover {
  text-decoration: underline;
}

/* animación */
.fade-enter-active,
.fade-leave-active {
  transition: opacity .15s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
