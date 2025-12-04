<template>
    <div class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50" @click.self="close">
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl 
             w-full max-w-lg border border-gray-300 dark:border-gray-700 
             animate-fadeIn modal-scale p-0 flex flex-col" style="min-height: 480px;">

            <!-- ===== HEADER CON X ===== -->
            <div class="relative w-full flex justify-end p-4">
                <button @click="close" class="text-gray-500 hover:text-gray-800 dark:hover:text-gray-300">
                    <SvgIcon name="close" class="w-5 h-5" />
                </button>
            </div>

            <!-- ===== CONTENIDO SCROLLEABLE ===== -->
            <div class="px-6 pb-6 flex-1 overflow-y-auto">

                <transition :name="step === 1 ? 'slide-left' : 'slide-right'" mode="out-in">
                    <div :key="step" class="space-y-6">

                        <!-- ======================== -->
                        <!-- PASO 1 -->
                        <!-- ======================== -->
                        <div v-if="step === 1" class="space-y-6">

                            <h2 class="text-lg font-semibold text-[#102372]">Nuevo Dispositivo</h2>

                            <!-- Nombre -->
                            <div>
                                <label class="text-sm font-medium">Nombre del Dispositivo</label>
                                <input v-model="form.name" type="text"
                                    class="w-full p-2 border rounded-md bg-gray-50 dark:bg-gray-700"
                                    placeholder="Ej: GPS Camión 12" />
                            </div>

                            <!-- Empresa -->
                            <div>
                                <label class="text-sm font-medium">Empresa</label>
                                <select v-model="form.company"
                                    class="w-full p-2 border rounded-md bg-gray-50 dark:bg-gray-700">
                                    <option disabled value="">Selecciona una empresa</option>
                                    <option v-for="e in empresas" :key="e.id" :value="e.name">
                                        {{ e.name }}
                                    </option>
                                </select>
                            </div>

                            <!-- Fecha -->
                            <div>
                                <label class="text-sm font-medium">Fecha de creación</label>
                                <input v-model="form.createdAt" type="date"
                                    class="w-full p-2 border rounded-md bg-gray-50 dark:bg-gray-700" />
                            </div>

                            <!-- ⭐ ICCID EN PASO 1 ⭐ -->
                            <div>
                                <label class="text-sm font-medium">ICCID (SIM Card)</label>
                                <input v-model="form.iccid" type="text"
                                    class="w-full p-2 border rounded-md bg-gray-50 dark:bg-gray-700"
                                    placeholder="Ej: 8955112309876543210" />
                            </div>

                        </div>

                        <!-- ======================== -->
                        <!-- PASO 2 -->
                        <!-- ======================== -->
                        <div v-else class="space-y-6">

                            <!-- TIPO -->
                            <div class="flex items-center gap-2">
                                <button v-for="t in ['TCP', 'HTTP', 'MQTT']" :key="t" @click="form.type = t" :class="[
                                    'flex-1 py-2 border rounded-md text-sm font-medium transition',
                                    form.type === t
                                        ? 'bg-[#FF6600] border-[#ff6666] text-white'
                                        : 'bg-gray-100 dark:bg-gray-700'
                                ]">
                                    {{ t }}
                                </button>
                            </div>

                            <!-- TCP -->
                            <div v-if="form.type === 'TCP'" class="space-y-2">
                                <label class="text-sm font-medium">IMEI del dispositivo</label>

                                <div class="flex items-center border rounded-md p-2 bg-gray-50 dark:bg-gray-700">
                                    <input v-model="form.imei" class="flex-1 bg-transparent outline-none"
                                        placeholder="Ej: 863453045612345" />
                                </div>
                            </div>

                            <!-- HTTP / MQTT -->
                            <div v-else class="space-y-2">
                                <label class="text-sm font-medium">Token Generado (backend)</label>

                                <div
                                    class="relative flex items-center border rounded-md p-2 bg-gray-50 dark:bg-gray-700">
                                    <input v-model="form.token" readonly
                                        class="flex-1 bg-transparent outline-none text-gray-600 dark:text-gray-300" />

                                    <!-- COPY -->
                                    <div class="relative">
                                        <SvgIcon name="copy" class="w-4 h-4 cursor-pointer" @click="copyToken" />

                                        <span v-if="copied"
                                            class="absolute -top-7 right-0 px-2 py-1 text-xs text-white bg-black rounded-md opacity-90 animate-fadeOut">
                                            Copiado!
                                        </span>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
                </transition>

            </div>

            <!-- FOOTER -->
            <div
                class="sticky bottom-0 left-0 w-full bg-white dark:bg-gray-800 border-t border-gray-300 dark:border-gray-700 p-4 z-20">

                <!-- PASO 1 -->
                <div v-if="step === 1" class="flex justify-between w-full gap-4">

                    <button @click="close"
                        class="w-[48%] py-3 border border-gray-400 rounded-md text-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                        Cancelar
                    </button>

                    <button @click="goToStep2"
                        class="w-[48%] py-3 rounded-md text-white bg-[#102372] hover:bg-[#ff6600] transition flex items-center justify-center gap-2">
                        Siguiente
                        <SvgIcon name="arrow-right" class="w-4 h-4" />
                    </button>

                </div>

                <!-- PASO 2 -->
                <div v-else class="flex justify-between w-full gap-4">

                    <button @click="step = 1"
                        class="w-[48%] py-3 border border-gray-400 rounded-md text-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                        Volver
                    </button>

                    <button @click="emitSave"
                        class="w-[48%] py-3 rounded-md text-white bg-[#102372] hover:bg-[#ff6600] transition">
                        Guardar
                    </button>

                </div>

            </div>

        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import SvgIcon from "@/components/icons/SvgIcon.vue";

const props = defineProps({
    show: Boolean,
    empresas: Array,
    tokenGenerado: String,
});

const emit = defineEmits(["close", "save"]);
const step = ref(1);

const form = ref({
    name: "",
    company: "",
    createdAt: "",
    iccid: "",      // ⭐ AHORA EN PASO 1
    type: "TCP",
    imei: "",
    token: "",
});

const copied = ref(false);

onMounted(() => {
    if (props.tokenGenerado) form.value.token = props.tokenGenerado;
});

watch(
    () => props.tokenGenerado,
    (newVal) => {
        if (newVal) form.value.token = newVal;
    }
);

const close = () => emit("close");

const goToStep2 = () => {
    if (!form.value.name || !form.value.company || !form.value.createdAt) return;
    step.value = 2;
};

const copyToken = () => {
    navigator.clipboard.writeText(form.value.token);
    copied.value = true;
    setTimeout(() => (copied.value = false), 1200);
};

const emitSave = () => {
    emit("save", { ...form.value });
};
</script>
