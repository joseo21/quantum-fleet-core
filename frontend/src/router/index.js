import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '../Views/AdminDashboard.vue'
import Empresas from '../Views/EmpresasView.vue'
import LoginAdmin from '@/Views/LoginAdmin.vue'
import MantencionesView from '@/Views/MantencionesView.vue'

const routes = [
  { path: '/', name: 'LoginAdmin', component: LoginAdmin },
  { path: '/AdminDashboard', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/empresas', name: 'Empresas', component: Empresas },
  { path: '/mantenciones', name: 'MantencionesView', component: MantencionesView }

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
