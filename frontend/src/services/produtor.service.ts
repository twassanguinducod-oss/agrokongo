/**
 * Serviço de API do Produtor
 * Centraliza todas as chamadas relacionadas a operações de produtor
 */

import { apiPost, apiGet, ApiResponse } from '../lib/api';

// ============================================================================
// TYPES
// ============================================================================

export interface SafraRequest {
  produto_nome: string;
  categoria?: string;
  quantidade_disponivel: number;
  preco_unitario: number;
  unidade_medida?: string;
  descricao?: string;
  provincia_id?: number;
  municipio_id?: number;
  data_colheita?: string; // ISO format
}

export interface SafraResponse {
  safra_id: number;
  produto_nome: string;
}

export interface ConfirmarReservaRequest {
  transacao_id: number;
  confirmar: boolean;
}

export interface ListarResponse<T> {
  itens: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface SafraItem {
  id: number;
  produto_nome: string;
  categoria: string;
  quantidade_disponivel: number;
  preco_unitario: number;
  unidade_medida: string;
  descricao: string;
  data_criacao: string | null;
  data_colheita: string | null;
  imagem_path: string | null;
  produtor_nome: string;
  provincia: string;
  municipio: string;
}

export interface VendaItem {
  id: number;
  fatura_ref: string;
  produto: string;
  quantidade: number;
  valor_total: number;
  valor_liquido: number | null;
  status: string;
  data_criacao: string | null;
  comprador_nome: string;
  avaliacao: { nota: number | null } | null;
}

// ============================================================================
// SERVICE
// ============================================================================

export const produtorService = {
  /**
   * Lista safras do produtor
   * GET /api/produtor/safras
   */
  async listarSafras(
    params?: {
      status?: 'ativo' | 'inativo' | 'todos';
      page?: number;
      per_page?: number;
    }
  ): Promise<ApiResponse<ListarResponse<SafraItem>>> {
    const queryParams = new URLSearchParams();
    
    if (params?.status) queryParams.append('status', params.status);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
    
    const query = queryParams.toString();
    return await apiGet(`/api/produtor/safras${query ? `?${query}` : ''}`);
  },

  /**
   * Cria uma nova safra
   * POST /api/produtor/safras
   */
  async criarSafra(data: SafraRequest): Promise<ApiResponse<SafraResponse>> {
    return await apiPost<SafraResponse>('/api/produtor/safras', data);
  },

  /**
   * Confirma ou recusa reserva de safra
   * POST /api/produtor/confirmar-reserva
   */
  async confirmarReserva(
    data: ConfirmarReservaRequest
  ): Promise<ApiResponse<void>> {
    return await apiPost('/api/produtor/confirmar-reserva', data);
  },

  /**
   * Lista vendas do produtor
   * GET /api/produtor/vendas
   */
  async listarVendas(
    params?: {
      status?: string;
      page?: number;
      per_page?: number;
    }
  ): Promise<ApiResponse<ListarResponse<VendaItem>>> {
    const queryParams = new URLSearchParams();
    
    if (params?.status) queryParams.append('status', params.status);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
    
    const query = queryParams.toString();
    return await apiGet(`/api/produtor/vendas${query ? `?${query}` : ''}`);
  },

  /**
   * Health check da API
   * GET /api/produtor/health
   */
  async healthCheck(): Promise<ApiResponse<any>> {
    return await apiGet('/api/produtor/health');
  },
};
