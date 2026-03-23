import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.error?.message || '请求失败，请稍后重试'
    toast.error(message)
    return Promise.reject(error)
  }
)

// ==================== 健康检查 API ====================

export const fetchHealthStatus = () => {
  return api.get('/health')
}

export const fetchSimpleHealth = () => {
  return api.get('/health/simple')
}

// ==================== RAG API ====================

export const queryRAG = (question: string, topK: number = 5) => {
  return api.post('/rag/query', {
    question,
    top_k: topK,
  })
}

export const addDocuments = (documents: Array<{ content: string; metadata?: object }>) => {
  return api.post('/rag/documents', { documents })
}

// ==================== 文档解析 API ====================

export const parseDocument = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post(`${API_BASE_URL}/docs/parse`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const parseDocumentFromUrl = (url: string) => {
  return api.post('/docs/parse', { url })
}

// ==================== 网页抓取 API ====================

export const scrapeWebpage = (url: string, selector?: string, extractLinks?: boolean) => {
  return api.post('/web/scrape', {
    url,
    selector,
    extract_links: extractLinks,
  })
}

// ==================== 聊天 API ====================

export const sendChatMessage = (message: string, sessionId?: string, context?: object) => {
  return api.post('/chat', {
    message,
    session_id: sessionId,
    context,
  })
}

export default api
