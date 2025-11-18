<template>
  <div class="home-page">
    <div class="hero">
      <div class="container">
        <h1 class="hero-title">歡迎來到會員內容平台</h1>
        <p class="hero-subtitle">探索精彩內容，享受專屬體驗</p>
      </div>
    </div>

    <div class="container">
      <section class="categories-section">
        <h2 class="section-title">熱門分類</h2>
        <div class="categories-grid">
          <router-link
            v-for="category in categories"
            :key="category.id"
            :to="`/category/${category.id}`"
            class="category-card"
          >
            <div class="category-icon">📚</div>
            <h3 class="category-name">{{ category.name }}</h3>
            <p class="category-description">{{ category.description || '探索更多精彩內容' }}</p>
          </router-link>
        </div>
      </section>

      <section class="latest-section">
        <h2 class="section-title">最新文章</h2>
        <div class="articles-grid">
          <router-link
            v-for="article in latestArticles"
            :key="article.id"
            :to="`/article/${article.id}`"
            class="article-card card"
          >
            <div
              class="article-cover"
              :style="{ backgroundImage: article.cover_image_url ? `url(${article.cover_image_url})` : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }"
            >
              <span v-if="!authStore.isAuthenticated" class="lock-badge">🔒 需登入</span>
            </div>
            <div class="article-content">
              <h3 class="article-title">{{ article.title }}</h3>
              <p class="article-meta">
                <span class="article-date">{{ formatDate(article.created_at) }}</span>
              </p>
            </div>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../store/auth'
import api from '../services/api'

const authStore = useAuthStore()
const categories = ref([])
const latestArticles = ref([])

const fetchCategories = async () => {
  try {
    const { data } = await api.get('/api/categories')
    categories.value = data
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const fetchLatestArticles = async () => {
  try {
    const { data } = await api.get('/api/contents?status=published&limit=6')
    latestArticles.value = data
  } catch (error) {
    console.error('Failed to fetch articles:', error)
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

onMounted(() => {
  fetchCategories()
  fetchLatestArticles()
})
</script>

<style scoped>
.home-page {
  min-height: calc(100vh - 64px);
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0;
  text-align: center;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}

.hero-subtitle {
  font-size: 20px;
  opacity: 0.9;
  font-weight: 400;
}

.categories-section,
.latest-section {
  padding: 60px 0;
}

.section-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 32px;
  color: var(--color-text-primary);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.category-card {
  background: var(--color-bg);
  border-radius: var(--border-radius);
  padding: 32px;
  text-align: center;
  text-decoration: none;
  color: var(--color-text-primary);
  box-shadow: var(--shadow);
  transition: var(--transition);
}

.category-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px);
}

.category-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.category-name {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.category-description {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.article-card {
  text-decoration: none;
  color: var(--color-text-primary);
  display: flex;
  flex-direction: column;
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

.article-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
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
  color: var(--color-text-secondary);
  font-size: 14px;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .section-title {
    font-size: 24px;
  }

  .categories-grid,
  .articles-grid {
    grid-template-columns: 1fr;
  }
}
</style>
