<!-- SidebarUi/IdentificadorView.vue -->
<template>
    <div class="space-y-3">

        <!-- Label + botón Editar -->
        <div class="flex items-center justify-between">
            <label class="text-gray-500 text-xs">
                {{ isImei ? 'IMEI del dispositivo' : 'Token del dispositivo' }}
            </label>

            <!-- ⭐ SOLO aparece si es TCP y no está en edición -->
            <button v-if="isImei && !isEditing" type="button" @click="$emit('edit')" class="flex items-center gap-1 px-2 py-1 border border-gray-300 
               rounded-md text-[11px] hover:bg-gray-100 
               dark:border-gray-600 dark:hover:bg-gray-800 transition">
                <SvgIcon name="pencil" class="w-4 h-4" />
                Editar
            </button>
        </div>

        <!-- Input + ícono copiar -->
        <div class="relative mt-1">
            <input :value="identifier" :disabled="!canEdit" @input="onInput" class="w-full p-2 pr-10 border rounded-md dark:bg-gray-700
               transition focus:outline-none focus:ring-1 focus:ring-[#102372]" :class="!canEdit
                ? 'bg-gray-100 dark:bg-gray-800 text-gray-500 cursor-default focus:ring-0 pointer-events-none'
                : ''" />

            <!-- Ícono copiar dentro del input (SIEMPRE FUNCIONA) -->
            <button type="button" class="absolute inset-y-0 right-2 flex items-center cursor-pointer group"
                @click="copyIdentifier">
                <SvgIcon name="copy" class="w-6 h-6" />

                <!-- ⭐ TOOLTIP ARRIBA DEL ICONO -->
                <span v-if="copied" class="absolute -top-7 right-0 bg-black text-white 
                 text-[10px] px-2 py-1 rounded shadow-lg opacity-90 
                 animate-tooltip">
                    Copiado!
                </span>
            </button>
        </div>

        <p class="text-[11px] text-gray-500">
            <span v-if="isImei">
                El IMEI solo puede modificarse en modo edición.
            </span>
            <span v-else>
                El token no se puede editar
            </span>
        </p>

    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'

const props = defineProps({
    identifier: String,
    isEditing: Boolean,
    type: String
})

const emit = defineEmits(['update:identifier', 'edit'])

const isImei = computed(() => props.type === 'TCP')
// Solo editable si está en edición y es IMEI
const canEdit = computed(() => props.isEditing && isImei.value)

const onInput = (event) => {
    if (!canEdit.value) {
        event.target.value = props.identifier || ''
        return
    }
    emit('update:identifier', event.target.value)
}

/* COPIAR */
const copied = ref(false)

const copyIdentifier = () => {
    if (!props.identifier) return
    navigator.clipboard.writeText(props.identifier)
    copied.value = true
    setTimeout(() => (copied.value = false), 900)
}
</script>

<style scoped>
@keyframes tooltipFade {
    0% {
        opacity: 0;
        transform: translateY(3px);
    }

    20% {
        opacity: 1;
        transform: translateY(0);
    }

    80% {
        opacity: 1;
        transform: translateY(0);
    }

    100% {
        opacity: 0;
        transform: translateY(-3px);
    }
}

.animate-tooltip {
    animation: tooltipFade 0.9s ease forwards;
}
</style>
