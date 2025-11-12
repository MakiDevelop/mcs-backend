<template>
  <el-container class="layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">MCS Admin</div>
      <el-menu :default-active="activeRoute" class="nav" router>
        <el-menu-item index="/">Dashboard</el-menu-item>
        <el-menu-item index="/members">Members</el-menu-item>
        <el-menu-item index="/contents">Contents</el-menu-item>
        <el-menu-item index="/categories">Categories</el-menu-item>
        <el-menu-item index="/media">Media</el-menu-item>
        <el-menu-item index="/audit">Audit</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-title">{{ currentTitle }}</div>
        <div class="header-actions">
          <span class="user-name">{{ authStore.user?.name }}</span>
          <el-button type="primary" link @click="handleLogout">Logout</el-button>
        </div>
      </el-header>
      <el-main class="content">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'

import { useAuthStore } from '../store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const titles: Record<string, string> = {
  dashboard: 'Dashboard',
  members: 'Member Management',
  contents: 'Content Management',
  categories: 'Category Management',
  audit: 'Behavior Audit'
}

const activeRoute = computed(() => route.path)
const currentTitle = computed(() => titles[route.name as string] || 'Dashboard')

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  if (!authStore.user) {
    authStore.fetchProfile()
  }
})
</script>

<style scoped>
.layout {
  height: 100vh;
}
.sidebar {
  background: #0f172a;
  color: #fff;
  display: flex;
  flex-direction: column;
}
.logo {
  padding: 24px;
  font-weight: 700;
  font-size: 20px;
}
.nav {
  border-right: none;
  flex: 1;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}
.header-title {
  font-size: 20px;
  font-weight: 600;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-name {
  font-weight: 500;
}
.content {
  background: #f4f6fb;
  min-height: calc(100vh - 60px);
}
</style>
