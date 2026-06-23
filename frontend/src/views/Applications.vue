<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { applications as api } from '../api'

const router = useRouter()
const items = ref([])
const total = ref(0)
const page = ref(1)
const statusFilter = ref('')
const loading = ref(false)
const showNewForm = ref(false)
const newApp = ref({ company:'', title:'', location:'', company_type:'', job_category:'', status:'收藏' })

const statuses = ['收藏','已投递','笔试','面试','Offer','拒信','放弃']

async function load() {
  loading.value = true
  try {
    const r = await api.list({ status: statusFilter.value || undefined, page: page.value })
    items.value = r.data.items
    total.value = r.data.total
  } catch {}
  loading.value = false
}

onMounted(load)
watch([page, statusFilter], load)

async function createApp() {
  try {
    await api.create(newApp.value)
    showNewForm.value = false
    newApp.value = { company:'', title:'', location:'', company_type:'', job_category:'', status:'收藏' }
    load()
  } catch (e) { alert(e.response?.data?.detail || '创建失败') }
}

function statusTag(s) {
  if (s === '收藏') return 'tag-gray'
  if (s === '已投递') return 'tag-blue'
  if (s === '笔试') return 'tag-yellow'
  if (s === '面试') return 'badge-blue'
  if (s === 'Offer') return 'tag-green'
  if (s === '拒信') return 'tag-red'
  return 'tag-gray'
}
</script>

<template>
  <div class="page">
    <div class="top-bar">
      <h1>📋 投递追踪</h1>
      <button class="btn btn-sm btn-primary" @click="showNewForm=true">＋ 新增</button>
    </div>
    <div class="container">
      <!-- 状态筛选 -->
      <div class="status-tabs">
        <button :class="{active:!statusFilter}" @click="statusFilter='';page=1">全部</button>
        <button v-for="s in statuses" :key="s" :class="{active:statusFilter===s}" @click="statusFilter=s;page=1">
          {{ s }}
        </button>
      </div>

      <div v-if="loading" class="loading"><span class="spinner"></span></div>
      <div v-else-if="items.length===0" class="empty">还没有投递记录</div>

      <div v-for="a in items" :key="a.id" class="card" @click="router.push(`/applications/${a.id}`)">
        <div class="app-header">
          <div>
            <div class="app-company">{{ a.company }}</div>
            <div class="app-title">{{ a.title }}</div>
          </div>
          <span class="tag" :class="statusTag(a.status)">{{ a.status }}</span>
        </div>
        <div class="app-meta">
          <span v-if="a.location">📍 {{ a.location }}</span>
          <span v-if="a.interview_rounds?.length">🎤 {{ a.interview_rounds.length }} 轮面试</span>
          <span v-if="a.next_step">⏭ {{ a.next_step }}</span>
        </div>
        <div v-if="a.next_reminder_at" class="app-reminder">🔔 提醒：{{ a.next_reminder_at.slice(0,16) }}</div>
      </div>

      <!-- 新增模态 -->
      <div v-if="showNewForm" class="modal-overlay" @click.self="showNewForm=false">
        <div class="modal">
          <h2>新增投递</h2>
          <div class="form-group"><label>公司 *</label><input v-model="newApp.company" required></div>
          <div class="form-group"><label>岗位 *</label><input v-model="newApp.title" required></div>
          <div class="form-group"><label>地点</label><input v-model="newApp.location"></div>
          <div class="form-group">
            <label>公司类型</label>
            <select v-model="newApp.company_type">
              <option value="">请选择</option><option>大厂</option><option>外企</option><option>国央</option><option>上市</option>
            </select>
          </div>
          <div class="form-group">
            <label>岗位类别</label>
            <select v-model="newApp.job_category">
              <option value="">请选择</option><option>管培</option><option>财务分析</option><option>BP</option><option>资金</option><option>财务</option><option>会计</option>
            </select>
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="newApp.status">
              <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div style="display:flex;gap:8px;margin-top:16px">
            <button class="btn btn-primary" style="flex:1" @click="createApp">保存</button>
            <button class="btn btn-outline" style="flex:1" @click="showNewForm=false">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.status-tabs{display:flex;gap:6px;overflow-x:auto;padding:0 0 12px;-webkit-overflow-scrolling:touch}
.status-tabs button{white-space:nowrap;border:none;border-radius:20px;padding:6px 16px;font-size:13px;background:var(--gray-100);color:var(--gray-500);transition:all .15s}
.status-tabs button.active{background:var(--blue);color:#fff;font-weight:600}
.app-header{display:flex;justify-content:space-between;align-items:start;gap:8px}
.app-company{font-size:13px;color:var(--gray-500);font-weight:600}
.app-title{font-size:16px;font-weight:600;margin:2px 0}
.app-meta{display:flex;flex-wrap:wrap;gap:6px;font-size:12px;color:var(--gray-500);margin:8px 0}
.app-reminder{font-size:12px;color:#f59e0b;background:#fef3c7;padding:4px 10px;border-radius:6px;display:inline-block}
</style>
