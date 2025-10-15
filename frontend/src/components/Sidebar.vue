<template>
    <div class="flex h-screen">
        <!-- Sidebar -->
        <aside
            class="w-64 bg-gray-50 border-r border-gray-200 dark:bg-[#162d38] dark:border-neutral-700 flex flex-col sticky top-0">
            <!-- Header -->
            <header class="p-4 flex bg-[#162d38] justify-between items-center">
                <img alt="Logo" src="https://www.gpsenchile.com/wp-content/uploads/2023/06/logowebblanco.png"
                    class="w-30 h-10" />

                <!-- Toggle Dark Mode -->
                <button @click="toggleDarkMode"
                    class="p-2 rounded-full bg-gray-200 hover:bg-[#102372] dark:bg-[#162d38] dark:hover:bg-[#102372]"
                    title="Cambiar tema">
                    <span v-if="isDark" class="text-yellow-300">☀️</span>
                    <span v-else class="text-gray-800">🌙</span>
                </button>
            </header>

            <!-- Perfil -->
            <div class="flex items-center gap-2 p-4 border-b border-gray-100 dark:border-neutral-700">
                <img alt="Perfil" src="https://img.freepik.com/vector-premium/perfil-hombre_1083548-15963.jpg"
                    class="w-10 h-10 rounded-full object-cover" />
                <div>
                    <p class="text-xs">
                        <strong class="block font-medium text-gray-900 dark:text-white">Sebastián Suazo</strong>
                        <span class="text-gray-500 dark:text-neutral-300 text-xs">suazosebastian68@gmail.com</span>
                    </p>
                </div>
            </div>

            <!-- Menú -->
            <nav class="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
                <ul class="space-y-1">
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Dashboard</a>
                    </li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Dispositivos</a>
                    </li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Alertas</a>
                    </li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Motor
                            de Reglas</a></li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Fuentes
                            de Datos</a></li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Analytics</a>
                    </li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Usuarios/Clientes</a>
                    </li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Reportes/Informes</a>
                    </li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Mantenciones</a>
                    </li>
                    <li><a href="#"
                            class="flex items-center gap-x-3.5 py-2 px-2.5 rounded-lg text-sm text-gray-800 hover:bg-gray-100 dark:text-white dark:hover:bg-neutral-700">Configuración</a>
                    </li>
                </ul>
            </nav>
        </aside>


    </div>
</template>

<script>
export default {
    name: "AppSidebar",
    data() {
        return {
            isDark: false,
        };
    },
    mounted() {
        const theme = localStorage.getItem("theme");
        if (theme === "dark") {
            document.documentElement.classList.add("dark");
            this.isDark = true;
        }
    },
    methods: {
        toggleDarkMode() {
            this.isDark = !this.isDark;
            if (this.isDark) {
                document.documentElement.classList.add("dark");
                localStorage.setItem("theme", "dark");
            } else {
                document.documentElement.classList.remove("dark");
                localStorage.setItem("theme", "light");
            }
        },
    },
};
</script>

<style>
html {
    transition: background-color 0.3s, color 0.3s;
}
</style>
