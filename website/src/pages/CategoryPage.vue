<template>
  <div class="category-page">
    <div class="category-header">
      <div class="container">
        <h1 class="category-title">{{ category?.name }}</h1>
        <p v-if="category?.description" class="category-description">{{ category.description }}</p>
      </div>
    </div>

    <div class="container">
      <div class="controls">
        <div class="view-toggle">
          <button
            @click="viewMode = 'grid'"
            class="view-btn"
            :class="{ active: viewMode === 'grid' }"
            title="卡片視圖"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <rect x="2" y="2" width="7" height="7" rx="1"/>
              <rect x="11" y="2" width="7" height="7" rx="1"/>
              <rect x="2" y="11" width="7" height="7" rx="1"/>
              <rect x="11" y="11" width="7" height="7" rx="1"/>
            </svg>
          </button>
          <button
            @click="viewMode = 'list'"
            class="view-btn"
            :class="{ active: viewMode === 'list' }"
            title="列表視圖"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <rect x="2" y="3" width="16" height="3" rx="1"/>
              <rect x="2" y="8.5" width="16" height="3" rx="1"/>
              <rect x="2" y="14" width="16" height="3" rx="1"/>
            </svg>
          </button>
        </div>
        <div class="article-count">共 {{ articles.length }} 篇文章</div>
      </div>

      <div v-if="loading" class="loading">載入中...</div>
      <div v-else-if="articles.length === 0" class="empty">
        <p>此分類目前沒有文章</p>
      </div>
      <div v-else :class="['articles-container', viewMode]">
        <router-link
          v-for="article in articles"
          :key="article.id"
          :to="`/article/${article.id}`"
          class="article-item card"
        >
          <div
            v-if="viewMode === 'grid'"
            class="article-cover"
            :style="{ backgroundImage: article.cover_image_url ? `url(${article.cover_image_url})` : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }"
          >
            <span v-if="!authStore.isAuthenticated" class="lock-badge">🔒</span>
          </div>

          <div class="article-info">
            <div
              v-if="viewMode === 'list'"
              class="article-cover-small"
              :style="{ backgroundImage: article.cover_image_url ? `url(${article.cover_image_url})` : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }"
            >
              <span v-if="!authStore.isAuthenticated" class="lock-badge-small">🔒</span>
            </div>

            <div class="article-details">
              <h3 class="article-title">{{ article.title }}</h3>
              <div class="article-meta">
                <span class="article-date">{{ formatDate(article.created_at) }}</span>
                <span v-if="article.tags" class="article-tags">{{ article.tags }}</span>
              </div>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import api from '../services/api'

const route = useRoute()
const authStore = useAuthStore()
const category = ref(null)
const articles = ref([])
const loading = ref(true)
const viewMode = ref(localStorage.getItem('viewMode') || 'grid')

const fetchCategory = async (id) => {
  try {
    const { data } = await api.get(`/api/categories`)
    category.value = data.find(c => c.id === parseInt(id))
  } catch (error) {
    console.error('Failed to fetch category:', error)
  }
}

const fetchArticles = async (categoryId) => {
  loading.value = true
  try {
    const { data } = await api.get(`/api/contents?category_id=${categoryId}&status=published`)
    articles.value = data
  } catch (error) {
    console.error('Failed to fetch articles:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchCategory(newId)
    fetchArticles(newId)
  }
}, { immediate: true })

watch(viewMode, (newMode) => {
  localStorage.setItem('viewMode', newMode)
})

onMounted(() => {
  fetchCategory(route.params.id)
  fetchArticles(route.params.id)
})
</script>

<style scoped>
.category-page {
  min-height: calc(100vh - 64px);
  padding-bottom: 60px;
}

.category-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 0 40px;
}

.category-title {
  font-size: 40px;
  font-weight: 700;
  margin-bottom: 12px;
}

.category-description {
  font-size: 18px;
  opacity: 0.9;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px 0;
}

.view-toggle {
  display: flex;
  gap: 8px;
  background: var(--color-bg);
  padding: 4px;
  border-radius: 10px;
  box-shadow: var(--shadow);
}

.view-btn {
  padding: 8px 12px;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-btn:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.view-btn.active {
  background: var(--color-primary);
  color: white;
}

.article-count {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.loading, .empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-secondary);
  font-size: 16px;
}

/* 卡片視圖 */
.articles-container.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.articles-container.grid .article-item {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: var(--color-text-primary);
}

.article-cover {
  width: 100%;
  height: 200px;
  background-size: cover;
  background-position: center;
  border-radius: var(--border-radius) var(--border-radius) 0 0;
  position: relative;
}

.lock-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.article-info {
  padding: 20px;
}

.article-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.article-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.article-tags {
  color: var(--color-primary);
}

/* 列表視圖 */
.articles-container.list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.articles-container.list .article-item {
  display: flex;
  text-decoration: none;
  color: var(--color-text-primary);
  padding: 20px;
}

.articles-container.list .article-info {
  display: flex;
  gap: 20px;
  width: 100%;
  padding: 0;
}

.article-cover-small {
  width: 120px;
  height: 80px;
  flex-shrink: 0;
  background-size: cover;
  background-position: center;
  border-radius: 8px;
  position: relative;
}

.lock-badge-small {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
}

.article-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.articles-container.list .article-title {
  -webkit-line-clamp: 1;
  margin-bottom: 4px;
}

@media (max-width: 768px) {
  .category-title {
    font-size: 28px;
  }

  .controls {
    padding: 20px 0;
  }

  .articles-container.grid {
    grid-template-columns: 1fr;
  }

  .articles-container.list .article-info {
    flex-direction: column;
    gap: 12px;
  }

  .article-cover-small {
    width: 100%;
    height: 160px;
  }
}
</style>
