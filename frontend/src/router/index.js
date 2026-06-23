import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { noAuth: true } },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue'), meta: { noAuth: true } },
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/jobs', name: 'Jobs', component: () => import('../views/Jobs.vue') },
  { path: '/applications', name: 'Applications', component: () => import('../views/Applications.vue') },
  { path: '/applications/:id', name: 'ApplicationDetail', component: () => import('../views/ApplicationDetail.vue'), props: true },
  { path: '/files', name: 'Files', component: () => import('../views/Files.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue') },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.noAuth && !token) next('/login')
  else next()
})

export default router
