import api from './api'

export type User = {
  id: string
  email: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type TokenResponse = {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

export async function registerUser(
  email: string,
  password: string,
): Promise<User> {
  const response = await api.post<User>('/api/v1/auth/register', {
    email,
    password,
  })

  return response.data
}

export async function loginUser(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const formData = new URLSearchParams()
  formData.set('username', email)
  formData.set('password', password)

  const response = await api.post<TokenResponse>(
    '/api/v1/auth/login',
    formData,
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    },
  )

  return response.data
}
