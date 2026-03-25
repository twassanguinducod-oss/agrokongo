'use client';

import { useState } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ReservaSafraForm, UploadComprovativo, AvaliacaoForm, DisputaForm } from '@/components/forms';
import { compradorService } from '@/services/comprador.service';
import { useApiError } from '@/hooks/useApiError';
import toast from 'react-hot-toast';

// Dados mockados para demonstração
const safraExemplo = {
  id: 1,
  produto: 'Milho Branco',
  quantidade_disponivel: 500,
  preco_unitario: 250,
  produtor_nome: 'Carlos D.',
  provincia: 'Huambo',
};

const transacaoExemplo = {
  id: 12345,
  faturaRef: 'AK-2026-A1B2C3D4',
  produtoNome: 'Milho Branco',
  produtorNome: 'Carlos D.',
  valorTransacao: 125000,
  status: 'aguardando_pagamento', // aguardando_pagamento, enviado, finalizado, etc.
};

export default function ExemploFormulariosPage() {
  const [formularioAtivo, setFormularioAtivo] = useState<'reserva' | 'upload' | 'avaliacao' | 'disputa'>('reserva');
  const [showReserva, setShowReserva] = useState(false);
  const { withErrorHandling } = useApiError();

  return (
    <ProtectedRoute allowedRoles={['comprador']}>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Formulários Complexos - Demo
            </h1>
            <p className="text-lg text-gray-600">
              Demonstração de todas as funcionalidades implementadas
            </p>
          </div>

          {/* Seletor de Formulário */}
          <Card className="mb-8 border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex flex-wrap gap-3">
                <Button
                  variant={formularioAtivo === 'reserva' ? 'primary' : 'outline'}
                  onClick={() => setFormularioAtivo('reserva')}
                >
                  <i className="fas fa-shopping-cart mr-2"></i>
                  Reserva de Safra
                </Button>
                <Button
                  variant={formularioAtivo === 'upload' ? 'primary' : 'outline'}
                  onClick={() => setFormularioAtivo('upload')}
                >
                  <i className="fas fa-upload mr-2"></i>
                  Upload Comprovativo
                </Button>
                <Button
                  variant={formularioAtivo === 'avaliacao' ? 'primary' : 'outline'}
                  onClick={() => setFormularioAtivo('avaliacao')}
                >
                  <i className="fas fa-star mr-2"></i>
                  Avaliação
                </Button>
                <Button
                  variant={formularioAtivo === 'disputa' ? 'danger' : 'outline'}
                  onClick={() => setFormularioAtivo('disputa')}
                >
                  <i className="fas fa-gavel mr-2"></i>
                  Disputa
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Renderização Condicional dos Formulários */}
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Coluna Esquerda - Informações */}
            <div>
              <Card className="border-0 shadow-lg mb-6">
                <CardHeader className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
                  <CardTitle>Contexto da Transação</CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Produto:</span>
                      <span className="font-semibold">{safraExemplo.produto}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Quantidade:</span>
                      <span className="font-semibold">{safraExemplo.quantidade_disponivel} kg</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Preço Unitário:</span>
                      <span className="font-semibold text-green-600">
                        {new Intl.NumberFormat('pt-AO', { style: 'currency', currency: 'AOA' }).format(safraExemplo.preco_unitario)}/kg
                      </span>
                    </div>
                    <div className="border-t pt-4 mt-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-600">Fatura:</span>
                        <Badge variant="info">{transacaoExemplo.faturaRef}</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Status:</span>
                        <Badge variant={
                          transacaoExemplo.status === 'finalizado' ? 'success' :
                          transacaoExemplo.status === 'aguardando_pagamento' ? 'warning' :
                          'info'
                        }>
                          {transacaoExemplo.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Documentação */}
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle>
                    <i className="fas fa-book mr-2 text-blue-600"></i>
                    Integração com Backend
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-800 mb-2"><strong>Status da Implementação:</strong></p>
                    <ul className="list-disc list-inside space-y-1 text-sm text-blue-800">
                      <li>✅ Componentes UI criados</li>
                      <li>✅ Validações implementadas</li> <li>✅ UX/UI sofisticada</li>
                      <li>⏳ Aguardando endpoints da API Flask</li>
                    </ul>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <p className="text-sm font-semibold text-gray-900 mb-2">Endpoints Implementados:</p>
                    <code className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded block mb-2 border border-green-200">
                      ✅ POST /api/comprador/reservar
                    </code>
                    <code className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded block mb-2 border border-green-200">
                      ✅ POST /api/comprador/upload-comprovativo
                    </code>
                    <code className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded block mb-2 border border-green-200">
                      ✅ POST /api/comprador/avaliar
                    </code>
                    <code className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded block mb-2 border border-green-200">
                      ✅ POST /api/comprador/abrir-disputa
                    </code>
                    <code className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded block border border-green-200">
                      ✅ GET /api/comprador/health
                    </code>
                  </div>

                  <div className="mt-4 bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <p className="text-sm font-semibold text-blue-900 mb-2">Camada de API:</p>
                    <ul className="text-xs text-blue-800 space-y-1">
                      <li>• <strong>lib/api.ts</strong> - HTTP client genérico</li>
                      <li>• <strong>services/comprador.service.ts</strong> - Service layer</li>
                      <li>• <strong>hooks/useApiError.ts</strong> - Error handling</li>
                      <li>• Tratamento automático de erros</li>
                      <li>• Retry e fallback embutidos</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Coluna Direita - Formulário Ativo */}
            <div>
              {formularioAtivo === 'reserva' && (
                <ReservaSafraForm safra={safraExemplo} />
              )}
              
              {formularioAtivo === 'upload' && (
                <UploadComprovativo
                  transacaoId={transacaoExemplo.id}
                  faturaRef={transacaoExemplo.faturaRef}
                />
              )}
              
              {formularioAtivo === 'avaliacao' && (
                <AvaliacaoForm
                  transacaoId={transacaoExemplo.id}
                  produtoNome={transacaoExemplo.produtoNome}
                  produtorNome={transacaoExemplo.produtorNome}
                />
              )}
              
              {formularioAtivo === 'disputa' && (
                <DisputaForm
                  transacaoId={transacaoExemplo.id}
                  faturaRef={transacaoExemplo.faturaRef}
                  produtoNome={transacaoExemplo.produtoNome}
                  valorTransacao={transacaoExemplo.valorTransacao}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
