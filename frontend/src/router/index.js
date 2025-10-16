import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '../Views/AdminDashboard.vue'
import Empresas from '../Views/Empresas.vue'

const routes = [
  { path: '/', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/empresas', name: 'Empresas', component: Empresas }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
