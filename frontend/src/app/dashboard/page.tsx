// frontend/src/app/dashboard/page.tsx
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default function DashboardPage() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  if (!isAuthenticated) {
    router.push('/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header com Background Africano */}
      <section className="relative h-48 overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: 'url(https://images.unsplash.com/photo-1627920769838-5b1507d1e6e6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80)',
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-green-900/90 to-green-800/80" />

        <div className="relative z-10 container mx-auto px-4 h-full flex items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-white"
          >
            <h1 className="text-4xl font-bold mb-2">
              Olá, {user?.username}! 👋
            </h1>
            <p className="text-green-100 text-lg">
              Bem-vindo ao seu painel {user?.tipo === 'produtor' ? 'de produtor' : user?.tipo === 'comprador' ? 'de comprador' : 'administrativo'}
            </p>
          </motion.div>
        </div>
      </section>

      {/* Conteúdo Principal */}
      <div className="container mx-auto max-w-7xl px-4 py-8">
        {/* KPIs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {[
            { title: 'Safras Ativas', value: '8', icon: 'fa-seedling', color: 'green' },
            { title: 'Vendas este Mês', value: '450.000', unit: 'Kz', icon: 'fa-chart-line', color: 'blue' },
            { title: 'Taxa de Conversão', value: '68%', icon: 'fa-percentage', color: 'purple' },
            { title: 'Avaliação Média', value: '4.7', icon: 'fa-star', color: 'yellow' },
          ].map((kpi, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
            >
              <Card className="border-0 shadow-lg">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">{kpi.title}</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {kpi.value} {kpi.unit}
                      </p>
                    </div>
                    <div className={`w-12 h-12 bg-${kpi.color}-100 rounded-full flex items-center justify-center`}>
                      <i className={`fas ${kpi.icon} text-${kpi.color}-600 text-xl`}></i>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Ações Rápidas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
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