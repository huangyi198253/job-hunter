<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { applications as api } from '../api'

const route = useRoute()
const router = useRouter()
const app = ref(null)
const loading = ref(true)
const showReviewForm = ref(false)
const reviewContent = ref('')
const reviewTags = ref('')
const showInterviewForm = ref(false)
const IForm = ref({ round_number:1, round_name:'一面', interview_type:'视频面试', notes:'' })

onMounted(async () => {
  try {
    const r = await api.get(route.params.id)
    app.value = r.data
  } catch { router.push('/applications') }
  loading.value = false
})

async function updateStatus(status) {
  try {
    const r = await api.update(app.value.id, { status })
    app.value = r.data
  } catch (e) { alert(e.response?.data?.detail || '更新失败') }
}

async function addReview() {
  try {
    const r = await api.addReview(app.value.id, { content: reviewContent.value, tags: reviewTags.value || undefined })
    app.value.review_notes.unshift(r.data)
    showReviewForm.value = false
    reviewContent.value = ''
    reviewTags.value = ''
  } catch (e) { alert(e.response?.data?.detail || '添加失败') }
}

async function addInterview() {
  try {
    const r = await api.addInterview(app.value.id, IForm.value)
    app.value.interview_rounds.push(r.data)
    app.value.status = '面试'
    showInterviewForm.value = false
  } catch (e) { alert(e.response?.data?.detail || '添加失败') }
}

function handleFileUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  fd.append('tags', '')
  api.addFile(app.value.id, fd).then(r => {
    app.value.files.push(r.data)
    alert('上传成功')
  }).catch(e => alert(e.response?.data?.detail || '上传失败'))
}

const statuses = ['收藏','已投递','笔试','面试','Offer','拒信','放弃']
const interviewTypes = ['视频面试','线下面试','电话面试','AI 面试']
</script>

