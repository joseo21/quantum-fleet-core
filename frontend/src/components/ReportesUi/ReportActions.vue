<template>
  <div class="h-fit">
    <button
      class="primary-btn"
      :disabled="!canGenerate"
      @click="open = true"
    >
      Generar reportes
    </button>

    <SendReportModal
      v-if="open"
      :default-format="defaultFormat"
      @close="open = false"
      @send="handleSend"
    />
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import SendReportModal from "./SendReportModal.vue"

const props = defineProps({
  devices: Array,
  variables: Array
})

const emit = defineEmits(["send-report"])

const open = ref(false)
const defaultFormat = "csv"

const canGenerate = computed(() =>
  props.devices?.length && props.variables?.length
)

function handleSend(payload) {
  emit("send-report", payload)
  open.value = false
}
</script>

<style scoped>
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
</style>
