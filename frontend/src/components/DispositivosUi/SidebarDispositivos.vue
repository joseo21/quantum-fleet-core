<!-- SidebarDevice.vue -->
<template>
    <!-- OVERLAY -->
    <div v-if="open" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40" @click="handleOverlayClick"></div>

    <!-- SIDEBAR -->
    <transition name="slide-sidebar">
        <div v-if="open" class="fixed top-0 right-0 h-full bg-white dark:bg-gray-900 shadow-xl z-50
             border-l border-gray-200 dark:border-gray-700 flex flex-col" style="width: 50vw;">

            <!-- ⭐ HEADER CON TABS -->
            <div class="border-b border-gray-200 dark:border-gray-700 px-4 pt-4">

                <div class="flex justify-between items-center mb-3">
                    <h2 class="text-lg font-semibold text-gray-800 dark:text-white">
                        Detalles del Dispositivo
                    </h2>

                    <button @click="closeSidebar" class="p-2 hover:bg-gray-200 dark:hover:bg-gray-800 rounded">
                        <SvgIcon name="close" class="w-5 h-5" />
                    </button>
                </div>

                <!-- ⭐ MENÚ DE TABS -->
                <div class="flex gap-4 text-sm font-medium border-b border-gray-300 dark:border-gray-700">
                    <button v-for="t in tabs" :key="t.value" @click="onTabClick(t.value)" :class="[
                        'pb-2 px-1 transition',
                        activeTab === t.value
                            ? 'border-b-2 border-[#102372] text-[#102372] dark:text-[#ff6600]'
                            : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300',
                        isEditing ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                    ]">
                        {{ t.label }}
                    </button>
                </div>

            </div>

            <!-- ⭐ CONTENT -->
            <div class="flex-1 overflow-y-auto p-4">

                <DetalleView v-if="activeTab === 'detalle'" :name="localDevice.name" :iccid="localDevice.iccid"
                    :created-at="localDevice.createdAt" :is-editing="isEditing && editingSection === 'detalle'"
                    @edit="startEditing('detalle')" @update:name="localDevice.name = $event"
                    @update:iccid="localDevice.iccid = $event" />

                <IdentificadorView v-else-if="activeTab === 'identificador'" :identifier="localDevice.identifier"
                    :type="localDevice.type" :is-editing="isEditing && editingSection === 'identificador'"
                    @edit="startEditing('identificador')" @update:identifier="localDevice.identifier = $event" />

                <UrlView v-else-if="activeTab === 'url'" :device-id="localDevice.id" :token="localDevice.token"
                    :tipo="localDevice.type" />

                <TelemetriaView v-else-if="activeTab === 'telemetria'" :last-report="localDevice.lastReport"
                    :last-level="localDevice.lastLevel" :last-liters="localDevice.lastLiters" />

                <!-- ⭐ CONTROL DE VERSIONES -->
                <ControlDeVersiones 
                    v-if="activeTab === 'versiones'" 
                    :versions="localDevice.versions"
                    @confirm-rollback="openRollbackModal"
                    @show-details="openDetailsModal"
                />

            </div>

            <!-- ⭐ FOOTER -->
            <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between gap-4">

                <template v-if="!isEditing">
                    <button class="w-full py-3 border rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
                        @click="closeSidebar">
                        Cerrar
                    </button>
                </template>

                <template v-else>
                    <button class="w-[48%] py-3 border rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
                        @click="cancelEditing">
                        Cancelar
                    </button>

                    <button class="w-[48%] py-3 rounded-md text-white bg-[#102372] hover:bg-[#ff6600]"
                        @click="saveChanges">
                        Guardar Cambios
                    </button>
                </template>

            </div>

        </div>
    </transition>

    <!-- ============================ -->
    <!-- ⭐ MODALES (fuera del sidebar) -->
    <!-- ============================ -->
    <RollbackConfirmModal
        v-if="showRollbackModal"
        :show="showRollbackModal"
        :version="versionToRollback"
        :device="localDevice"
        @cancel="showRollbackModal = false"
        @confirm="doRollback"
    />

    <ModalDetalles
        v-if="showDetailsModal"
        :show="showDetailsModal"
        :version="detailsVersion"
        @close="showDetailsModal = false"
    />
</template>

<script setup>
import { ref, watch } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'

import DetalleView from '@/components/DispositivosUi/SidebarUi/DetalleView.vue'
import IdentificadorView from '@/components/DispositivosUi/SidebarUi/IdentificadorView.vue'
import UrlView from '@/components/DispositivosUi/SidebarUi/UrlView.vue'
import TelemetriaView from '@/components/DispositivosUi/SidebarUi/TelemetriaView.vue'
import ControlDeVersiones from '@/components/DispositivosUi/SidebarUi/ControlDeVersiones.vue'
import RollbackConfirmModal from '@/components/DispositivosUi/SidebarUi/ModalConfirmacion.vue'
import ModalDetalles from '@/components/DispositivosUi/SidebarUi/ModalDetalles.vue'

