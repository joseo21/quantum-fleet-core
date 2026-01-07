import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '../Views/AdminDashboard.vue'
import Empresas from '../Views/EmpresasView.vue'
import LoginAdmin from '@/Views/LoginAdmin.vue'
import MantencionesView from '@/Views/MantencionesView.vue'
import Copec from '@/Views/CopecDashboard.vue'
import Dispositivos from '@/Views/DispositivosView.vue'
import ReportesView from '@/Views/ReportesView.vue'
import AlertsView from '@/Views/AlertsView.vue'

const routes = [
  { path: '/', name: 'LoginAdmin', component: LoginAdmin },
  { path: '/AdminDashboard', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/empresas', name: 'Empresas', component: Empresas },
  { path: '/mantenciones', name: 'MantencionesView', component: MantencionesView },
  { path: '/copec', name: 'Copec', component: Copec },
  { path: '/dispositivos', name: 'Dispositivos', component: Dispositivos },
  { path: '/reportes', name: 'ReportesView', component: ReportesView },
  { path: '/alertas', name: 'AlertsView', component: AlertsView },

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Middleware simple de autenticación
router.beforeEach((to, from, next) => {
  const isLoggedIn = !!localStorage.getItem('user')

  if (!isLoggedIn && to.path !== '/') {
    next('/')
  } else if (isLoggedIn && to.path === '/') {
    next('/AdminDashboard')
  } else {
    next()
  }
})

export default router
