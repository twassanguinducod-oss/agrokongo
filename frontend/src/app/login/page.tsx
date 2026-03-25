// frontend/src/app/login/page.tsx
'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get('redirect') || '/';

  const [formData, setFormData] = useState({
    telemovel: '',
    senha: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

  try {
    // ✅ CORRETO: Passar telemovel e senha separadamente
    await login(formData.telemovel, formData.senha);
    router.push(redirect);
  } catch (err: any) {
    setError(err.response?.data?.error || err.message || 'Erro ao fazer login');
  } finally {
    setIsLoading(false);
  }
  };

  return (
    <div className="min-h-screen flex">
      {/* ===========================================
          LEFT SIDE - IMAGEM DE AGRICULTOR AFRICANO
          =========================================== */}
      <div
        className="hidden lg:flex lg:w-1/2 relative"
        style={{
          backgroundImage: 'url(https://images.pexels.com/photos/7821256/pexels-photo-7821256.jpeg?auto=compress&cs=tinysrgb&w=1920)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-green-900/90 to-green-800/70" />

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-white text-center m-auto p-8"
        >
          <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>

          <h1 className="text-5xl font-bold mb-4">AgroKongo</h1>
          <p className="text-xl mb-8 text-gray-200">
            Conectando a terra ao mercado com segurança e confiança
          </p>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div className="text-3xl font-bold text-green-400">1000+</div>
              <div className="text-sm text-gray-300">Produtores</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div className="text-3xl font-bold text-blue-400">5000+</div>
              <div className="text-sm text-gray-300">Compradores</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div className="text-3xl font-bold text-purple-400">98%</div>
              <div className="text-sm text-gray-300">Satisfação</div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* ===========================================
          RIGHT SIDE - FORMULÁRIO DE LOGIN
          =========================================== */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          <Card className="border-0 shadow-xl">
            <CardContent className="p-8">
              {/* Mobile Logo */}
              <div className="lg:hidden text-center mb-8">
                <div className="w-16 h-16 bg-green-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <h1 className="text-3xl font-bold text-green-600 mb-2">AgroKongo</h1>
                <p className="text-gray-600">Bem-vindo de volta!</p>
              </div>

              {/* Header */}
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Login</h2>
                <p className="text-gray-600">
                  Ainda não tem conta?{' '}
                  <Link href="/registro" className="text-green-600 hover:text-green-700 font-semibold underline">
                    Criar Conta
                  </Link>
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  <i className="fas fa-exclamation-circle mr-2"></i>
                  {error}
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Telemóvel */}
                <Input
                  label="Telemóvel"
                  type="tel"
                  value={formData.telemovel}
                  onChange={(e) => setFormData({ ...formData, telemovel: e.target.value })}
                  placeholder="9XX XXX XXX"
                  required
                  leftIcon={<i className="fas fa-phone"></i>}
                  helperText="Número de Angola (9 dígitos)"
                  maxLength={9}
                />

                {/* Senha */}
                <Input
                  label="Palavra-passe"
                  type="password"
                  value={formData.senha}
                  onChange={(e) => setFormData({ ...formData, senha: e.target.value })}
                  placeholder="••••••••"
                  required
                  leftIcon={<i className="fas fa-lock"></i>}
                />

                {/* Lembrar-me & Esqueci Senha */}
                <div className="flex items-center justify-between">
                  <label className="flex items-center">
                    <input type="checkbox" className="w-4 h-4 text-green-600 rounded focus:ring-green-500" />
                    <span className="ml-2 text-sm text-gray-600">Lembrar-me</span>
                  </label>
                  <Link href="/recuperar-senha" className="text-sm text-green-600 hover:text-green-700 font-medium">
                    Esqueceu a senha?
                  </Link>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  variant="primary"
                  fullWidth
                  isLoading={isLoading}
                  className="py-3 text-lg"
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Entrando...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-sign-in-alt mr-2"></i>
                      Entrar
                    </>
                  )}
                </Button>
              </form>

              {/* Divider */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <p className="text-center text-sm text-gray-600 mb-4">Ou continue com</p>
                <div className="grid grid-cols-2 gap-4">
                  <button className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                    <i className="fab fa-google text-red-500"></i>
                    <span className="font-medium">Google</span>
                  </button>
                  <button className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                    <i className="fab fa-facebook text-blue-600"></i>
                    <span className="font-medium">Facebook</span>
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Back Link */}
          <p className="text-center mt-8 text-sm text-gray-600">
            <Link href="/" className="text-green-600 hover:text-green-700 font-medium">
              <i className="fas fa-arrow-left mr-2"></i>
              Voltar para o início
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}