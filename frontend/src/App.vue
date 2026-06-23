<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const auth = useAuthStore()
const noNav = computed(() => ['Login', 'Register'].includes(route.name))
</script>

<template>
  <div class="app">
    <router-view />
    <nav v-if="auth.isLoggedIn && !noNav" class="bottom-nav">
      <router-link to="/" :class="{ active: route.path === '/' }">
        <span class="icon">📊</span>概况
      </router-link>
      <router-link to="/jobs" :class="{ active: route.path.startsWith('/jobs') }">
        <span class="icon">💼</span>岗位
      </router-link>
      <router-link to="/applications" :class="{ active: route.path.startsWith('/applications') && route.path !== '/applications/new' }">
        <span class="icon">📋</span>投递
      </router-link>
      <router-link to="/files" :class="{ active: route.path === '/files' }">
        <span class="icon">📁</span>文件
      </router-link>
      <router-link to="/profile" :class="{ active: route.path === '/profile' }">
        <span class="icon">👤</span>我的
      </router-link>
    </nav>
  </div>
</template>
