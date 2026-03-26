'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { SimpleKPICard } from '@/components/ui/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge, StatusBadge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { motion } from 'framer-motion';

function CompradorDashboard() {
  const { user } = useAuth();

  const stats = {
    reservasAtivas: 5,
    comprasMes: 320000,
    produtoresFavoritos: 12,
    avaliacaoMedia: 4.5,
  };

  const ultimasReservas = [
    { id: 1, produtor: 'Carlos D.', produto: 'Milho Branco', quantidade: '200 kg', status: 'pending', data: '15/03/2024' },
    { id: 2, produtor: 'Ana P.', produto: 'Feijão', quantidade: '100 kg', status: 'approved', data: '14/03/2024' },
    { id: 3, produtor: 'José M.', produto: 'Café', quantidade: '50 kg', status: 'completed', data: '13/03/2024' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white py-12 px-4 mb-8">
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
              <p className="text-blue-100 text-lg">Bem-vindo ao seu painel de comprador</p>
            </div>
            <Link href="/mercado">
              <Button variant="primary" size="lg" className="bg-white text-blue-600 hover:bg-blue-50 shadow-xl">
                <i className="fas fa-shopping-cart mr-2"></i>
                Explorar Mercado
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
            title="Reservas Ativas"
            value={stats.reservasAtivas}
            icon={<i className="fas fa-calendar-check text-3xl"></i>}
            color="blue"
          />
          <SimpleKPICard
            title="Compras este Mês"
            value={stats.comprasMes}
            unit="Kz"
            isMoney
            icon={<i className="fas fa-shopping-bag text-3xl"></i>}
            color="green"
          />
          <SimpleKPICard
            title="Produtores Favoritos"
            value={stats.produtoresFavoritos}
            icon={<i className="fas fa-heart text-3xl"></i>}
            color="red"
          />
          <SimpleKPICard
            title="Avaliação Média"
            value={stats.avaliacaoMedia}
            icon={<i className="fas fa-star text-3xl"></i>}
            color="yellow"
          />
        </motion.div>

        {/* Últimas Reservas */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gray-50 border-b border-gray-100">
              <CardTitle className="flex justify-between items-center">
                <span className="text-xl font-bold">Últimas Reservas</span>
                <Link href="/comprador/reservas" className="text-sm text-blue-600 hover:underline font-medium">
                  Ver todas
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-gray-100">
                {ultimasReservas.map((reserva) => (
                  <div key={reserva.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-gray-900">{reserva.produtor}</h4>
                          <StatusBadge status={reserva.status as any} />
                        </div>
                        <p className="text-sm text-gray-500">{reserva.produto} • {reserva.quantidade}</p>
                        <p className="text-xs text-gray-400 mt-1">{reserva.data}</p>
                      </div>
                      <div className="flex gap-2">
                        <Link
                          href={`/reserva/${reserva.id}`}
                          className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                        >
                          Ver detalhes
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Ações Rápidas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8"
        >
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gray-50 border-b border-gray-100">
              <CardTitle className="text-xl font-bold">Ações Rápidas</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { icon: 'fa-store', label: 'Mercado', href: '/mercado', color: 'green' },
                  { icon: 'fa-calendar-check', label: 'Minhas Reservas', href: '/comprador/reservas', color: 'blue' },
                  { icon: 'fa-shopping-cart', label: 'Compras', href: '/comprador/compras', color: 'purple' },
                  { icon: 'fa-heart', label: 'Favoritos', href: '/comprador/favoritos', color: 'red' },
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

export default function CompradorDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={['comprador']}>
      <CompradorDashboard />
    </ProtectedRoute>
  );
}
