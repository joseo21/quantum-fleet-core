<template>
  <div class="bg-white rounded-2xl shadow-xl p-6 space-y-6 border border-[#E7E7E9]">

    <!-- Filtros -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

      <div class="flex flex-col">
        <label class="text-xs font-medium text-[#1D292F]">Desde</label>
        <input v-model="desde" type="date"
          class="border border-[#E7E7E9] text-sm p-2 rounded-md bg-[#F3F3F3] focus:ring-2 focus:ring-[#102372]" />
      </div>

      <div class="flex flex-col">
        <label class="text-xs font-medium text-[#1D292F]">Hasta</label>
        <input v-model="hasta" type="date"
          class="border border-[#E7E7E9] text-sm p-2 rounded-md bg-[#F3F3F3] focus:ring-2 focus:ring-[#102372]" />
      </div>

      <!-- ============= TIPO ============= -->
      <div class="flex flex-col">
        <label class="text-xs font-medium text-[#1D292F]">Tipo</label>

        <select v-model="tipo" @change="cambiarTipo"
          class="border border-[#E7E7E9] bg-[#F3F3F3] text-sm p-2 rounded-md focus:ring-2 focus:ring-[#102372]">

          <option value="carga">Carga (Excel)</option>
          <option value="descarga">Descarga (Manual)</option>

          <!-- ⬅ NUEVA OPCIÓN -->
          <option value="facturas">Facturas (PDF)</option>
        </select>
      </div>

      <div class="flex items-end">
        <button @click="buscar"
          class="w-full text-sm font-semibold bg-[#102372] hover:bg-[#FF6600] text-white px-4 py-2 rounded-md shadow">
          Buscar
        </button>
      </div>

    </div>

    <!-- ===================== CAMPOS A MOSTRAR ===================== -->
    <div class="space-y-2">
      <label class="block text-sm font-semibold text-[#1D292F]">Campos a mostrar:</label>

      <div class="flex flex-wrap gap-2">
        <button v-for="col in columnasBase" :key="col" @click="toggleCol(col)"
          class="text-xs px-3 py-1 rounded-full border transition shadow-sm"
          :class="columnasVisibles.includes(col)
            ? 'bg-[#6EC1E4]/20 text-[#102372] border-[#6EC1E4]'
            : 'bg-[#E7E7E9] text-[#54595F] border-[#D0D0D0] hover:bg-[#DADADA]'">
          {{ col }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center text-sm text-[#102372] py-3">
      Cargando datos...
    </div>

  </div>
</template>

<script>
const API_URL = process.env.VUE_APP_API_URL || "http://localhost:3001";


export default {
  name: 'SearchPanel',
  emits: ['loaded-data', 'update-columns', 'tipo-changed'],

  data() {
    return {
      data: [],
      loading: false,
      desde: '',
      hasta: '',
      tipo: 'carga',

      columnasCarga: [
        'Fecha', 'Hora', 'Zona', 'Patente', 'Región',
        'Comuna', 'Estación de Servicio', 'Litros', 'Precio', 'Monto', 'Odómetro', 'Proveedor'
      ],

      columnasDescarga: [
        'Fecha', 'Tipo de Descarga', 'Litros', 'Dispositivo', 'Encargado'
      ],

      columnasFacturas: [
        'Número', 'Fecha', 'Producto', 'Proveedor', 'Litros', 'Total'
      ],

      columnasVisibles: []
    };
  },

  mounted() {
    this.columnasVisibles = [...this.columnasCarga];
    this.$emit('update-columns', [...this.columnasVisibles]);
  },

  computed: {
    columnasBase() {
      if (this.tipo === 'carga') return this.columnasCarga;
      if (this.tipo === 'descarga') return this.columnasDescarga;
      if (this.tipo === 'facturas') return this.columnasFacturas;
      return [];
    }
  },

  methods: {

    // ===================== CAMBIAR TIPO =====================
    cambiarTipo() {
      this.data = [];
      this.desde = '';
      this.hasta = '';

      if (this.tipo === 'carga') {
        this.columnasVisibles = [...this.columnasCarga];
      }
      if (this.tipo === 'descarga') {
        this.columnasVisibles = [...this.columnasDescarga];
      }
      if (this.tipo === 'facturas') {
        this.columnasVisibles = [...this.columnasFacturas];
      }

      this.$emit('tipo-changed', this.tipo);
      this.$emit('update-columns', [...this.columnasVisibles]);
      this.$emit('loaded-data', []);
    },

    // ===================== MOSTRAR / OCULTAR COLUMNAS =====================
    toggleCol(col) {
      if (this.columnasVisibles.includes(col)) {
        this.columnasVisibles = this.columnasVisibles.filter(c => c !== col);
      } else {
        const base = this.columnasBase;
        this.columnasVisibles = base.filter(c => [...this.columnasVisibles, col].includes(c));
      }

      this.$emit('update-columns', [...this.columnasVisibles]);
    },

    // ===================== BUSCAR =====================
    async buscar() {
      if (!this.desde || !this.hasta) {
        console.warn("⏭️ Buscar cancelado: faltan fechas");
        return;
      }

      this.loading = true;

      try {
        let url = "";

        if (this.tipo === 'carga') {
          url = `${API_URL}/buscar?desde=${this.desde}&hasta=${this.hasta}`;
        }

        if (this.tipo === 'descarga') {
          url = `${API_URL}/descarga/manual?desde=${this.desde}&hasta=${this.hasta}`;
        }

        if (this.tipo === 'facturas') {
          url = `${API_URL}/facturas/buscar?desde=${this.desde}&hasta=${this.hasta}`;
        }

        const res = await fetch(url);
        const arr = await res.json();
        if (!Array.isArray(arr)) return;

        this.$emit('tipo-changed', this.tipo);

        // ------------------- CARGA -------------------
        if (this.tipo === 'carga') {
          this.data = arr.map(i => ({
            Fecha: i['Fecha'] || '',
            Hora: i['Hora'] || '',
            Zona: i['Zona'] || '',
            Patente: i['Patente'] || '',
            Región: i['Región'] || '',
            Comuna: i['Comuna'] || '',
            'Estación de Servicio': i['Estación de Servicio'] || '',
            Litros: Number(i['Litros']) || 0,
            Precio: Number(i['Precio']) || 0,
            Monto: Number(i['Monto']) || 0,
            Odómetro: i['Odómetro'] || '',
            Proveedor: i['Proveedor'] || ''
          }));
        }

        // ------------------- DESCARGA -------------------
        if (this.tipo === 'descarga') {
          this.data = arr.map(i => ({
            Fecha: i.Fecha || '',
            'Tipo de Descarga': i.TipoDescarga || '',
            Litros: i.Litros || 0,
            Dispositivo: i.Dispositivo || '',
            Encargado: i.Encargado || ''
          }));
        }

        // ------------------- FACTURAS -------------------
        if (this.tipo === 'facturas') {
          this.data = arr.map(i => ({
            Número: i.numero_factura || '',
            Fecha: i.fecha || '',
            Producto: i.producto || '',
            Proveedor: i.proveedor || '',
            Litros: i.litros || 0,
            Total: i.total || 0
          }));
        }

        this.$emit('loaded-data', this.data);

      } finally {
        this.loading = false;
      }
    }

  }
};
</script>
