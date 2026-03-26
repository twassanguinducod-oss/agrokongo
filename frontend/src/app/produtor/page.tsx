'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { KPICard, SimpleKPICard } from '@/components/ui/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge, StatusBadge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { motion } from 'framer-motion';

function ProdutorDashboard() {
  const { user } = useAuth();

  // Dados mockados (seriam buscados da API)
  const stats = {
    safrasAtivas: 8,
    vendasMes: 450000,
    taxaConversao: 68,
    avaliacaoMedia: 4.7,
  };

  const safrasRecentes = [
    { id: 1, produto: 'Milho Branco', quantidade: '500 kg', status: 'pending', data: '15/03/2024' },
    { id: 2, produto: 'Feijão Nhemba', quantidade: '300 kg', status: 'approved', data: '14/03/2024' },
    { id: 3, produto: 'Café Arábica', quantidade: '200 kg', status: 'completed', data: '13/03/2024' },
  ];

  const ultimasVendas = [
    { id: 1, comprador: 'João M.', produto: 'Milho', valor: 125000, status: 'processing' },
    { id: 2, comprador: 'Maria S.', produto: 'Feijão', valor: 85000, status: 'completed' },
    { id: 3, comprador: 'Pedro L.', produto: 'Café', valor: 240000, status: 'pending' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white py-12 px-4 mb-8">
        <div className="container mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col md:flex-row justify-between items-center gap-4"
          >
            <div>
              <h1 className="font-brand text-4xl font-bold mb-2">
                Olá, {user?.nome?.split(' ')[0]}! 👋
              </h1>
              <p className="text-green-100 text-lg">Bem-vindo ao seu painel de produtor</p>
            </div>
            <Link href="/produtor/nova-safra">
              <Button variant="primary" size="lg" className="bg-white text-green-600 hover:bg-green-50 shadow-xl">
                <i className="fas fa-plus-circle mr-2"></i>
                Publicar Nova Safra
              </Button>
            </Link>
          </motion.div>
        </div>
      </div>

      <div className="container mx-auto max-w-7xl px-4">
        {/* KPIs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <SimpleKPICard
            title="Safras Ativas"
            value={stats.safrasAtivas}
            icon={<i className="fas fa-seedling text-3xl"></i>}
            color="green"
          />
          <SimpleKPICard
            title="Vendas este Mês"
            value={stats.vendasMes}
            unit="Kz"
            isMoney
            icon={<i className="fas fa-chart-line text-3xl"></i>}
            color="blue"
          />
          <SimpleKPICard
            title="Taxa de Conversão"
            value={`${stats.taxaConversao}%`}
            icon={<i className="fas fa-percentage text-3xl"></i>}
            color="purple"
          />
          <SimpleKPICard
            title="Avaliação Média"
            value={stats.avaliacaoMedia}
            icon={<i className="fas fa-star text-3xl"></i>}
            color="yellow"
          />
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Safras Recentes */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="border-0 shadow-lg">
              <CardHeader className="bg-gray-50 border-b border-gray-100">
                <CardTitle className="flex justify-between items-center">
                  <span className="text-xl font-bold">Safras Recentes</span>
                  <Link href="/produtor/safras" className="text-sm text-green-600 hover:underline font-medium">
                    Ver todas
                  </Link>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-gray-100">
                  {safrasRecentes.map((safra) => (
                    <div key={safra.id} className="p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-semibold text-gray-900">{safra.produto}</h4>
                          <p className="text-sm text-gray-500">{safra.quantidade} • {safra.data}</p>
                        </div>
                        <StatusBadge status={safra.status as any} />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Últimas Vendas */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="border-0 shadow-lg">
              <CardHeader className="bg-gray-50 border-b border-gray-100">
                <CardTitle className="flex justify-between items-center">
                  <span className="text-xl font-bold">Últimas Vendas</span>
                  <Link href="/produtor/vendas" className="text-sm text-green-600 hover:underline font-medium">
                    Ver todas
                  </Link>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-gray-100">
                  {ultimasVendas.map((venda) => (
                    <div key={venda.id} className="p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-semibold text-gray-900">{venda.comprador}</h4>
                            <StatusBadge status={venda.status as any} />
                          </div>
                          <p className="text-sm text-gray-500">{venda.produto}</p>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-green-600">
                            {new Intl.NumberFormat('pt-AO', { style: 'currency', currency: 'AOA' }).format(venda.valor)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Ações Rápidas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8"
        >
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gray-50 border-b border-gray-100">
              <CardTitle className="text-xl font-bold">Ações Rápidas</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { icon: 'fa-plus-circle', label: 'Nova Safra', href: '/produtor/nova-safra', color: 'green' },
                  { icon: 'fa-box', label: 'Meus Produtos', href: '/produtor/safras', color: 'blue' },
                  { icon: 'fa-shopping-cart', label: 'Vendas', href: '/produtor/vendas', color: 'purple' },
                  { icon: 'fa-comments', label: 'Mensagens', href: '/produtor/mensagens', color: 'orange' },
                ].map((action, index) => (
                  <Link
                    key={index}
                    href={action.href}
                    className={`group p-6 rounded-xl border-2 border-${action.color}-100 hover:border-${action.color}-500 hover:bg-${action.color}-50 transition-all duration-300 text-center`}
                  >
                    <i className={`fas ${action.icon} text-3xl text-${action.color}-600 mb-3 group-hover:scale-110 transition-transform`}></i>
                    <div className="font-semibold text-gray-900">{action.label}</div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}

export default function ProdutorDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={['produtor']}>
      <ProdutorDashboard />
    </ProtectedRoute>
  );
}
