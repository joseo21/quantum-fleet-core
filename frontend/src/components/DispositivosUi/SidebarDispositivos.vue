<template>
    <!-- OVERLAY -->
    <div v-if="open" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40" @click="handleOverlayClick"></div>

    <!-- SIDEBAR -->
    <transition name="slide-sidebar">
        <div v-if="open" class="fixed top-0 right-0 h-full bg-white dark:bg-gray-900 shadow-xl z-50
                   border-l border-gray-200 dark:border-gray-700 flex flex-col" style="width: 50vw;">

            <!-- ⭐ HEADER AZUL CORPORATIVO -->
            <div class="px-5 pt-5 pb-3 border-b border-[#143ba7]
                        bg-[#102372] text-white">

                <!-- TÍTULO + BOTÓN CERRAR -->
                <div class="flex items-center justify-between mb-4">

                    <div class="flex items-center gap-3">
                        <div class="p-2 rounded-xl bg-white/20">
                            <SvgIcon name="dispositivos" class="w-5 h-5 text-white" />
                        </div>

                        <h2 class="text-lg font-semibold tracking-tight">
                            Detalles del Dispositivo
                        </h2>
                    </div>

                    <button @click="closeSidebar" class="p-2 rounded-lg hover:bg-white/20 transition">
                        <SvgIcon name="close" class="w-5 h-5 text-white" />
                    </button>
                </div>

                <!-- ⭐ TABS CON FONDO MÁS CLARO (SEPARACIÓN VISUAL) -->
                <div class="flex gap-6 text-sm font-medium bg-[#143ba7] px-3 py-2 rounded-md">

                    <button v-for="t in tabs" :key="t.value" @click="onTabClick(t.value)" :class="[
                        'pb-1 relative transition font-semibold',
                        activeTab === t.value
                            ? 'text-white'
                            : 'text-white/70 hover:text-white/90',
                        isEditing ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                    ]">
                        {{ t.label }}

                        <!-- Línea activa -->
                        <span v-if="activeTab === t.value"
                            class="absolute left-0 right-0 -bottom-0.5 h-[3px] bg-white rounded-full">
                        </span>
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
                <TelemetriaView v-else-if="activeTab === 'telemetria'" :data="localDevice.data" />


                <ControlDeVersiones v-if="activeTab === 'versiones'" :versions="localDevice.versions"
                    @confirm-rollback="openRollbackModal" @show-details="openDetailsModal" />

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
    <!-- MODALES -->
    <!-- ============================ -->
    <RollbackConfirmModal v-if="showRollbackModal" :show="showRollbackModal" :version="versionToRollback"
        :device="localDevice" @cancel="showRollbackModal = false" @confirm="doRollback" />

    <ModalDetalles v-if="showDetailsModal" :show="showDetailsModal" :version="detailsVersion"
        @close="showDetailsModal = false" />
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
import telemetriaDummyData from "@/dummy/telemetriaDummy.js";


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

            // Asignar los datos del dispositivo real
            localDevice.value = {
                ...newVal,
                identifier: newVal.identifier ?? newVal.imei ?? newVal.token ?? ''
            }

            // 🔵 Agregar el array de telemetría ficticia
            localDevice.value.data = telemetriaDummyData;

            // Snapshot original para rollback/edición
            originalSnapshot.value = { ...localDevice.value }

            // Estado inicial del sidebar
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
