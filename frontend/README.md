📊 Vue 3 Admin Dashboard

Este proyecto es un panel de administración moderno construido con Vue 3, Tailwind CSS y Vue Router.
Cuenta con un diseño responsivo, barra lateral desplegable, encabezado editable con foto de perfil, y navegación dinámica entre vistas.

🚀 Características principales

🧱 Arquitectura Vue 3 (Composition API)
Estructura modular y mantenible con componentes reutilizables (AppHeader, AppSidebar, etc.).

🎨 Tailwind CSS
Estilos modernos, totalmente responsive y personalizables.

🧭 Vue Router 4
Sistema de rutas SPA para navegar entre vistas como Dashboard y Empresas.

👤 Perfil editable
Permite cambiar la foto de perfil, almacenándola localmente en localStorage.

📱 Responsive Design
Sidebar colapsable en dispositivos móviles mediante menú hamburguesa.

🔒 Estructura lista para autenticación
Incluye lógica base para logout y control de sesión.

🧩 Estructura del proyecto

frontend/
├── src/
│   ├── assets/
│   │   └── tailwind.css
│   ├── components/
│   │   ├── AppHeader.vue
│   │   └── AppSidebar.vue
│   ├── router/
│   │   └── index.js
│   ├── views/
│   │   ├── AdminDashboard.vue
│   │   └── Empresas.vue
│   ├── App.vue
│   └── main.js
├── package.json
├── postcss.config.js
└── tailwind.config.js


⚙️ Instalación y configuración
1️⃣ Clonar el repositorio
git clone https://github.com/tuusuario/vue3-dashboard.git
cd vue3-dashboard

2️⃣ Instalar dependencias

npm install

3️⃣ Iniciar el servidor de desarrollo

npm run serve


La aplicación se abrirá automáticamente en:
👉 http://localhost:8080


🧠 Estructura de componentes principales
🔹 AppHeader.vue

Encabezado superior con:

Logo corporativo

Botón de menú móvil

Perfil editable (imagen y dropdown)

Opción de cerrar sesión

🔹 AppSidebar.vue

Barra lateral con:

Menú de navegación dinámico (Dashboard, Empresas, etc.)

Adaptación automática en pantallas pequeñas

Control de apertura/cierre mediante v-model:isOpen

🔹 AdminDashboard.vue

Vista principal con tarjetas resumen (ventas, costos, usuarios, productos).

🔹 Empresas.vue

Tabla base para listar empresas, lista para conectarse a datos dinámicos.
🧰 Dependencias principales

| Dependencia      | Versión | Descripción               |
| ---------------- | ------- | ------------------------- |
| **vue**          | ^3.2.13 | Framework principal       |
| **vue-router**   | ^4.6.3  | Sistema de rutas SPA      |
| **tailwindcss**  | ^3.x    | Framework CSS moderno     |
| **autoprefixer** | ^10.x   | Compatibilidad de estilos |
| **postcss**      | ^8.x    | Procesador de estilos     |


🧾 Scripts disponibles

| Comando         | Descripción                         |
| --------------- | ----------------------------------- |
| `npm run serve` | Inicia el entorno de desarrollo     |
| `npm run build` | Compila para producción             |
| `npm run lint`  | Ejecuta análisis de código (ESLint) |

🧑‍💻 Próximas mejoras sugeridas

🔐 Integración con sistema de login real.

🧾 Conexión de la vista Empresas con una API o base de datos.

📊 Incorporación de gráficos con Chart.js o ECharts.

🌙 Modo oscuro completo (Dark Mode persistente).

🖋️ Autor

Sebastián Suazo Parada
Proyecto desarrollado como panel administrativo base en Vue 3.

🪪 Licencia

Este proyecto se distribuye bajo la licencia MIT.
Eres libre de usarlo, modificarlo y adaptarlo según tus necesidades.

damelo en formato .md

