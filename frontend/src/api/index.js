import api from './client'

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login:    (data) => api.post('/auth/login',    data),
  refresh:  (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  logout:   () => api.post('/auth/logout'),
  me:       () => api.get('/auth/me'),
}

export const uploadApi = {
  upload:  (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  list:    () => api.get('/upload'),
  remove:  (docId) => api.delete(`/upload/${docId}`),
}

export const queryApi = {
  ask:     (payload) => api.post('/query', payload),
}

export const historyApi = {
  sessions: () => api.get('/history/sessions'),
  session:  (id) => api.get(`/history/sessions/${id}`),
  deleteSession: (id) => api.delete(`/history/sessions/${id}`),
}

export const analyticsApi = {
  dashboard: () => api.get('/analytics/dashboard'),
  reset: () => api.delete('/analytics/reset'),
}

export const voiceApi = {
  transcribe: (audioBlob) => {
    const form = new FormData();
    form.append('file', audioBlob, 'recording.webm');
    return api.post('/voice/transcribe', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  },
  synthesize: (text) => {
    return api.post('/voice/synthesize', { text }, { responseType: 'blob' });
  }
}
