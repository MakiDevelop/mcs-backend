<template>
  <div class="page">
    <div class="page-header">
      <el-button @click="fetchLogs" :loading="loading">重新整理</el-button>
    </div>
    <el-table :data="logs" stripe>
      <el-table-column prop="action" label="行為" width="160" />
      <el-table-column prop="target_id" label="目標" width="160" />
      <el-table-column prop="ip_address" label="IP" width="160" />
      <el-table-column label="時間" width="200">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
      </el-table-column>
      <el-table-column prop="meta" label="Meta" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import api from '../services/api'

interface AuditLog {
  id: number
  action: string
  target_id: string | null
  ip_address: string | null
  created_at: string
  meta: string | null
}

const logs = ref<AuditLog[]>([])
const loading = ref(false)

const fetchLogs = async () => {
  loading.value = true
  try {
    const { data } = await api.get<AuditLog[]>('/api/audit/logs')
    logs.value = data
  } finally {
    loading.value = false
  }
}

onMounted(fetchLogs)
</script>

<style scoped>
.page {
  padding: 16px;
}
.page-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}
</style>
