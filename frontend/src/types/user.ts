export interface User {
  id: number;
  nome: string;
  email: string | null;
  telemovel: string;
  tipo: 'admin' | 'produtor' | 'comprador';
  nif: string | null;
  iban: string | null;
  perfil_completo: boolean;
  conta_validada: boolean;
  saldo_disponivel: number;
  rating_vendedor: number;
  foto_perfil: string;
}

export interface LoginCredentials {
  telemovel: string;
  senha: string;
}

export interface RegisterData {
  nome: string;
  telemovel: string;
  email?: string;
  senha: string;
  tipo: 'admin' | 'produtor' | 'comprador';
  nif?: string;
  provincia_id?: number;
  municipio_id?: number;
}

export interface AuthResponse {
  user: User;
  token: string;
}
