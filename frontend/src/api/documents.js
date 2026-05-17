import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.message || err.message || 'Request failed'
    return Promise.reject(new Error(msg))
  }
)

export function uploadDocument(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function listDocuments(page = 1, pageSize = 20) {
  return api.get('/documents/list', { params: { page, page_size: pageSize } })
}

export function getDocumentContent(id) {
  return api.get(`/documents/${id}/content`)
}

export function deleteDocument(id) {
  return api.delete(`/documents/${id}`)
}
