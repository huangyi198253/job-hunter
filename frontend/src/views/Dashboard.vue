<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { applications, jobs } from '../api'

const router = useRouter()
const auth = useAuthStore()
const stats = ref(null)
const recentJobs = ref([])

onMounted(async () => {
  try {
    const r = await applications.stats()
    stats.value = r.data
  } catch {}
  try {
    const r = await jobs.list({ page_size: 5, sort_by: 'created_at', sort_order: 'desc' })
    recentJobs.value = r.data.items || []
  } catch {}
})

const statItems = computed(() => [
  { label: '收藏', count: stats.value?.total_saved, color: '#64748b' },
  { label: '已投递', count: stats.value?.total_applied, color: '#2563eb' },
  { label: '笔试', count: stats.value?.total_written_test, color: '#f59e0b' },
  { label: '面试', count: stats.value?.total_interview, color: '#8b5cf6' },
  { label: 'Offer', count: stats.value?.total_offer, color: '#10b981' },
  { label: '拒信', count: stats.value?.total_rejected, color: '#ef4444' },
])

import { computed } from 'vue'
</script>

<template>
  <div class="page">
    <div class="top-bar"><h1>📊 概况</h1></div>
    <div class="container">
      <!-- 今日待办 -->
      <div class="card" v-if="stats && (stats.today_deadlines > 0 || stats.upcoming_reminders > 0)">
        <div class="card-title">⏰ 待办提醒</div>
        <p v-if="stats.today_deadlines > 0" class="todo-item">📅 今日有 <strong>{{ stats.today_deadlines }}</strong> 件事项待处理</p>
        <p v-if="stats.upcoming_reminders > 0" class="todo-item">🔔 共 <strong>{{ stats.upcoming_reminders }}</strong> 条即将到来的提醒</p>
      </div>
      <div class="card" v-else-if="stats">
        <div class="card-title">✅ 今日暂无待办</div>
      </div>

      <!-- 投递概况 -->
      <div class="card">
        <div class="card-title">📈 投递概况</div>
        <div class="stat-grid">
          <div v-for="s in statItems" :key="s.label" class="stat-item" @click="router.push('/applications')">
            <div class="stat-count" :style="{color:s.color}">{{ s.count }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>
      </div>

      <!-- 最新岗位 -->
      <div class="card">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>🆕 最新岗位</span>
          <router-link to="/jobs" class="btn btn-sm btn-outline">查看全部</router-link>
        </div>
        <div v-if="recentJobs.length === 0" class="empty">暂无岗位数据</div>
        <div v-for="j in recentJobs" :key="j.id" class="job-mini">
          <div class="job-mini-company">{{ j.company }}</div>
          <div class="job-mini-title">{{ j.title }}</div>
          <span class="tag tag-blue">{{ j.company_type }}</span>
          <span class="tag tag-gray">{{ j.location }}</span>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="quick-actions">
        <button class="btn btn-primary" @click="router.push('/jobs')">💼 浏览岗位</button>
        <button class="btn btn-outline" @click="router.push('/profile')">👤 编辑档案</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.stat-item{text-align:center;padding:8px;border-radius:10px;background:var(--gray-50);cursor:pointer}
.stat-count{font-size:28px;font-weight:700}
.stat-label{font-size:12px;color:var(--gray-400);margin-top:2px}
.todo-item{padding:8px 12px;background:#fef3c7;border-radius:8px;font-size:14px;margin-bottom:6px}
.job-mini{padding:10px 0;border-bottom:1px solid var(--gray-100)}
.job-mini:last-child{border-bottom:none}
.job-mini-company{font-size:13px;color:var(--gray-500);font-weight:600}
.job-mini-title{font-size:15px;font-weight:600;margin:2px 0 4px}
.quick-actions{display:flex;gap:8px;margin-top:12px}
.quick-actions .btn{flex:1;padding:14px 0;font-size:15px}
</style>
