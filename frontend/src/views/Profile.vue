<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { profileApi as api } from '../api'

const router = useRouter()
const auth = useAuthStore()
const profile = ref({})
const loading = ref(true)
const saving = ref(false)
const activeTab = ref('basic')

// Resume files
const resumes = ref([])
const newResumeFile = ref(null)
const newResumeCategory = ref('resume')
const renameTarget = ref(null)
const renameName = ref('')

// Entries
const honorEntries = ref([])
const qualEntries = ref([])
const internEntries = ref([])
const campusEntries = ref([])

// File upload states
const pendingUploads = ref({})  // { 'entryType-entryId': File }
const transcriptUpload = reactive({ undergrad: null, grad: null })

onMounted(async () => {
  try {
    const r = await api.get()
    profile.value = r.data
    loadResumes()
    loadEntries()
  } catch {}
  loading.value = false
})

async function loadResumes() {
  try {
    const r = await api.get('/resumes')
    resumes.value = r.data || []
  } catch {}
}

async function loadEntries() {
  try {
    const r = await api.get('/entries')
    const items = r.data || []
    honorEntries.value = items.filter(e => e.category === 'honor')
    qualEntries.value = items.filter(e => e.category === 'qual')
    internEntries.value = items.filter(e => e.category === 'internship')
    campusEntries.value = items.filter(e => e.category === 'campus')
  } catch {}
}

// ===== Resume/Self-intro =====
function pickResumeFile() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.pdf,.doc,.docx,.png,.jpg'
  input.onchange = () => {
    newResumeFile.value = input.files[0]
    confirmUploadResume()
  }
  input.click()
}

async function confirmUploadResume() {
  if (!newResumeFile.value) return
  const fd = new FormData()
  fd.append('file', newResumeFile.value)
  fd.append('category', newResumeCategory.value)
  try {
    const r = await api.post('/resumes', fd)
    resumes.value.push(r.data)
    newResumeFile.value = null
    alert('上传成功')
  } catch (e) { alert(e.response?.data?.detail || '上传失败') }
}

async function deleteResume(id) {
  if (!confirm('确定删除此文件？')) return
  try {
    await api.delete(`/resumes/${id}`)
    resumes.value = resumes.value.filter(r => r.id !== id)
  } catch (e) { alert('删除失败') }
}

function startRename(r) {
  renameTarget.value = r
  renameName.value = r.original_name
}
async function confirmRename() {
  try {
    await api.put(`/resumes/${renameTarget.value.id}/rename?name=${encodeURIComponent(renameName.value)}`)
    renameTarget.value.original_name = renameName.value
    renameTarget.value = null
  } catch (e) { alert('重命名失败') }
}

// ===== Form save =====
async function saveProfile() {
  saving.value = true
  try {
    const r = await api.update('/profile/', profile.value)
    profile.value = r.data
    alert('保存成功')
  } catch (e) { alert(e.response?.data?.detail || '保存失败') }
  saving.value = false
}

// ===== Entries =====
const entryForms = reactive({
  honor: { show: false, data: {}, editId: null },
  qual: { show: false, data: {}, editId: null },
  internship: { show: false, data: {}, editId: null },
  campus: { show: false, data: {}, editId: null },
})

const entryFields = {
  honor: [
    { key: 'name', label: '名称', type: 'text' },
    { key: 'date', label: '获奖时间', type: 'text' },
    { key: 'level', label: '获奖等级', type: 'text' },
    { key: 'desc', label: '描述', type: 'textarea' },
  ],
  qual: [
    { key: 'name', label: '证书名称', type: 'text' },
    { key: 'date', label: '获得时间', type: 'text' },
    { key: 'level', label: '等级', type: 'text' },
    { key: 'desc', label: '描述', type: 'textarea' },
  ],
  internship: [
    { key: 'company', label: '公司名称', type: 'text' },
    { key: 'company_type', label: '公司类型', type: 'text' },
    { key: 'period', label: '实习时间', type: 'text' },
    { key: 'desc', label: '描述', type: 'textarea' },
  ],
  campus: [
    { key: 'name', label: '活动/组织名称', type: 'text' },
    { key: 'period', label: '时间', type: 'text' },
    { key: 'desc', label: '描述', type: 'textarea' },
  ],
}

