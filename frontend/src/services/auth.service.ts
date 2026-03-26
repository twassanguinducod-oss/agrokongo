import axios from 'axios';
import type { LoginCredentials, RegisterData, User, AuthResponse } from '@/types/user';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token em cada requisição
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('@agrokongo:token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para lidar com erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('@agrokongo:user');
      localStorage.removeItem('@agrokongo:token');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    // Backend Flask espera 'telemovel' no formato correto
    const payload = {
      nome: data.nome,
      telemovel: data.telemovel.replace(/\D/g, ''), // Remove caracteres não numéricos
      tipo: data.tipo,
      senha: data.senha,
    };
    
    const response = await api.post<AuthResponse>('/auth/registro', payload);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.put<User>('/auth/perfil', data);
    return response.data;
  },
};
