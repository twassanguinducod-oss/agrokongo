'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Input';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function MercadoPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filtroProvincia, setFiltroProvincia] = useState('');
  const [filtroCategoria, setFiltroCategoria] = useState('');

  const provincias = ['Todas', 'Luanda', 'Benguela', 'Huambo', 'Huíla', 'Cabinda'];
  const categorias = ['Todos', 'Cereais', 'Leguminosas', 'Frutas', 'Verduras', 'Tubérculos'];

  const produtos = [
    { id: 1, nome: 'Milho Branco', produtor: 'Carlos D.', provincia: 'Huambo', quantidade: '500 kg', preco: 250, unidade: 'kg', imagem: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80' },
    { id: 2, nome: 'Feijão Nhemba', produtor: 'Ana P.', provincia: 'Huíla', quantidade: '300 kg', preco: 450, unidade: 'kg', imagem: 'https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80' },
    { id: 3, nome: 'Café Arábica', produtor: 'José M.', provincia: 'Uíge', quantidade: '200 kg', preco: 1200, unidade: 'kg', imagem: 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80' },
    { id: 4, nome: 'Batata Doce', produtor: 'Maria S.', provincia: 'Benguela', quantidade: '1000 kg', preco: 180, unidade: 'kg', imagem: 'https://images.unsplash.com/photo-1601648764658-ad77dd8e87a6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80' },
    { id: 5, nome: 'Banana', produtor: 'Pedro L.', provincia: 'Luanda', quantidade: '400 kg', preco: 300, unidade: 'kg', imagem: 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80' },
    { id: 6, nome: 'Mandioca', produtor: 'João K.', provincia: 'Cabinda', quantidade: '800 kg', preco: 150, unidade: 'kg', imagem: 'https://images.unsplash.com/photo-1621960663003-6608fa7d7c25?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white py-16 px-4 mb-8">
        <div className="container mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <h1 className="font-brand text-5xl md:text-6xl font-bold mb-4">
              Mercado Agrícola
            </h1>
            <p className="text-xl text-green-100 max-w-2xl mx-auto">
              Encontre os melhores produtos agrícolas diretamente dos produtores angolanos
            </p>
          </motion.div>
        </div>
      </div>

      <div className="container mx-auto max-w-7xl px-4">
        {/* Filtros */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="grid md:grid-cols-4 gap-4">
                <Input
                  placeholder="🔍 Buscar produto..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Select
                  value={filtroProvincia}
                  onChange={(e) => setFiltroProvincia(e.target.value)}
                  options={[
                    { value: '', label: 'Todas as Províncias' },
                    ...provincias.map(p => ({ value: p, label: p })),
                  ]}
                />
                <Select
                  value={filtroCategoria}
                  onChange={(e) => setFiltroCategoria(e.target.value)}
                  options={[
                    { value: '', label: 'Todas as Categorias' },
                    ...categorias.map(c => ({ value: c, label: c })),
                  ]}
                />
                <Button variant="primary" className="w-full">
                  <i className="fas fa-filter mr-2"></i>
                  Filtrar
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Grid de Produtos */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {produtos.map((produto, index) => (
            <motion.div
              key={produto.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="border-0 shadow-lg overflow-hidden hover:shadow-xl transition-shadow group">
                <div className="h-48 overflow-hidden relative">
                  <img
                    src={produto.imagem}
                    alt={produto.nome}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute top-3 right-3">
                    <Badge variant="success" size="sm">Disponível</Badge>
                  </div>
                </div>
                <CardContent className="p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-1">{produto.nome}</h3>
                      <p className="text-sm text-gray-500">
                        <i className="fas fa-user mr-1"></i>{produto.produtor}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center mb-3">
                    <div className="text-2xl font-bold text-green-600">
                      {new Intl.NumberFormat('pt-AO', { style: 'currency', currency: 'AOA' }).format(produto.preco)}
                      <span className="text-sm text-gray-500">/{produto.unidade}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">{produto.quantidade}</div>
                      <div className="text-xs text-gray-400">
                        <i className="fas fa-location-dot mr-1"></i>{produto.provincia}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Link href={`/mercado/${produto.id}`} className="flex-1">
                      <Button variant="primary" fullWidth>
                        <i className="fas fa-shopping-cart mr-2"></i>
                        Reservar
                      </Button>
                    </Link>
                    <Button variant="outline" className="px-4">
                      <i className="far fa-heart"></i>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Paginação */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-12 flex justify-center"
        >
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((page) => (
              <button
                key={page}
                className={`w-10 h-10 rounded-lg font-semibold transition-colors ${
                  page === 1
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {page}
              </button>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
