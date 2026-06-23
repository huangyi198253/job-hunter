<script setup>
import { ref, onMounted } from 'vue'
import { applications as api } from '../api'

const apps = ref([])
const allFiles = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const r = await api.list({ page_size: 50 })
    apps.value = r.data.items || []
    allFiles.value = apps.value.flatMap(a =>
      (a.files || []).map(f => ({ ...f, company: a.company, title: a.title, appId: a.id }))
    )
  } catch {}
  loading.value = false
})

function fileIcon(type) {
  const m = { pdf:'📄', doc:'📝', docx:'📝', png:'🖼️', jpg:'🖼️', jpeg:'🖼️', mp3:'🎵', mp4:'🎬' }
  return m[type] || '📎'
}
</script>

<template>
  <div class="page">
    <div class="top-bar"><h1>📁 文件档案</h1></div>
    <div class="container">
      <div class="card">
        <div class="card-title">全部文件（{{ allFiles.length }}）</div>
        <div v-if="loading" class="loading"><span class="spinner"></span></div>
        <div v-else-if="allFiles.length === 0" class="empty">还没有上传过文件</div>
        <div v-for="f in allFiles" :key="f.id" class="file-row">
          <span class="file-icon">{{ fileIcon(f.file_type) }}</span>
          <div class="file-info">
            <div class="file-name">{{ f.original_name }}</div>
            <div class="file-source">{{ f.company }} — {{ f.title }}</div>
          </div>
          <span v-if="f.tags" class="tag tag-blue">{{ f.tags }}</span>
          <span class="file-size" v-if="f.file_size">{{ (f.file_size/1024).toFixed(0) }}KB</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.file-row{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--gray-100)}
.file-row:last-child{border-bottom:none}
.file-icon{font-size:24px}
.file-info{flex:1;min-width:0}
.file-name{font-size:14px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-source{font-size:12px;color:var(--gray-400)}
.file-size{font-size:12px;color:var(--gray-400);white-space:nowrap}
</style>
