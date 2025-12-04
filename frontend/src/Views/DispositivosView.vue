<template>
    <div class="w-full bg-transparent">

        <!-- ⭐ CONTAINER GENERAL -->
        <div class="max-w-7xl mx-auto w-full bg-white dark:bg-gray-900 rounded-xl py-6 px-2 sm:px-4">

            <div class="p-2 sm:p-4 w-full flex flex-col">

                <!-- HEADER -->
                <div class="flex flex-col sm:flex-row justify-between items-center mb-4 gap-3">

                    <!-- BARRA DE BÚSQUEDA -->
                    <div class="flex w-full sm:w-2/3 md:w-1/2">
                        <div class="flex w-full border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
                            <div
                                class="flex items-center justify-center px-3 bg-gray-100 dark:bg-gray-800 text-gray-500">
                                <SvgIcon name="search" class="w-4 h-4 sm:w-5 sm:h-5" />
                            </div>
                            <input v-model="searchTerm" placeholder="Buscar dispositivo..."
                                class="flex-1 p-2 text-sm sm:text-base bg-white dark:bg-gray-700 
                                text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-300 focus:outline-none" />

                            <button v-if="searchTerm" @click="searchTerm = ''"
                                class="px-4 bg-[#ff6600] hover:bg-[#e65500] text-white font-semibold text-sm transition">
                                Limpiar
                            </button>
                        </div>
                    </div>

                    <!-- BOTÓN AGREGAR DISPOSITIVO -->
                    <div>
                        <button @click="abrirModal" class="flex items-center justify-center gap-2 px-4 py-2 bg-[#102372] hover:bg-[#e65500] 
                            text-white rounded-md font-medium transition">
                            <SvgIcon name="plus" class="w-5 h-5" />
                            <span>Agregar Dispositivo</span>
                        </button>
                    </div>

                </div>

                <!-- TABLA -->
                <DispositivosTable :devices="filteredDevices" :copiedId="copiedId"
                    @update:selectedIds="selectedIds = $event" @update:selectAll="selectAll = $event"
                    @eliminar="eliminarSeleccionados" @edit="editarDispositivo" @copy-device="copiarDispositivo" />

                <!-- MODAL AGREGAR -->
                <AddDispositivoModal v-if="showAddModal" :show="showAddModal" :empresas="empresas"
                    :token-generado="tokenDesdeBackend" @close="showAddModal = false" @save="crearDispositivo" />

                <!-- ⭐ SIDEBAR EDITAR DISPOSITIVO -->
                <SidebarDevice :open="showSidebar" :device="deviceToEdit" :usuario="usuarioActual"
                    @close="showSidebar = false" @save="guardarEdicion" />

            </div>

        </div>

    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import SvgIcon from '@/components/icons/SvgIcon.vue'
import DispositivosTable from '@/components/DispositivosUi/DispositivosTable.vue'
import AddDispositivoModal from '@/components/DispositivosUi/AgregarDispositivos.vue'
import SidebarDevice from '@/components/DispositivosUi/SidebarDispositivos.vue'

/* --------------------------- USUARIO ACTUAL --------------------------- */
/* Aquí defines quién está editando. En producción debería venir del login. */

const usuarioActual = ref("Sebastián Suazo")

/* --------------------------- STATE --------------------------- */

const selectedIds = ref([])
const selectAll = ref(false)

const showAddModal = ref(false)
const showSidebar = ref(false)
const deviceToEdit = ref(null)

const copiedId = ref(null)

const empresas = ref([
    { id: 1, name: "Safco" },
    { id: 2, name: "Demo Combustible" },
])

const tokenDesdeBackend = ref("")

/* --------------------------- MODAL AGREGAR --------------------------- */

const abrirModal = () => {
    showAddModal.value = true
}

const crearDispositivo = (nuevo) => {
    devices.value.push({
        id: devices.value.length + 1,
        name: nuevo.name,
        company: nuevo.company,
        createdAt: nuevo.createdAt,
        type: nuevo.type,
        imei: nuevo.imei || null,
        token: nuevo.token || null,
        lastReport: "—",
        iccid: nuevo.iccid || null,
        versions: []
    })

    showAddModal.value = false
}

/* --------------------------- DISPOSITIVOS --------------------------- */

