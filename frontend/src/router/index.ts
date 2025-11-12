import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '../components/AdminLayout.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import MembersPage from '../pages/MembersPage.vue'
import ContentsPage from '../pages/ContentsPage.vue'
import CategoriesPage from '../pages/CategoriesPage.vue'
import AuditPage from '../pages/AuditPage.vue'
import MediaPage from '../pages/MediaPage.vue'
import { useAuthStore } from '../store/auth'
import { pinia } from '../store'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginPage, name: 'login' },
    {
      path: '/',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: DashboardPage },
        { path: 'members', name: 'members', component: MembersPage },
        { path: 'contents', name: 'contents', component: ContentsPage },
        { path: 'categories', name: 'categories', component: CategoriesPage },
        { path: 'media', name: 'media', component: MediaPage },
        { path: 'audit', name: 'audit', component: AuditPage }
      ]
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore(pinia)
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }
  next()
})

export default router
