'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { SimpleKPICard } from '@/components/ui/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge, StatusBadge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { motion } from 'framer-motion';

function AdminDashboard() {
  const { user } = useAuth();

  const stats = {
    usuariosTotais: 6234,
    produtoresAtivos: 1089,
    compradoresAtivos: 5145,
    transacoesMes: 8920000,
    disputasPendentes: 7,
    taxaCrescimento: 23,
  };

  const ultimosUsuarios = [
    { id: 1, nome: 'João Pedro', email: 'joao@email.com', tipo: 'produtor', status: 'approved', data: '15/03/2024' },
    { id: 2, nome: 'Maria Santos', email: 'maria@email.com', tipo: 'comprador', status: 'pending', data: '15/03/2024' },
    { id: 3, nome: 'Carlos Lima', email: 'carlos@email.com', tipo: 'produtor', status: 'rejected', data: '14/03/2024' },
  ];

  const transacoesRecentes = [
    { id: 1, valor: 125000, status: 'completed', data: '15/03/2024 14:30' },
    { id: 2, valor: 450000, status: 'processing', data: '15/03/2024 13:15' },
    { id: 3, valor: 85000, status: 'pending', data: '15/03/2024 12:00' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white py-12 px-4 mb-8">
        <div className="container mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col md:flex-row justify-between items-center gap-4"
          >
            <div>
              <h1 className="font-brand text-4xl font-bold mb-2">
                Painel Administrativo 👋
              </h1>
              <p className="text-purple-100 text-lg">Bem-vindo, {user?.nome?.split(' ')[0]}</p>
            </div>
            <div className="flex gap-3">
              <Link href="/admin/relatorios">
                <Button variant="primary" size="lg" className="bg-white text-purple-600 hover:bg-purple-50 shadow-xl">
                  <i className="fas fa-chart-bar mr-2"></i>
                  Relatórios
                </Button>
              </Link>
              <Link href="/admin/configuracoes">
                <Button variant="primary" size="lg" className="bg-white/20 hover:bg-white/30 border-2 border-white shadow-xl">
                  <i className="fas fa-cog mr-2"></i>
                  Configurações
                </Button>
              </Link>
            </div>
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
            title="Total de Usuários"
            value={stats.usuariosTotais.toLocaleString()}
            icon={<i className="fas fa-users text-3xl"></i>}
            color="blue"
          />
          <SimpleKPICard
            title="Produtores Ativos"
            value={stats.produtoresAtivos.toLocaleString()}
            icon={<i className="fas fa-seedling text-3xl"></i>}
            color="green"
          />
          <SimpleKPICard
            title="Compradores Ativos"
            value={stats.compradoresAtivos.toLocaleString()}
            icon={<i className="fas fa-shopping-cart text-3xl"></i>}
            color="purple"
          />
          <SimpleKPICard
            title="Transações (Mês)"
            value={stats.transacoesMes}
            unit="Kz"
            isMoney
            icon={<i className="fas fa-exchange-alt text-3xl"></i>}
            color="yellow"
          />
        </motion.div>

        {/* Segunda linha de KPIs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8"
        >
          <SimpleKPICard
            title="Disputas Pendentes"
            value={stats.disputasPendentes}
            icon={<i className="fas fa-exclamation-triangle text-3xl"></i>}
            color="red"
          />
          <SimpleKPICard
            title="Taxa de Crescimento"
            value={`${stats.taxaCrescimento}%`}
            icon={<i className="fas fa-arrow-trend-up text-3xl"></i>}
            color="green"
          />
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Últimos Usuários */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="border-0 shadow-lg">
              <CardHeader className="bg-gray-50 border-b border-gray-100">
                <CardTitle className="flex justify-between items-center">
                  <span className="text-xl font-bold">Últimos Usuários</span>
                  <Link href="/admin/usuarios" className="text-sm text-purple-600 hover:underline font-medium">
                    Ver todos
                  </Link>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-gray-100">
                  {ultimosUsuarios.map((usuario) => (
                    <div key={usuario.id} className="p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-semibold text-gray-900">{usuario.nome}</h4>
                            <Badge variant="neutral" size="sm">{usuario.tipo}</Badge>
                          </div>
                          <p className="text-sm text-gray-500">{usuario.email}</p>
                          <p className="text-xs text-gray-400 mt-1">{usuario.data}</p>
                        </div>
                        <StatusBadge status={usuario.status as any} />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Transações Recentes */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="border-0 shadow-lg">
              <CardHeader className="bg-gray-50 border-b border-gray-100">
                <CardTitle className="flex justify-between items-center">
                  <span className="text-xl font-bold">Transações Recentes</span>
                  <Link href="/admin/transacoes" className="text-sm text-purple-600 hover:underline font-medium">
                    Ver todas
                  </Link>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-gray-100">
                  {transacoesRecentes.map((transacao) => (
                    <div key={transacao.id} className="p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-semibold text-gray-900">
                              {new Intl.NumberFormat('pt-AO', { style: 'currency', currency: 'AOA' }).format(transacao.valor)}
                            </h4>
                            <StatusBadge status={transacao.status as any} />
                          </div>
                          <p className="text-xs text-gray-400 mt-1">{transacao.data}</p>
                        </div>
                        <Link
                          href={`/admin/transacoes/${transacao.id}`}
                          className="text-purple-600 hover:text-purple-700 font-medium text-sm"
                        >
                          Ver detalhes
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Ações Rápidas Admin */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8"
        >
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gray-50 border-b border-gray-100">
              <CardTitle className="text-xl font-bold">Gestão da Plataforma</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { icon: 'fa-users', label: 'Usuários', href: '/admin/usuarios', color: 'blue' },
                  { icon: 'fa-seedling', label: 'Produtores', href: '/admin/produtores', color: 'green' },
                  { icon: 'fa-handshake', label: 'Disputas', href: '/admin/disputas', color: 'orange' },
                  { icon: 'fa-file-invoice-dollar', label: 'Pagamentos', href: '/admin/pagamentos', color: 'purple' },
                  { icon: 'fa-chart-line', label: 'Relatórios', href: '/admin/relatorios', color: 'red' },
                  { icon: 'fa-cog', label: 'Configurações', href: '/admin/configuracoes', color: 'gray' },
                  { icon: 'fa-bullhorn', label: 'Notificações', href: '/admin/notificacoes', color: 'yellow' },
                  { icon: 'fa-shield-alt', label: 'Segurança', href: '/admin/seguranca', color: 'green' },
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

export default function AdminDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <AdminDashboard />
    </ProtectedRoute>
  );
}
