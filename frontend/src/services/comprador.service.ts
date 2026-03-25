/**
 * Serviço de API do Comprador
 * Centraliza todas as chamadas relacionadas a operações de comprador
 */

import { apiPost, apiGet, apiUploadFile, ApiResponse } from '../lib/api';

// ============================================================================
// TYPES
// ============================================================================

export interface ReservaRequest {
  safra_id: number;
  quantidade: number;
  observacoes?: string;
}

export interface ReservaResponse {
  transacao_id: number;
  fatura_ref: string;
  valor_total: number;
  quantidade: number;
  status: string;
  produto: string;
}

export interface UploadComprovativoResponse {
  comprovativo_path: string;
  status_atual: string;
  fatura_ref: string;
}

export interface AvaliacaoRequest {
  transacao_id: number;
  nota: number; // 1-5
  comentario: string;
}

export interface AvaliacaoResponse {
  nota: number;
  rating_vendedor: number;
}

export interface DisputaRequest {
  transacao_id: number;
  tipo: string;
  titulo: string;
  descricao: string;
  valor_reclamacao?: number | null;
}

export interface DisputaResponse {
  disputa_id: string;
  protocolo: string;
  status_atual: string;
}

// ============================================================================
// SERVICE
// ============================================================================

export const compradorService = {
  /**
   * Reserva uma safra
   * POST /api/comprador/reservar
   */
  async reservarSafra(data: ReservaRequest): Promise<ApiResponse<ReservaResponse>> {
    return await apiPost<ReservaResponse>('/api/comprador/reservar', data);
  },

  /**
   * Faz upload do comprovativo de pagamento
   * POST /api/comprador/upload-comprovativo
   */
  async uploadComprovativo(
    transacaoId: number,
    file: File
  ): Promise<ApiResponse<UploadComprovativoResponse>> {
    const formData = new FormData();
    formData.append('transacao_id', transacaoId.toString());
    formData.append('comprovativo', file);

    return await apiUploadFile<UploadComprovativoResponse>(
      '/api/comprador/upload-comprovativo',
      formData
    );
  },

  /**
   * Avalia uma transação finalizada
   * POST /api/comprador/avaliar
   */
  async avaliarTransacao(data: AvaliacaoRequest): Promise<ApiResponse<AvaliacaoResponse>> {
    return await apiPost<AvaliacaoResponse>('/api/comprador/avaliar', data);
  },

  /**
   * Abre disputa para uma transação
   * POST /api/comprador/abrir-disputa
   */
  async abrirDisputa(data: DisputaRequest): Promise<ApiResponse<DisputaResponse>> {
    return await apiPost<DisputaResponse>('/api/comprador/abrir-disputa', data);
  },

  /**
   * Health check da API
   * GET /api/comprador/health
   */
  async healthCheck(): Promise<ApiResponse<any>> {
    return await apiGet('/api/comprador/health');
  },
};