function openEntryForm(type, entry = null) {
  entryForms[type].show = true
  entryForms[type].data = entry ? { ...entry.data } : {}
  entryForms[type].editId = entry ? entry.id : null
}

async function saveEntry(type) {
  const form = entryForms[type]
  try {
    if (form.editId) {
      const r = await api.put(`/entries/${form.editId}`, { data: form.data })
      const list = getEntryList(type)
      const idx = list.value.findIndex(e => e.id === form.editId)
      if (idx >= 0) list.value[idx] = r.data
    } else {
      const r = await api.post('/entries', { category: type, data: form.data })
      getEntryList(type).value.push(r.data)
    }
    form.show = false
  } catch (e) { alert(e.response?.data?.detail || '保存失败') }
}

async function deleteEntry(type, id) {
  if (!confirm('确定删除？')) return
  try {
    await api.delete(`/entries/${id}`)
    getEntryList(type).value = getEntryList(type).value.filter(e => e.id !== id)
  } catch (e) { alert('删除失败') }
}

function getEntryList(type) {
  const map = { honor: honorEntries, qual: qualEntries, internship: internEntries, campus: campusEntries }
  return map[type]
}

// ===== File upload with confirm =====
function pickEntryFile(type, entryId) {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.pdf,.doc,.docx,.png,.jpg,.jpeg,.mp3,.mp4'
  input.onchange = () => {
    pendingUploads.value[`${type}-${entryId}`] = input.files[0]
  }
  input.click()
}

async function confirmEntryFile(type, entryId) {
  const key = `${type}-${entryId}`
  const file = pendingUploads.value[key]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const r = await api.post(`/entries/${entryId}/files`, fd)
    const entry = getEntryList(type).value.find(e => e.id === entryId)
    if (entry) { if (!entry.files) entry.files = []; entry.files.push(r.data) }
    delete pendingUploads.value[key]
    alert('上传成功')
  } catch (e) { alert(e.response?.data?.detail || '上传失败') }
}

async function deleteEntryFile(type, entryId, fileId) {
  if (!confirm('确定删除此文件？')) return
  try {
    await api.delete(`/entries/files/${fileId}`)
    const entry = getEntryList(type).value.find(e => e.id === entryId)
    if (entry) entry.files = entry.files.filter(f => f.id !== fileId)
  } catch {}
}

// ===== Transcript / ID photo =====
function pickFile(field) {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.pdf,.doc,.docx,.png,.jpg,.jpeg'
  input.onchange = () => { transcriptUpload[field] = input.files[0] }
  input.click()
}
async function confirmTranscript(level) {
  const file = transcriptUpload[level]
  if (!file) return
  const fd = new FormData(); fd.append('file', file)
  try {
    const r = await api.post(`/transcript/${level}`, fd)
    profile.value = r.data
    transcriptUpload[level] = null
    alert('上传成功')
  } catch (e) { alert('上传失败') }
}

function pickIdPhoto() {
  const input = document.createElement('input')
  input.type = 'file'; input.accept = '.png,.jpg,.jpeg,.gif,.webp'
  input.onchange = async () => {
    const fd = new FormData(); fd.append('file', input.files[0])
    try {
      const r = await api.post('/idphoto', fd)
      profile.value = r.data
      alert('上传成功')
    } catch (e) { alert('上传失败') }
  }
  input.click()
}

function btnClass(active) { return active ? 'tab tab-active' : 'tab' }
</script>

