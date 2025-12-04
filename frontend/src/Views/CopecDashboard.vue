<template>
  <div class="space-y-12">

    <div class="bg-white rounded-3xl shadow-xl p-8 border border-gray-200 space-y-10">
      <KpiCards :data="data" />

      <SearchPanel
        ref="searchPanel"
        @loaded-data="onDataLoaded"
        @update-columns="columns = $event"
        @tipo-changed="cambiarModo"
      />

      <!-- TABLA CARGA -->
      <DataTable
        v-if="modo === 'carga'"
        :data="data"
        :columns="columns"
        @open-uploader="showUploader = true"
      />

      <!-- TABLA DESCARGA -->
      <DataTableDescarga
        v-if="modo === 'descarga'"
        :data="data"
        :columns="columns"
        @open-manual-form="showManualForm = true"
      />

      <!-- TABLA FACTURAS -->
      <FacturaTable
        v-if="modo === 'facturas'"
        :facturas="data"
        :columns="columns"
        v-model="selectedFacturas"
        @nuevaFactura="showFacturaModal = true"
        @eliminarSeleccionadas="eliminarFacturas"
      />
    </div>

    <!-- Modal Excel -->
    <FileUploader
      v-if="showUploader"
      @uploaded="onFilesUploaded"
      @close="showUploader = false"
    />

    <!-- Modal Descarga manual -->
    <ManualForm
      v-if="showManualForm"
      @close="showManualForm = false"
      @saved="recargarManual"
    />

    <!-- Modal Facturas PDF -->
    <FacturaUploadModal
      v-if="showFacturaModal"
      @close="showFacturaModal = false"
      @uploaded="recargarFacturas"
    />

  </div>
</template>

<script>
import FileUploader from '../components/CopecUi/Cargas/FileUploader.vue'
import ManualForm from '../components/CopecUi/Descargas/ManualForm.vue'
import SearchPanel from '../components/CopecUi/Cargas/SearchPanel.vue'
import KpiCards from '../components/CopecUi/Cargas/KpiCards.vue'
import DataTable from '../components/CopecUi/Cargas/DataTable.vue'
import DataTableDescarga from '../components/CopecUi/Descargas/DataTableDescarga.vue'
import FacturaTable from '../components/CopecUi/Facturas/FacturaTable.vue'
import FacturaUploadModal from '../components/CopecUi/Facturas/FacturaUploadModal.vue'

export default {
  name: 'CopecDashboard',

  components: {
    FileUploader,
    ManualForm,
    SearchPanel,
    KpiCards,
    DataTable,
    DataTableDescarga,
    FacturaTable,
    FacturaUploadModal
  },

  data() {
    return {
      data: [],
      modo: 'carga',

      columns: [
        'Fecha', 'Hora', 'Zona', 'Patente', 'Región',
        'Comuna', 'Estación de Servicio', 'Litros', 'Precio', 'Monto', 'Odómetro', 'Proveedor'
      ],

      showUploader: false,
      showManualForm: false,
      showFacturaModal: false,

      selectedFacturas: []
    }
  },

  methods: {

    cambiarModo(nuevoModo) {
      this.modo = nuevoModo

      // -------------------------------
      // TABLA DE CARGAS NORMALES
      // -------------------------------
      if (nuevoModo === 'carga') {
        this.columns = [
          'Fecha', 'Hora', 'Zona', 'Patente', 'Región',
          'Comuna', 'Estación de Servicio', 'Litros',
          'Precio', 'Monto', 'Odómetro', 'Proveedor'
        ]
      }

      // -------------------------------
      // TABLA DESCARGAS MANUALES
      // -------------------------------
      if (nuevoModo === 'descarga') {
        this.columns = [
          'Fecha', 'Tipo de Descarga', 'Litros', 'Dispositivo', 'Encargado'
        ]
      }

      // -------------------------------
      // TABLA DE FACTURAS (MODIFICADO)
      // -------------------------------
      if (nuevoModo === 'facturas') {
        this.columns = [
          "numero_factura",
          "producto",
          "proveedor",
          "fecha",
          "litros",
          "total"
        ]
      }
    },

    onDataLoaded(rows) {
      this.data = rows
    },

    onFilesUploaded() {
      this.$refs.searchPanel.buscar()
    },

    recargarManual() {
      this.$refs.searchPanel.buscar()
    },

    recargarFacturas() {
      this.$refs.searchPanel.buscar()
    },

    eliminarFacturas() {
      console.log("Eliminar:", this.selectedFacturas)
    }
  }
}
</script>
