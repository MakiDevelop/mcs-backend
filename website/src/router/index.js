import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { pinia } from '../store'

import HomePage from '../pages/HomePage.vue'
import CategoryPage from '../pages/CategoryPage.vue'
import ArticlePage from '../pages/ArticlePage.vue'
import LoginPage from '../pages/LoginPage.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { requiresAuth: false }
  },
  {
    path: '/category/:id',
    name: 'category',
    component: CategoryPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/article/:id',
    name: 'article',
    component: ArticlePage,
    meta: { requiresAuth: true } // 文章內容頁需要登入
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守衛
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore(pinia)

  // 如果需要認證
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登入，跳轉到登入頁
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 已登入但沒有用戶資料，先獲取
    if (!authStore.user) {
      try {
        await authStore.fetchProfile()
      } catch (error) {
        next({ name: 'login', query: { redirect: to.fullPath } })
        return
      }
    }
  }

  // 已登入用戶訪問登入頁，跳轉到首頁
  if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  next()
})

export default router