/* ============================== PROPS ============================== */
const props = defineProps({
    open: Boolean,
    device: Object,
    usuario: String
})

const emit = defineEmits(['close', 'save'])

/* ============================== STATE ============================== */
const activeTab = ref('detalle')
const isEditing = ref(false)
const editingSection = ref(null)

const showRollbackModal = ref(false)
const showDetailsModal = ref(false)

const versionToRollback = ref(null)
const detailsVersion = ref(null)

const tabs = [
    { label: 'Detalle', value: 'detalle' },
    { label: 'Identificador', value: 'identificador' },
    { label: 'URL', value: 'url' },
    { label: 'Último Dato', value: 'telemetria' },
    { label: 'Control de Versiones', value: 'versiones' }
]

const localDevice = ref({})
const originalSnapshot = ref({})

/* ============================== INIT ============================== */
watch(
    () => props.device,
    (newVal) => {
        if (newVal) {
            localDevice.value = {
                ...newVal,
                identifier: newVal.identifier ?? newVal.imei ?? newVal.token ?? ''
            }
            originalSnapshot.value = { ...localDevice.value }
            activeTab.value = 'detalle'
            isEditing.value = false
            editingSection.value = null
        }
    },
    { immediate: true }
)

/* ============================== TABS ============================== */
const onTabClick = (tabValue) => {
    if (isEditing.value) return
    activeTab.value = tabValue
}

/* ============================== MODALES ============================== */
const openRollbackModal = (version) => {
    versionToRollback.value = version
    showRollbackModal.value = true
}

const openDetailsModal = (version) => {
    detailsVersion.value = version
    showDetailsModal.value = true
}

/* ============================== ROLLBACK ============================== */
const doRollback = () => {
    handleRollback(versionToRollback.value)
    showRollbackModal.value = false
}

const handleRollback = (versionData) => {
    if (!versionData || !versionData.snapshot) return

    const snap = versionData.snapshot

    // ✅ BEFORE: estado actual ANTES de aplicar snapshot
    const before = {
        name: localDevice.value.name,
        iccid: localDevice.value.iccid,
        identifier: localDevice.value.identifier,
        token: localDevice.value.token
    }

    // AFTER: estado restaurado
    const after = {
        name: snap.name,
        iccid: snap.iccid,
        identifier: snap.identifier ?? snap.imei ?? snap.token,
        token: snap.token
    }

    // Aplicar rollback al dispositivo
    localDevice.value = {
        ...localDevice.value,
        ...after
    }

    const rollbackVersion = {
        version: (localDevice.value.versions?.length || 0) + 1,
        user: props.usuario || "Usuario desconocido",
        date: new Date().toISOString(),
        changes: `Rollback aplicado a Versión #${versionData.version}`,
        before,
        after
    }

    if (!localDevice.value.versions) localDevice.value.versions = []
    localDevice.value.versions.push(rollbackVersion)
    localDevice.value.versions.sort((a, b) => b.version - a.version)

    emit("save", { ...localDevice.value })
}


/* ============================== EDITAR ============================== */
const startEditing = (section) => {
    if (isEditing.value) return
    originalSnapshot.value = { ...localDevice.value }
    editingSection.value = section
    isEditing.value = true
}

const cancelEditing = () => {
    localDevice.value = { ...originalSnapshot.value }
    isEditing.value = false
    editingSection.value = null
}

const closeSidebar = () => {
    cancelEditing()
    emit('close')
}

/* ============================== SAVE ============================== */
const saveChanges = () => {
    const old = originalSnapshot.value
    const newD = localDevice.value
    const cambios = []

    if (old.name !== newD.name)
        cambios.push(`Nombre: "${old.name}" → "${newD.name}"`)

    if (old.iccid !== newD.iccid)
        cambios.push(`ICCID: "${old.iccid || '—'}" → "${newD.iccid || '—'}"`)

    if (old.identifier !== newD.identifier && newD.type === 'TCP')
        cambios.push(`IMEI: "${old.identifier}" → "${newD.identifier}"`)

    if (cambios.length > 0) {
        const snapshot = { ...old }

        const nuevaVersion = {
            version: (newD.versions?.length || 0) + 1,
            user: props.usuario || "Usuario desconocido",
            date: new Date().toISOString(),
            changes: "• " + cambios.join("\n• "),
            snapshot
        }

        if (!newD.versions) newD.versions = []
        newD.versions.push(nuevaVersion)
        newD.versions.sort((a, b) => b.version - a.version)
    }

    emit('save', { ...newD })
    isEditing.value = false
    editingSection.value = null
}
</script>

<style>
.slide-sidebar-enter-from {
    transform: translateX(100%);
}
.slide-sidebar-enter-to {
    transform: translateX(0);
}
.slide-sidebar-leave-from {
    transform: translateX(0);
}
.slide-sidebar-leave-to {
    transform: translateX(100%);
}
.slide-sidebar-enter-active,
.slide-sidebar-leave-active {
    transition: transform 0.35s ease;
}
</style>