const devices = ref([
    { id: 1, name: 'GPS Camión 12', company: 'Safco', imei: '863453045612345', token: null, iccid: '8955112309876543210', createdAt: '2025-10-28', lastReport: '2025-11-03 14:32', type: 'TCP', versions: [] },
    { id: 2, name: 'Medidor Estanque 1', company: 'Demo Combustible', imei: null, token: '863A1DSDF4561245', iccid: null, createdAt: '2025-09-10', lastReport: '2025-11-03 09:10', type: 'HTTP', versions: [] },
    { id: 3, name: 'GPS Grúa Horquilla 7', company: 'Safco', imei: '864502349876123', token: null, iccid: '8955100099123412345', createdAt: '2025-08-15', lastReport: '2025-11-03 12:05', type: 'MQTT', versions: [] },
    { id: 4, name: 'Sensor Estanque Sur', company: 'Demo Combustible', imei: null, token: 'ABC123TOKENESTS', iccid: '8955123498347561234', createdAt: '2025-07-02', lastReport: '2025-11-02 18:29', type: 'HTTP', versions: [] },
    { id: 5, name: 'GPS Retroexcavadora 2', company: 'Constructora Andes', imei: '865432109876543', token: null, iccid: '8955112345557763211', createdAt: '2025-05-21', lastReport: '2025-11-03 16:40', type: 'TCP', versions: [] },
    { id: 6, name: 'Medidor Estanque Principal', company: 'Petro Sur', imei: null, token: 'TOKENMED123456', iccid: '8955100045678912345', createdAt: '2025-06-10', lastReport: '2025-11-03 08:15', type: 'HTTP', versions: [] },
    { id: 7, name: 'GPS Camión Tolva 21', company: 'Safco', imei: '867890123456782', token: null, iccid: null, createdAt: '2025-03-18', lastReport: '2025-11-01 19:22', type: 'TCP', versions: [] },
    { id: 8, name: 'Sensor Estanque Norte', company: 'Demo Combustible', imei: null, token: 'TOKENNORTE9988', iccid: '8955198765432101123', createdAt: '2025-02-11', lastReport: '2025-11-03 06:55', type: 'MQTT', versions: [] },
    { id: 9, name: 'GPS Camioneta Técnica 3', company: 'Mantenciones Pro', imei: '862345678900123', token: null, iccid: '8955111001122334455', createdAt: '2025-01-26', lastReport: '2025-11-03 10:48', type: 'TCP', versions: [] },
    { id: 10, name: 'Medidor Estanque Secundario', company: 'Petro Sur', imei: null, token: 'TOKENSEC556677', iccid: '8955105544332211987', createdAt: '2024-12-05', lastReport: '2025-11-03 07:31', type: 'HTTP', versions: [] }
])

/* --------------------------- FUNCIONES --------------------------- */

const eliminarSeleccionados = (ids) => {
    devices.value = devices.value.filter(d => !ids.includes(d.id))
    selectedIds.value = []
    selectAll.value = false
}

const editarDispositivo = (device) => {
    deviceToEdit.value = { ...device }
    showSidebar.value = true
}

const guardarEdicion = (editado) => {

    const index = devices.value.findIndex(d => d.id === editado.id)
    if (index !== -1) {
        devices.value[index] = { ...editado }
    }

    showSidebar.value = false
}

const copiarDispositivo = (device) => {
    const texto = `
Nombre: ${device.name}
Empresa: ${device.company}
Tipo: ${device.type}
Identificador: ${device.imei ?? device.token}
Creado: ${device.createdAt}
Último reporte: ${device.lastReport}
`.trim()

    navigator.clipboard.writeText(texto)
    copiedId.value = device.id

    setTimeout(() => copiedId.value = null, 1000)
}

/* --------------------------- BUSCADOR --------------------------- */

const searchTerm = ref('')

const filteredDevices = computed(() => {
    const term = searchTerm.value.toLowerCase().trim()
    if (!term) return devices.value

    return devices.value.filter(d => {
        return (
            d.name.toLowerCase().includes(term) ||
            d.company.toLowerCase().includes(term) ||
            (d.imei && d.imei.toLowerCase().includes(term)) ||
            (d.token && d.token.toLowerCase().includes(term)) ||
            (d.iccid && d.iccid.toLowerCase().includes(term)) ||
            d.type.toLowerCase().includes(term) ||
            (d.createdAt && d.createdAt.toLowerCase().includes(term)) ||
            (d.lastReport && d.lastReport.toLowerCase().includes(term))
        )
    })
})

</script>
