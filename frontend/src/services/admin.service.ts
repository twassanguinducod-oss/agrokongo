/**
 * Serviço de API do Administrador
 * Centraliza todas as chamadas relacionadas a operações administrativas
 */

import { apiPost, apiGet, ApiResponse } from '../lib/api';

// ============================================================================
// TYPES
// ============================================================================

export interface DashboardResponse {
  kpis: {
    total_usuarios: number;
    total_compras_ativas: number;
    volume_financeiro_mes: number;
    comissao_plataforma_mes: number;
    transacoes_validacao: number;
    disputas_abertas: number;
  };
  ultimas_transacoes: TransacaoItem[];
  alertas: AlertaItem[];
}

export interface TransacaoItem {
  id: number;
  fatura_ref: string;
  produto: string;
  quantidade: number;
  valor_total: number;
  comissao: number | null;
  status: string;
  data_criacao: string | null;
  comprador: { id: number; nome: string } | null;
  vendedor: { id: number; nome: string } | null;
  comprovativo_path: string | null;
}

export interface AlertaItem {
  tipo: 'disputa' | 'pagamento' | 'estoque';
  mensagem: string;
  link: string;
  urgencia: 'baixa' | 'media' | 'alta';
}

export interface ValidarPagamentoRequest {
  transacao_id: number;
  aprovar: boolean;
}

export interface ResolverDisputaRequest {
  transacao_id: number;
  favor: 'comprador' | 'vendedor';
  observacao: string;
}

export interface UsuarioItem {
  id: number;
  nome: string;
  email: string | null;
  telemovel: string;
  tipo: 'admin' | 'produtor' | 'comprador';
  perfil_completo: boolean;
  conta_validada: boolean;
  rating: number;
  data_criacao: string | null;
}

export interface ListarResponse<T> {
  itens: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// ============================================================================
// SERVICE
// ============================================================================

export const adminService = {
  /**
   * Carrega dashboard administrativo com KPIs
   * GET /api/admin/dashboard
   */
  async getDashboard(): Promise<ApiResponse<DashboardResponse>> {
    return await apiGet<DashboardResponse>('/api/admin/dashboard');
  },

  /**
   * Lista transações para administração
   * GET /api/admin/transacoes
   */
  async listarTransacoes(
    params?: {
      status?: string;
      page?: number;
      per_page?: number;
    }
  ): Promise<ApiResponse<ListarResponse<TransacaoItem>>> {
    const queryParams = new URLSearchParams();
    
    if (params?.status) queryParams.append('status', params.status);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
    
    const query = queryParams.toString();
    return await apiGet(`/api/admin/transacoes${query ? `?${query}` : ''}`);
  },

  /**
   * Valida pagamento (aprova ou rejeita comprovativo)
   * POST /api/admin/validar-pagamento
   */
  async validarPagamento(
    data: ValidarPagamentoRequest
  ): Promise<ApiResponse<void>> {
    return await apiPost('/api/admin/validar-pagamento', data);
  },

  /**
   * Resolve disputa (favorável a comprador ou vendedor)
   * POST /api/admin/resolver-disputa
   */
  async resolverDisputa(
    data: ResolverDisputaRequest
  ): Promise<ApiResponse<void>> {
    return await apiPost('/api/admin/resolver-disputa', data);
  },

  /**
   * Lista usuários para gestão
   * GET /api/admin/usuarios
   */
  async listarUsuarios(
    params?: {
      tipo?: 'admin' | 'produtor' | 'comprador';
      page?: number;
      per_page?: number;
    }
  ): Promise<ApiResponse<ListarResponse<UsuarioItem>>> {
    const queryParams = new URLSearchParams();
    
    if (params?.tipo) queryParams.append('tipo', params.tipo);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
    
    const query = queryParams.toString();
    return await apiGet(`/api/admin/usuarios${query ? `?${query}` : ''}`);
  },

  /**
   * Health check da API
   * GET /api/admin/health
   */
  async healthCheck(): Promise<ApiResponse<any>> {
    return await apiGet('/api/admin/health');
  },
};
