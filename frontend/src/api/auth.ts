import api from './index'

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
}

export interface User {
  id: number
  username: string
  email: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  login: (data: LoginForm) => {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    return api.post<TokenResponse>('/auth/login', formData)
  },

  register: (data: RegisterForm) => {
    return api.post<User>('/auth/register', data)
  },

  getCurrentUser: () => {
    return api.get<User>('/auth/me')
  }
}
