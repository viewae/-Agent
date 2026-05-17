import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.message || err.message || 'Request failed'
    return Promise.reject(new Error(msg))
  }
)

export function sendMessage(query, sessionId, documentIds) {
  return api.post('/chat/query', {
    query,
    session_id: sessionId || null,
    document_ids: documentIds || null,
  })
}

export function getSessions() {
  return api.get('/chat/sessions')
}

export function getSessionHistory(sessionId) {
  return api.get(`/chat/sessions/${sessionId}`)
}

export function deleteSession(sessionId) {
  return api.delete(`/chat/sessions/${sessionId}`)
}

export function executeTask(instruction, documentIds) {
  return api.post('/tasks/execute', {
    instruction,
    document_ids: documentIds || null,
  })
}
