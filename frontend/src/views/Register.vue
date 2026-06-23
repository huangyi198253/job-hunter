<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(email.value, password.value, name.value)
    router.push('/profile')
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">🎯</div>
      <h1>创建账号</h1>
      <p class="auth-sub">开始你的秋招管理之旅</p>
      <div>
        <div class="form-group">
          <label>姓名</label>
          <input v-model="name" placeholder="你的名字">
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="your@email.com">
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="至少 6 位">
        </div>
        <p v-if="error" class="auth-error">{{ error }}</p>
        <button class="btn btn-primary" style="width:100%;margin-top:8px" :disabled="loading" @click="handleRegister">
          {{ loading ? '注册中...' : '注 册' }}
        </button>
      </div>
      <p class="auth-footer">已有账号？<router-link to="/login">去登录</router-link></p>
    </div>
  </div>
</template>

<style scoped>
.auth-page{min-height:100dvh;display:flex;align-items:center;justify-content:center;padding:24px;background:linear-gradient(135deg,#eff6ff,#dbeafe)}
.auth-card{background:#fff;border-radius:20px;padding:36px 28px;width:100%;max-width:380px;box-shadow:0 4px 24px rgba(37,99,235,.08);text-align:center}
.auth-logo{font-size:48px;margin-bottom:8px}
.auth-card h1{font-size:24px;font-weight:700;margin-bottom:4px}
.auth-sub{font-size:13px;color:var(--gray-400);margin-bottom:24px}
.auth-error{color:#ef4444;font-size:13px;margin-bottom:12px}
.auth-footer{font-size:13px;color:var(--gray-400);margin-top:20px}
.auth-footer a{color:var(--blue);font-weight:600}
.form-group{margin-bottom:16px;text-align:left}
.form-group label{display:block;font-size:13px;font-weight:600;color:var(--gray-500);margin-bottom:6px}
.form-group input{width:100%;border:2px solid var(--gray-200);border-radius:10px;padding:10px 14px;font-size:15px;outline:none}
.form-group input:focus{border-color:var(--blue)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;border:none;border-radius:10px;padding:10px 20px;font-size:14px;font-weight:500;cursor:pointer}
.btn-primary{background:var(--blue);color:#fff}
.btn-primary:hover{background:#1d4ed8}
</style>
