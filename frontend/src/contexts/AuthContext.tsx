// frontend/src/contexts/AuthContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';
import api, { User, TokenResponse } from '@/utils/api';
import { useRouter } from 'next/navigation';

// ===========================================
// INTERFACES
// ===========================================

interface RegisterData {
  telemovel: string;
  senha: string;
  senha_confirmacao: string;
  tipo?: 'admin' | 'produtor' | 'comprador';
  first_name?: string;
  last_name?: string;
  nif?: string;
  iban?: string;
  provincia?: string;
  municipio?: string;
  email?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (telemovel: string, senha: string) => Promise<TokenResponse>;
  register: (data: RegisterData) => Promise<TokenResponse>;
  updateUser: (data: Partial<User>) => Promise<User>;
  logout: () => void;
}

// ===========================================
// CREATE CONTEXT
// ===========================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ===========================================
// AUTH PROVIDER
// ===========================================

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // ===========================================
  // INIT AUTH
  // ===========================================

  useEffect(() => {
    const initAuth = async () => {
      const token = Cookies.get('access_token');
      const storedUser = Cookies.get('user');

      if (token && storedUser) {
        try {
          const { data } = await api.get<User>('/accounts/usuarios/me/');
          setUser(data);
          Cookies.set('user', JSON.stringify(data), {
            expires: 1,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
          });
        } catch (error) {
          logout();
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, []);

  // ===========================================
  // LOGIN
  // ===========================================

  const login = async (telemovel: string, senha: string): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>('/accounts/usuarios/login/', {
      username: telemovel,
      password: senha,
    });

    Cookies.set('access_token', data.tokens.access, {
      expires: 1 / 24,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    Cookies.set('refresh_token', data.tokens.refresh, {
      expires: 1,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    Cookies.set('user', JSON.stringify(data.user), {
      expires: 1,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    setUser(data.user);

    return data;
  };

  // ===========================================
  // REGISTER (PASSO 1)
  // ===========================================

  const register = async (data: RegisterData): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/accounts/usuarios/', {
      telemovel: data.telemovel,
      senha: data.senha,
      senha_confirmacao: data.senha_confirmacao,
    });

    Cookies.set('access_token', response.data.tokens.access, {
      expires: 1 / 24,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    Cookies.set('refresh_token', response.data.tokens.refresh, {
      expires: 1,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    Cookies.set('user', JSON.stringify(response.data.user), {
      expires: 1,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    setUser(response.data.user);

    return response.data;
  };

  // ===========================================
  // UPDATE USER (PASSO 2)
  // ===========================================

  const updateUser = async (data: Partial<User>): Promise<User> => {
    const { data: updatedUser } = await api.put<User>('/accounts/usuarios/me/', data);

    setUser(updatedUser);

    Cookies.set('user', JSON.stringify(updatedUser), {
      expires: 1,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    return updatedUser;
  };

  // ===========================================
  // LOGOUT
  // ===========================================

  const logout = () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    Cookies.remove('user');
    setUser(null);
    router.push('/login');
  };

  // ===========================================
  // CONTEXT VALUE
  // ===========================================

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    updateUser,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ===========================================
// HOOK
// ===========================================

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}