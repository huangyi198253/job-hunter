import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.hash = '#/login'
    }
    return Promise.reject(err)
  }
)

export default api

export const auth = {
  register: data => api.post('/auth/register', data),
  login: data => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

export const jobs = {
  list: params => api.get('/jobs/', { params }),
  get: id => api.get(`/jobs/${id}`),
  create: data => api.post('/jobs/', data),
  delete: id => api.delete(`/jobs/${id}`),
}

export const applications = {
  stats: () => api.get('/applications/stats'),
  list: params => api.get('/applications/', { params }),
  get: id => api.get(`/applications/${id}`),
  create: data => api.post('/applications/', data),
  update: (id, data) => api.put(`/applications/${id}`, data),
  delete: id => api.delete(`/applications/${id}`),
  addInterview: (id, data) => api.post(`/applications/${id}/interviews`, data),
  addFile: (id, formData) => api.post(`/applications/${id}/files`, formData),
  addReview: (id, data) => api.post(`/applications/${id}/reviews`, data),
  getReviews: id => api.get(`/applications/${id}/reviews`),
}

function profileReq(method, path, data) {
  if (path && !path.startsWith('/')) path = '/' + path
  return api[method](`/profile${path || '/'}`, data)
}

export const profileApi = {
  get: (path) => profileReq('get', path),
  post: (path, data) => profileReq('post', path, data),
  put: (path, data) => profileReq('put', path, data),
  delete: (path) => profileReq('delete', path),
  fetch: () => profileReq('get', ''),
  update: (path, data) => {
    if (data === undefined) { data = path; path = '' }
    return profileReq('put', path, data)
  },
}
