import axios, { AxiosError } from 'axios'

export const ACCESS_TOKEN_KEY = 'fitness_access_token'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  headers: {
    Accept: 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }

  return config
})

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail

    if (typeof detail === 'string') {
      return detail
    }

    if (!error.response) {
      return '无法连接后端服务，请确认 Docker 服务正在运行。'
    }
  }

  return '请求失败，请稍后重试。'
}

export default api
