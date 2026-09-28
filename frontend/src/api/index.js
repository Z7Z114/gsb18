import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const templeApi = {
  getTemples: () => api.get('/temples'),
  getTemple: (id) => api.get(`/temples/${id}`),
  createTemple: (data) => api.post('/temples', data),
  getHalls: (templeId) => api.get(`/temples/${templeId}/halls`),
  createHall: (templeId, data) => api.post(`/temples/${templeId}/halls`, data),
  getHall: (id) => api.get(`/temples/halls/${id}`),
  updateHall: (id, data) => api.put(`/temples/halls/${id}`, data)
}

export const meetingApi = {
  getMeetings: (hallId) => api.get('/meetings', { params: { hall_id: hallId } }),
  getMeeting: (id) => api.get(`/meetings/${id}`),
  createMeeting: (data) => api.post('/meetings', data),
  uploadAudio: (meetingId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/meetings/${meetingId}/upload-audio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  processMeeting: (meetingId) => api.post(`/meetings/${meetingId}/process`),
  getDialogue: (meetingId) => api.get(`/meetings/${meetingId}/dialogue`),
  downloadMarkdown: (meetingId) => api.get(`/meetings/${meetingId}/download-markdown`, {
    responseType: 'blob'
  }),
  sendEmails: (meetingId, data) => api.post(`/meetings/${meetingId}/send-emails`, data)
}

export const donorApi = {
  getDonors: () => api.get('/donors'),
  createDonor: (data) => api.post('/donors', data),
  getDonor: (id) => api.get(`/donors/${id}`)
}

export default api