<template>
  <div class="page">
    <div class="top-bar">
      <h1>👤 个人档案</h1>
      <button class="btn btn-sm btn-primary" @click="saveProfile" :disabled="saving">
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </div>
    <div class="container">

      <!-- 第一区域：简历 & 自我介绍 -->
      <div class="card">
        <div class="card-title">📄 简历 & 自我介绍</div>
        <div class="resume-toolbar">
          <select v-model="newResumeCategory" class="mini-select">
            <option value="resume">简历</option>
            <option value="self_intro">自我介绍</option>
          </select>
          <button class="btn btn-sm btn-primary" @click="pickResumeFile">选择文件</button>
          <span v-if="newResumeFile" class="pending-file">已选择: {{ newResumeFile.name }} <button class="btn btn-sm btn-primary" @click="confirmUploadResume">确定上传</button></span>
        </div>
        <div v-if="resumes.length === 0" class="empty">暂无文件</div>
        <div v-for="r in resumes" :key="r.id" class="file-row">
          <span class="file-icon">{{ r.category === 'resume' ? '📄' : '🎙️' }}</span>
          <div class="file-info">
            <div class="file-name">
              <template v-if="renameTarget?.id === r.id">
                <input v-model="renameName" class="inline-input" @keyup.enter="confirmRename">
                <button class="btn btn-sm btn-primary" @click="confirmRename">确定</button>
                <button class="btn btn-sm btn-outline" @click="renameTarget=null">取消</button>
              </template>
              <template v-else>
                {{ r.original_name }}
                <span class="file-tag">{{ r.category === 'resume' ? '简历' : '自我介绍' }}</span>
              </template>
            </div>
          </div>
          <div class="file-actions">
            <button v-if="renameTarget?.id !== r.id" class="btn btn-sm btn-outline" @click="startRename(r)">重命名</button>
            <button class="btn btn-sm btn-danger" @click="deleteResume(r.id)">删除</button>
          </div>
        </div>
      </div>

      <!-- 第二区域：基础资料 -->
      <div class="card">
        <div class="tabs">
          <button :class="btnClass(activeTab==='basic')" @click="activeTab='basic'">基础信息</button>
          <button :class="btnClass(activeTab==='education')" @click="activeTab='education'">教育背景</button>
          <button :class="btnClass(activeTab==='honor')" @click="activeTab='honor'">荣誉证书</button>
          <button :class="btnClass(activeTab==='qual')" @click="activeTab='qual'">资格/能力</button>
          <button :class="btnClass(activeTab==='internship')" @click="activeTab='internship'">实习经历</button>
          <button :class="btnClass(activeTab==='campus')" @click="activeTab='campus'">校园经历</button>
          <button :class="btnClass(activeTab==='photo')" @click="activeTab='photo'">证件照</button>
        </div>
      </div>

      <!-- 基础信息 -->
      <div class="card" v-if="activeTab === 'basic'">
        <div class="card-title">基础信息</div>
        <div class="form-row"><div class="form-group"><label>姓名</label><input v-model="profile.name"></div><div class="form-group"><label>手机号</label><input v-model="profile.phone"></div></div>
        <div class="form-row"><div class="form-group"><label>邮箱</label><input v-model="profile.email"></div><div class="form-group"><label>性别</label><input v-model="profile.gender" placeholder="男/女"></div></div>
        <div class="form-row"><div class="form-group"><label>政治面貌</label><input v-model="profile.political_status" placeholder="中共党员/共青团员/群众"></div><div class="form-group"><label>常住地</label><input v-model="profile.residence"></div></div>
        <div class="form-group"><label>家庭通讯地址</label><input v-model="profile.home_address"></div>
        <div class="form-row"><div class="form-group"><label>籍贯</label><input v-model="profile.birthplace"></div><div class="form-group"><label>联系人1</label><input v-model="profile.contact1_name"></div></div>
        <div class="form-row"><div class="form-group"><label>联系人1 电话</label><input v-model="profile.contact1_phone"></div><div class="form-group"><label>联系人2</label><input v-model="profile.contact2_name"></div></div>
        <div class="form-row"><div class="form-group"><label>联系人2 电话</label><input v-model="profile.contact2_phone"></div><div class="form-group"></div></div>
      </div>

      <!-- 教育背景 -->
      <div class="card" v-if="activeTab === 'education'">
        <div class="card-title">本科阶段</div>
        <div class="form-row">
          <div class="form-group"><label>学校名称</label><input v-model="profile.undergrad_school"></div>
          <div class="form-group"><label>学院</label><input v-model="profile.undergrad_college"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>专业</label><input v-model="profile.undergrad_major"></div>
          <div class="form-group"><label>时间段</label><input v-model="profile.undergrad_period" placeholder="2021-2025"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>绩点</label><input v-model="profile.undergrad_gpa"></div>
          <div class="form-group"><label>绩点排名</label><input v-model="profile.undergrad_gpa_rank" placeholder="3/120"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>综合成绩</label><input v-model="profile.undergrad_overall_score"></div>
          <div class="form-group"><label>综合排名</label><input v-model="profile.undergrad_overall_rank"></div>
        </div>
        <div class="form-group">
          <label>成绩单证明</label>
          <div class="file-upload-bar">
            <span v-if="profile.undergrad_transcript" class="file-tag">已上传: {{ profile.undergrad_transcript.original_name || '文件' }}</span>
            <button class="btn btn-sm btn-outline" @click="pickFile('undergrad')">选择文件</button>
            <span v-if="transcriptUpload.undergrad" class="pending-file">已选: {{ transcriptUpload.undergrad.name }} <button class="btn btn-sm btn-primary" @click="confirmTranscript('undergrad')">确定上传</button></span>
          </div>
        </div>

        <div class="card-title" style="margin-top:16px">研究生阶段</div>
        <div class="form-row">
          <div class="form-group"><label>学校名称</label><input v-model="profile.grad_school"></div>
          <div class="form-group"><label>学院</label><input v-model="profile.grad_college"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>专业</label><input v-model="profile.grad_major"></div>
          <div class="form-group"><label>时间段</label><input v-model="profile.grad_period" placeholder="2025-2027"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>绩点</label><input v-model="profile.grad_gpa"></div>
          <div class="form-group"><label>绩点排名</label><input v-model="profile.grad_gpa_rank"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>综合成绩</label><input v-model="profile.grad_overall_score"></div>
          <div class="form-group"><label>综合排名</label><input v-model="profile.grad_overall_rank"></div>
        </div>
        <div class="form-group">
          <label>成绩单证明</label>
          <div class="file-upload-bar">
            <span v-if="profile.grad_transcript" class="file-tag">已上传: {{ profile.grad_transcript.original_name || '文件' }}</span>
            <button class="btn btn-sm btn-outline" @click="pickFile('grad')">选择文件</button>
            <span v-if="transcriptUpload.grad" class="pending-file">已选: {{ transcriptUpload.grad.name }} <button class="btn btn-sm btn-primary" @click="confirmTranscript('grad')">确定上传</button></span>
          </div>
        </div>
      </div>

      <!-- 荣誉证书 -->
      <div class="card" v-if="activeTab === 'honor'">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>🏆 荣誉证书</span>
          <button class="btn btn-sm btn-primary" @click="openEntryForm('honor')">＋ 添加</button>
        </div>
        <div v-if="honorEntries.length === 0" class="empty">暂无记录</div>
        <div v-for="e in honorEntries" :key="e.id" class="entry-card">
          <div class="entry-header">
            <strong>{{ e.data.name }}</strong>
            <div class="entry-actions">
              <button class="btn btn-sm btn-outline" @click="openEntryForm('honor', e)">编辑</button>
              <button class="btn btn-sm btn-danger" @click="deleteEntry('honor', e.id)">删除</button>
            </div>
          </div>
          <div class="entry-meta">{{ e.data.date }} · {{ e.data.level }}</div>
          <p v-if="e.data.desc" class="entry-desc">{{ e.data.desc }}</p>
          <div class="entry-files">
            <span v-for="f in (e.files||[])" :key="f.id" class="file-tag">
              {{ f.original_name }}
              <button class="btn btn-sm btn-danger" @click="deleteEntryFile('honor', e.id, f.id)">✕</button>
            </span>
            <button v-if="pendingUploads['honor-'+e.id]" class="btn btn-sm btn-primary" @click="confirmEntryFile('honor', e.id)">确定上传</button>
            <button class="btn btn-sm btn-outline" @click="pickEntryFile('honor', e.id)">+ 附件</button>
          </div>
        </div>
      </div>

      <!-- 资格/能力证书 -->
      <div class="card" v-if="activeTab === 'qual'">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>📜 资格/能力证书</span>
          <button class="btn btn-sm btn-primary" @click="openEntryForm('qual')">＋ 添加</button>
        </div>
        <div v-if="qualEntries.length === 0" class="empty">暂无记录</div>
        <div v-for="e in qualEntries" :key="e.id" class="entry-card">
          <div class="entry-header">
            <strong>{{ e.data.name }}</strong>
            <div class="entry-actions">
              <button class="btn btn-sm btn-outline" @click="openEntryForm('qual', e)">编辑</button>
              <button class="btn btn-sm btn-danger" @click="deleteEntry('qual', e.id)">删除</button>
            </div>
          </div>
          <div class="entry-meta">{{ e.data.date }} · {{ e.data.level }}</div>
          <p v-if="e.data.desc" class="entry-desc">{{ e.data.desc }}</p>
          <div class="entry-files">
            <span v-for="f in (e.files||[])" :key="f.id" class="file-tag">{{ f.original_name }} <button class="btn btn-sm btn-danger" @click="deleteEntryFile('qual', e.id, f.id)">✕</button></span>
            <button v-if="pendingUploads['qual-'+e.id]" class="btn btn-sm btn-primary" @click="confirmEntryFile('qual', e.id)">确定上传</button>
            <button class="btn btn-sm btn-outline" @click="pickEntryFile('qual', e.id)">+ 附件</button>
          </div>
        </div>
      </div>

      <!-- 实习经历 -->
      <div class="card" v-if="activeTab === 'internship'">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>💼 实习经历</span>
          <button class="btn btn-sm btn-primary" @click="openEntryForm('internship')">＋ 添加</button>
        </div>
        <div v-if="internEntries.length === 0" class="empty">暂无记录</div>
        <div v-for="e in internEntries" :key="e.id" class="entry-card">
          <div class="entry-header">
            <strong>{{ e.data.company }}</strong>
            <div class="entry-actions">
              <button class="btn btn-sm btn-outline" @click="openEntryForm('internship', e)">编辑</button>
              <button class="btn btn-sm btn-danger" @click="deleteEntry('internship', e.id)">删除</button>
            </div>
          </div>
          <div class="entry-meta">{{ e.data.company_type }} · {{ e.data.period }}</div>
          <p v-if="e.data.desc" class="entry-desc">{{ e.data.desc }}</p>
          <div class="entry-files">
            <span v-for="f in (e.files||[])" :key="f.id" class="file-tag">{{ f.original_name }} <button class="btn btn-sm btn-danger" @click="deleteEntryFile('internship', e.id, f.id)">✕</button></span>
            <button v-if="pendingUploads['internship-'+e.id]" class="btn btn-sm btn-primary" @click="confirmEntryFile('internship', e.id)">确定上传</button>
            <button class="btn btn-sm btn-outline" @click="pickEntryFile('internship', e.id)">+ 附件</button>
          </div>
        </div>
      </div>

      <!-- 校园经历 -->
      <div class="card" v-if="activeTab === 'campus'">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>🎓 校园经历</span>
          <button class="btn btn-sm btn-primary" @click="openEntryForm('campus')">＋ 添加</button>
        </div>
        <div v-if="campusEntries.length === 0" class="empty">暂无记录</div>
        <div v-for="e in campusEntries" :key="e.id" class="entry-card">
          <div class="entry-header">
            <strong>{{ e.data.name }}</strong>
            <div class="entry-actions">
              <button class="btn btn-sm btn-outline" @click="openEntryForm('campus', e)">编辑</button>
              <button class="btn btn-sm btn-danger" @click="deleteEntry('campus', e.id)">删除</button>
            </div>
          </div>
          <div class="entry-meta">{{ e.data.period }}</div>
          <p v-if="e.data.desc" class="entry-desc">{{ e.data.desc }}</p>
          <div class="entry-files">
            <span v-for="f in (e.files||[])" :key="f.id" class="file-tag">{{ f.original_name }} <button class="btn btn-sm btn-danger" @click="deleteEntryFile('campus', e.id, f.id)">✕</button></span>
            <button v-if="pendingUploads['campus-'+e.id]" class="btn btn-sm btn-primary" @click="confirmEntryFile('campus', e.id)">确定上传</button>
            <button class="btn btn-sm btn-outline" @click="pickEntryFile('campus', e.id)">+ 附件</button>
          </div>
        </div>
      </div>

      <!-- 证件照 -->
      <div class="card" v-if="activeTab === 'photo'">
        <div class="card-title">证件照</div>
        <div class="photo-area">
          <div v-if="profile.id_photo" class="photo-preview">
            <img :src="'data:image/jpeg;base64,'" alt="证件照" style="display:none">
            <div class="photo-placeholder">📷</div>
            <p>已上传: {{ profile.id_photo.original_name }}</p>
          </div>
          <button class="btn btn-outline" @click="pickIdPhoto">选择证件照上传</button>
        </div>
      </div>

      <!-- ===== Entry Modal ===== -->
      <div v-for="(form, type) in entryForms" :key="type">
        <div v-if="form.show" class="modal-overlay" @click.self="form.show=false">
          <div class="modal">
            <h2>{{ form.editId ? '编辑' : '添加' }} {{ {honor:'荣誉证书',qual:'资格/能力证书',internship:'实习经历',campus:'校园经历'}[type] }}</h2>
            <div v-for="f in entryFields[type]" :key="f.key" class="form-group">
              <label>{{ f.label }}</label>
              <input v-if="f.type==='text'" v-model="form.data[f.key]" :placeholder="f.label">
              <textarea v-else v-model="form.data[f.key]" rows="3" :placeholder="f.label"></textarea>
            </div>
            <div style="display:flex;gap:8px;margin-top:12px">
              <button class="btn btn-primary" style="flex:1" @click="saveEntry(type)">保存</button>
              <button class="btn btn-outline" style="flex:1" @click="form.show=false">取消</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.tabs{display:flex;gap:4px;overflow-x:auto;padding:4px 0;-webkit-overflow-scrolling:touch}
