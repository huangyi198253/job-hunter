<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">🎯</div>
      <h1>秋招助手</h1>
      <p class="auth-sub">求职指挥台 · 投递追踪 · AI 复盘</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="your@email.com" required>
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="••••••••" required>
        </div>
        <p v-if="error" class="auth-error">{{ error }}</p>
        <button type="submit" class="btn btn-primary" style="width:100%;margin-top:8px" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>
      <p class="auth-footer">还没有账号？<router-link to="/register">立即注册</router-link></p>
    </div>
  </div>
</template>

<style scoped>
.auth-page{min-height:100dvh;display:flex;align-items:center;justify-content:center;padding:24px;background:linear-gradient(135deg,#eff6ff,#dbeafe)}
.auth-card{background:#fff;border-radius:20px;padding:36px 28px;width:100%;max-width:380px;box-shadow:0 4px 24px rgba(37,99,235,.08);text-align:center}
.auth-logo{font-size:48px;margin-bottom:8px}
.auth-card h1{font-size:24px;font-weight:700;margin-bottom:4px}
.auth-sub{font-size:13px;color:var(--gray-400);margin-bottom:24px}
.auth-error{color:#ef4444;font-size:13px;margin-top:-8px;margin-bottom:12px}
.auth-footer{font-size:13px;color:var(--gray-400);margin-top:20px}
.auth-footer a{color:var(--blue);font-weight:600}
form{text-align:left}
</style>
