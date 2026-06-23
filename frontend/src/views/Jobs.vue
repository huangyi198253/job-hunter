<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { jobs as jobsApi, applications as appApi } from '../api'

const router = useRouter()
const items = ref([])
const total = ref(0)
const page = ref(1)
const keyword = ref('')
const companyType = ref('')
const jobCategory = ref('')
const loading = ref(false)
const showFilter = ref(false)

async function load() {
  loading.value = true
  try {
    const r = await jobsApi.list({
      keyword: keyword.value || undefined,
      company_type: companyType.value || undefined,
      job_category: jobCategory.value || undefined,
      page: page.value,
      page_size: 20,
    })
    items.value = r.data.items
    total.value = r.data.total
  } catch {}
  loading.value = false
}

onMounted(load)
watch([page, companyType, jobCategory], load)

function search() {
  page.value = 1
  load()
}

async function quickApply(job) {
  const confirmed = confirm(`投递 ${job.company} - ${job.title}？`)
  if (!confirmed) return
  try {
    await appApi.create({
      job_id: job.id,
      company: job.company,
      title: job.title,
      location: job.location,
      company_type: job.company_type,
      job_category: job.job_category,
      status: '已投递',
    })
    alert('已记录投递！')
    load()
  } catch (e) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

async function quickSave(job) {
  try {
    await appApi.create({
      job_id: job.id,
      company: job.company,
      title: job.title,
      location: job.location,
      company_type: job.company_type,
      job_category: job.job_category,
      status: '收藏',
    })
    alert('已收藏')
  } catch (e) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

const typeOptions = ['大厂','外企','国央','上市']
const catOptions = ['管培','财务分析','BP','资金','财务','会计']
</script>

<template>
  <div class="page">
    <div class="top-bar">
      <h1>💼 岗位库</h1>
      <button class="btn btn-sm btn-outline" @click="showFilter=!showFilter">
        {{ showFilter ? '收起' : '筛选' }}
      </button>
    </div>
    <div class="container">
      <!-- 搜索条 -->
      <div class="search-bar">
        <input v-model="keyword" placeholder="搜索公司/岗位/关键词" @keyup.enter="search">
        <button class="btn btn-sm btn-primary" @click="search">搜索</button>
      </div>

      <!-- 筛选项 -->
      <div v-if="showFilter" class="filter-bar">
        <select v-model="companyType">
          <option value="">公司类型</option>
          <option v-for="t in typeOptions" :key="t" :value="t">{{ t }}</option>
        </select>
        <select v-model="jobCategory">
          <option value="">岗位类别</option>
          <option v-for="c in catOptions" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <!-- 列表 -->
      <div v-if="loading" class="loading"><span class="spinner"></span></div>
      <div v-else-if="items.length === 0" class="empty">暂无匹配岗位</div>

      <div v-for="j in items" :key="j.id" class="card" style="padding:14px 16px">
        <div class="job-header">
          <div>
            <div class="job-company">{{ j.company }}</div>
            <div class="job-title">{{ j.title }}</div>
          </div>
          <span class="tag" :class="{'tag-blue':j.company_type==='大厂','tag-yellow':j.company_type==='国央','tag-green':j.company_type==='外企','tag-gray':!j.company_type}">
            {{ j.company_type || '其他' }}
          </span>
        </div>
        <div class="job-meta">
          <span>📍 {{ j.location || '不限' }}</span>
          <span v-if="j.deadline">⏰ {{ j.deadline }}</span>
          <span v-if="j.job_category" class="tag tag-gray">{{ j.job_category }}</span>
          <span class="tag tag-green" v-if="j.is_active">活跃</span>
          <span class="tag tag-red" v-else>可能已下线</span>
        </div>
        <div class="job-actions">
          <button class="btn btn-sm btn-primary" @click="quickApply(j)">投递</button>
          <button class="btn btn-sm btn-outline" @click="quickSave(j)">收藏</button>
          <a v-if="j.url" :href="j.url" target="_blank" class="btn btn-sm btn-outline">查看原文</a>
        </div>
      </div>

      <div v-if="total > 20" class="pagination">
        <button :disabled="page===1" @click="page--" class="btn btn-sm btn-outline">上一页</button>
        <span>{{ page }} / {{ Math.ceil(total/20) }}</span>
        <button :disabled="page>=Math.ceil(total/20)" @click="page++" class="btn btn-sm btn-outline">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-bar{display:flex;gap:8px;margin-bottom:12px}
.search-bar input{flex:1;border:2px solid var(--gray-200);border-radius:10px;padding:10px 14px;font-size:15px;outline:none}
.search-bar input:focus{border-color:var(--blue)}
.filter-bar{display:flex;gap:8px;margin-bottom:12px}
.filter-bar select{flex:1;border:2px solid var(--gray-200);border-radius:10px;padding:8px 12px;font-size:13px;outline:none;background:#fff}
.job-header{display:flex;justify-content:space-between;align-items:start;gap:8px}
.job-company{font-size:13px;color:var(--gray-500);font-weight:600}
.job-title{font-size:16px;font-weight:600;margin:2px 0}
.job-meta{display:flex;flex-wrap:wrap;gap:6px;font-size:12px;color:var(--gray-500);margin:8px 0}
.job-actions{display:flex;gap:6px;margin-top:8px;padding-top:8px;border-top:1px solid var(--gray-100)}
.pagination{display:flex;align-items:center;justify-content:center;gap:12px;padding:16px 0;font-size:13px;color:var(--gray-400)}
</style>
