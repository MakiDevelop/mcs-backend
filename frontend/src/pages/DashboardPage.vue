<template>
  <div class="page">
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card>
          <div class="stat-title">會員數</div>
          <div class="stat-value">{{ stats?.members ?? '-' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-title">內容數</div>
          <div class="stat-value">{{ stats?.contents ?? '-' }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-4">
      <el-col :span="12">
        <el-card>
          <template #header>最近登入</template>
          <el-empty v-if="!stats?.recent_logins?.length" description="無紀錄" />
          <el-timeline v-else>
            <el-timeline-item v-for="item in stats.recent_logins" :key="item.time" :timestamp="formatTime(item.time)">
              {{ item.user_id || '未知' }} - {{ item.ip }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>最近閱讀</template>
          <el-empty v-if="!stats?.recent_reads?.length" description="無紀錄" />
          <el-timeline v-else>
            <el-timeline-item v-for="item in stats.recent_reads" :key="item.time" :timestamp="formatTime(item.time)">
              Content #{{ item.target_id }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import api from '../services/api'

interface DashboardStats {
  members: number
  contents: number
  recent_logins: Array<{ user_id: string | null; ip: string | null; time: string }>
  recent_reads: Array<{ user_id: string | null; target_id: string | null; time: string }>
}

const stats = ref<DashboardStats | null>(null)

const loadStats = async () => {
  const { data } = await api.get('/api/dashboard')
  stats.value = data
}

const formatTime = (value: string) => new Date(value).toLocaleString()

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.page {
  padding: 16px;
}
.stat-title {
  color: #64748b;
}
.stat-value {
  font-size: 32px;
  font-weight: 700;
}
.mt-4 {
  margin-top: 16px;
}
</style>
