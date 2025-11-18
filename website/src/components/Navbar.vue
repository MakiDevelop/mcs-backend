<template>
  <nav class="navbar">
    <div class="container navbar-content">
      <div class="navbar-brand">
        <router-link to="/" class="brand-link">
          會員內容平台
        </router-link>
      </div>

      <div class="navbar-menu">
        <router-link to="/" class="nav-link" :class="{ active: $route.name === 'home' }">
          首頁
        </router-link>
        <router-link
          v-for="category in categories"
          :key="category.id"
          :to="`/category/${category.id}`"
          class="nav-link"
          :class="{ active: $route.params.id == category.id }"
        >
          {{ category.name }}
        </router-link>
      </div>

      <div class="navbar-actions">
        <div v-if="authStore.isAuthenticated" class="user-menu">
          <span class="user-name">{{ authStore.user?.name }}</span>
          <button @click="handleLogout" class="btn-logout">登出</button>
        </div>
        <router-link v-else to="/login" class="btn btn-primary">登入</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import api from '../services/api'

const router = useRouter()
const authStore = useAuthStore()
const categories = ref([])

const fetchCategories = async () => {
  try {
    const { data } = await api.get('/api/categories')
    categories.value = data
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  fetchCategories()
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchProfile()
  }
})
</script>

<style scoped>
.navbar {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  gap: 32px;
}

.navbar-brand {
  flex-shrink: 0;
}

.brand-link {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  text-decoration: none;
  transition: var(--transition);
}

.brand-link:hover {
  color: var(--color-primary);
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  overflow-x: auto;
  scrollbar-width: none;
}

.navbar-menu::-webkit-scrollbar {
  display: none;
}

.nav-link {
  padding: 8px 16px;
  border-radius: 8px;
  color: var(--color-text-primary);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: var(--transition);
  white-space: nowrap;
}

.nav-link:hover {
  background: var(--color-bg-secondary);
  color: var(--color-primary);
}

.nav-link.active {
  background: var(--color-primary);
  color: white;
}

.navbar-actions {
  flex-shrink: 0;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.btn-logout {
  padding: 8px 16px;
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.btn-logout:hover {
  background: var(--color-border);
}

@media (max-width: 768px) {
  .navbar-content {
    gap: 16px;
  }

  .navbar-menu {
    gap: 4px;
  }

  .nav-link {
    padding: 6px 12px;
    font-size: 14px;
  }

  .user-name {
    display: none;
  }
}
</style>
