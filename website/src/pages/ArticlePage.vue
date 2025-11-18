<template>
  <div class="article-page">
    <div v-if="loading" class="loading">載入中...</div>
    <div v-else-if="!article" class="error">文章不存在</div>
    <div v-else class="container">
      <article class="article">
        <header class="article-header">
          <h1 class="article-title">{{ article.title }}</h1>
          <div class="article-meta">
            <span class="meta-item">📅 {{ formatDate(article.created_at) }}</span>
            <span v-if="article.tags" class="meta-item">🏷️ {{ article.tags }}</span>
            <span v-if="article.category" class="meta-item">
              📁
              <router-link :to="`/category/${article.category_id}`" class="category-link">
                {{ categoryName }}
              </router-link>
            </span>
          </div>
        </header>

        <div
          v-if="article.cover_image_url"
          class="article-cover"
          :style="{ backgroundImage: `url(${article.cover_image_url})` }"
        ></div>

        <div class="article-body" v-html="article.body"></div>

        <footer class="article-footer">
          <router-link
            v-if="article.category_id"
            :to="`/category/${article.category_id}`"
            class="btn btn-secondary"
          >
            ← 返回分類
          </router-link>
        </footer>
      </article>
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
const article = ref(null)
const categoryName = ref('')
const loading = ref(true)

const fetchArticle = async (id) => {
  loading.value = true
  try {
    // 需要認證的 API
    const { data } = await api.get(`/api/contents`)
    article.value = data.find(a => a.id === parseInt(id))

    if (article.value && article.value.category_id) {
      fetchCategoryName(article.value.category_id)
    }

    // 記錄閱讀行為
    if (article.value) {
      await api.post('/api/audit/track', {
        action: 'read_content',
        target_id: id.toString(),
        meta: { title: article.value.title }
      }).catch(err => console.error('Failed to track read:', err))
    }
  } catch (error) {
    console.error('Failed to fetch article:', error)
  } finally {
    loading.value = false
  }
}

const fetchCategoryName = async (categoryId) => {
  try {
    const { data } = await api.get('/api/categories')
    const category = data.find(c => c.id === categoryId)
    if (category) {
      categoryName.value = category.name
    }
  } catch (error) {
    console.error('Failed to fetch category:', error)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchArticle(newId)
  }
}, { immediate: true })

onMounted(() => {
  fetchArticle(route.params.id)
})
</script>

<style scoped>
.article-page {
  min-height: calc(100vh - 64px);
  padding: 40px 0 80px;
}

.loading, .error {
  text-align: center;
  padding: 80px 20px;
  color: var(--color-text-secondary);
  font-size: 18px;
}

.article {
  max-width: 800px;
  margin: 0 auto;
  background: var(--color-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  padding: 48px;
}

.article-header {
  margin-bottom: 32px;
}

.article-title {
  font-size: 36px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 16px;
  color: var(--color-text-primary);
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.category-link {
  color: var(--color-primary);
  text-decoration: none;
}

.category-link:hover {
  text-decoration: underline;
}

.article-cover {
  width: calc(100% + 96px);
  height: 400px;
  margin: 0 -48px 32px;
  background-size: cover;
  background-position: center;
  border-radius: var(--border-radius);
}

.article-body {
  font-size: 18px;
  line-height: 1.8;
  color: var(--color-text-primary);
  margin-bottom: 48px;
}

.article-body :deep(h1),
.article-body :deep(h2),
.article-body :deep(h3) {
  margin-top: 32px;
  margin-bottom: 16px;
  font-weight: 600;
}

.article-body :deep(h1) { font-size: 32px; }
.article-body :deep(h2) { font-size: 28px; }
.article-body :deep(h3) { font-size: 24px; }

.article-body :deep(p) {
  margin-bottom: 16px;
}

.article-body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 24px 0;
}

.article-body :deep(a) {
  color: var(--color-primary);
  text-decoration: none;
}

.article-body :deep(a:hover) {
  text-decoration: underline;
}

.article-body :deep(blockquote) {
  border-left: 4px solid var(--color-primary);
  padding-left: 20px;
  margin: 24px 0;
  color: var(--color-text-secondary);
  font-style: italic;
}

.article-body :deep(code) {
  background: var(--color-bg-secondary);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.article-body :deep(pre) {
  background: var(--color-bg-secondary);
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 24px 0;
}

.article-body :deep(pre code) {
  background: none;
  padding: 0;
}

.article-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 32px;
  border-top: 1px solid var(--color-border);
}

@media (max-width: 768px) {
  .article {
    padding: 32px 24px;
  }

  .article-title {
    font-size: 28px;
  }

  .article-cover {
    width: calc(100% + 48px);
    height: 240px;
    margin: 0 -24px 24px;
  }

  .article-body {
    font-size: 16px;
  }
}
</style>