.tab{white-space:nowrap;border:none;border-radius:20px;padding:6px 14px;font-size:12px;background:var(--gray-100);color:var(--gray-500)}
.tab-active{background:var(--blue);color:#fff;font-weight:600}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.form-row .form-group{margin-bottom:8px}
.resume-toolbar{display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.mini-select{border:2px solid var(--gray-200);border-radius:8px;padding:6px 10px;font-size:13px;background:#fff}
.pending-file{font-size:12px;color:var(--blue);display:flex;align-items:center;gap:6px}
.file-row{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--gray-100)}
.file-row:last-child{border-bottom:none}
.file-icon{font-size:20px}
.file-info{flex:1;min-width:0}
.file-name{font-size:14px;font-weight:500;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.file-tag{font-size:11px;background:var(--gray-100);color:var(--gray-500);padding:2px 8px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.file-actions{display:flex;gap:4px}
.file-upload-bar{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.inline-input{border:2px solid var(--blue);border-radius:6px;padding:4px 8px;font-size:13px;width:200px}
.entry-card{padding:12px;background:var(--gray-50);border-radius:10px;margin-bottom:8px}
.entry-header{display:flex;justify-content:space-between;align-items:start;gap:8px}
.entry-meta{font-size:12px;color:var(--gray-400);margin:4px 0}
.entry-desc{font-size:13px;color:var(--gray-500);line-height:1.5;white-space:pre-wrap}
.entry-files{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;align-items:center}
.entry-actions{display:flex;gap:4px}
.photo-area{text-align:center;padding:20px}
.photo-placeholder{font-size:64px;margin-bottom:8px}
</style>
