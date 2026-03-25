import { User as UserType } from '@/services/auth.service';

export interface User extends UserType {
  foto_perfil?: string;
  notificacoes?: Notificacao[];
  notificacoes_nao_lidas?: number;
}

export interface Notificacao {
  id: string;
  mensagem: string;
  data: string;
  lida: boolean;
  link?: string;
}

export type UserRole = 'admin' | 'produtor' | 'comprador';

export type NavItem = {
  href: string;
  label: string;
  icon: string;
  roles: UserRole[] | ['all'];
};