<template>
  <div class="page">
    <div class="top-bar">
      <button class="btn btn-sm btn-outline" @click="router.push('/applications')">← 返回</button>
      <h1>{{ app?.company || '详情' }}</h1>
    </div>
    <div class="container" v-if="!loading && app">
      <!-- 基本信息 -->
      <div class="card">
        <div class="app-company">{{ app.company }}</div>
        <div class="app-title">{{ app.title }}</div>
        <div class="app-meta">
          <span class="tag" :class="{'tag-blue':app.company_type==='大厂','tag-yellow':app.company_type==='国央','tag-green':app.company_type==='外企','tag-gray':!app.company_type}">
            {{ app.company_type || '其他' }}
          </span>
          <span class="tag tag-gray">{{ app.job_category || '未分类' }}</span>
          <span v-if="app.location">📍 {{ app.location }}</span>
        </div>
        <div class="status-bar">
          <span>当前状态：</span>
          <select :value="app.status" @change="updateStatus($event.target.value)" style="border:2px solid var(--blue);border-radius:8px;padding:4px 10px;font-size:13px;font-weight:600;background:var(--blue-light);color:var(--blue)">
            <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div v-if="app.next_step" class="next-step">⏭ 下一步：{{ app.next_step }}</div>
      </div>

      <!-- 面试轮次 -->
      <div class="card">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>🎤 面试记录</span>
          <button class="btn btn-sm btn-outline" @click="showInterviewForm=true">＋ 记录</button>
        </div>
        <div v-if="app.interview_rounds.length === 0" class="empty">暂无面试记录</div>
        <div v-for="r in app.interview_rounds" :key="r.id" class="round-item">
          <div class="round-header">
            <span class="round-name">{{ r.round_name }}</span>
            <span class="tag tag-gray">{{ r.interview_type }}</span>
            <span v-if="r.interview_date" class="round-date">{{ r.interview_date.slice(0,10) }}</span>
          </div>
          <p v-if="r.notes" class="round-notes">{{ r.notes }}</p>
        </div>
      </div>

      <!-- 文件 -->
      <div class="card">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>📁 文件 ({{ app.files.length }})</span>
          <label class="btn btn-sm btn-outline" style="cursor:pointer">
            上传
            <input type="file" hidden @change="handleFileUpload" accept=".doc,.docx,.pdf,.png,.jpg,.jpeg,.mp3,.mp4">
          </label>
        </div>
        <div v-if="app.files.length === 0" class="empty">暂无文件</div>
        <div v-for="f in app.files" :key="f.id" class="file-item">
          <span class="file-icon">{{ f.file_type==='pdf'?'📄':f.file_type==='doc'||f.file_type==='docx'?'📝':f.file_type==='png'||f.file_type==='jpg'||f.file_type==='jpeg'?'🖼️':'🎵' }}</span>
          <span class="file-name">{{ f.original_name }}</span>
          <span v-if="f.tags" class="tag tag-gray">{{ f.tags }}</span>
        </div>
      </div>

      <!-- 复盘笔记 -->
      <div class="card">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>📝 复盘笔记</span>
          <button class="btn btn-sm btn-outline" @click="showReviewForm=true">＋ 写复盘</button>
        </div>
        <div v-if="app.review_notes.length === 0" class="empty">暂无复盘</div>
        <div v-for="n in app.review_notes" :key="n.id" class="review-item">
          <p class="review-content">{{ n.content }}</p>
          <div class="review-meta">
            <span v-if="n.tags" class="tag tag-blue">{{ n.tags }}</span>
            <span class="review-date">{{ n.created_at?.slice(0,10) }}</span>
          </div>
          <div v-if="n.ai_analysis" class="ai-box">
            🤖 <strong>AI 分析</strong>
            <pre>{{ JSON.stringify(JSON.parse(n.ai_analysis), null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- 复盘模态 -->
    <div v-if="showReviewForm" class="modal-overlay" @click.self="showReviewForm=false">
      <div class="modal">
        <h2>写复盘</h2>
        <div class="form-group"><label>内容</label><textarea v-model="reviewContent" rows="5" placeholder="记录面试经历、收获、不足..."></textarea></div>
        <div class="form-group"><label>标签（逗号分隔）</label><input v-model="reviewTags" placeholder="如：技术面, 行为面, 财务分析"></div>
        <div style="display:flex;gap:8px"><button class="btn btn-primary" style="flex:1" @click="addReview">保存</button><button class="btn btn-outline" style="flex:1" @click="showReviewForm=false">取消</button></div>
      </div>
    </div>

    <!-- 面试模态 -->
    <div v-if="showInterviewForm" class="modal-overlay" @click.self="showInterviewForm=false">
      <div class="modal">
        <h2>记录面试</h2>
        <div class="form-group"><label>轮次名称</label><input v-model="IForm.round_name" placeholder="如：一面"></div>
        <div class="form-group"><label>轮次编号</label><input v-model.number="IForm.round_number" type="number" min="1"></div>
        <div class="form-group">
          <label>面试形式</label>
          <select v-model="IForm.interview_type">
            <option v-for="t in interviewTypes" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
        <div class="form-group"><label>备注</label><textarea v-model="IForm.notes" rows="3"></textarea></div>
        <div style="display:flex;gap:8px"><button class="btn btn-primary" style="flex:1" @click="addInterview">保存</button><button class="btn btn-outline" style="flex:1" @click="showInterviewForm=false">取消</button></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-company{font-size:14px;color:var(--gray-500);font-weight:600}
.app-title{font-size:20px;font-weight:700;margin:4px 0 8px}
.app-meta{display:flex;flex-wrap:wrap;gap:6px;font-size:13px;color:var(--gray-500);margin-bottom:12px}
.status-bar{display:flex;align-items:center;gap:8px;font-size:14px;color:var(--gray-500);margin-bottom:8px}
.next-step{font-size:13px;color:#f59e0b;background:#fef3c7;padding:6px 12px;border-radius:8px;display:inline-block}
.round-item{padding:10px 0;border-bottom:1px solid var(--gray-100)}
.round-item:last-child{border-bottom:none}
.round-header{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.round-name{font-weight:600;font-size:14px}
.round-date{font-size:12px;color:var(--gray-400)}
.round-notes{font-size:13px;color:var(--gray-500);margin-top:4px;line-height:1.5}
.file-item{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--gray-100);font-size:13px}
.file-item:last-child{border-bottom:none}
.file-icon{font-size:18px}
.file-name{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.review-item{padding:12px 0;border-bottom:1px solid var(--gray-100)}
.review-item:last-child{border-bottom:none}
.review-content{font-size:14px;line-height:1.6;white-space:pre-wrap}
.review-meta{display:flex;align-items:center;gap:8px;margin-top:6px;font-size:12px;color:var(--gray-400)}
.review-date{font-size:12px;color:var(--gray-400)}
.ai-box{background:#eff6ff;border-radius:8px;padding:10px;margin-top:8px;font-size:13px}
.ai-box pre{font-size:12px;margin-top:4px;overflow-x:auto}
</style>
