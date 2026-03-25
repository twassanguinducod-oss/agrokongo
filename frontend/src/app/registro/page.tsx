// frontend/src/app/registro/page.tsx
'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';

type UserType = 'produtor' | 'comprador' | 'admin';
type Step = 1 | 2;

export default function RegistroPage() {
  const { register, updateUser } = useAuth();
  const router = useRouter();

  const [step, setStep] = useState<Step>(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [step1Data, setStep1Data] = useState({
    telemovel: '',
    senha: '',
    senha_confirmacao: '',
  });

  const [step2Data, setStep2Data] = useState({
    tipo: 'produtor' as UserType,
    first_name: '',
    last_name: '',
    nif: '',
    iban: '',
    provincia: '',
    municipio: '',
    email: '',
  });

  // Função para formatar erros do Django
  const formatDjangoError = (data: any): string => {
    if (typeof data === 'string') return data;
    if (data.error) return data.error;
    if (data.message) return data.message;
    if (data.detail) return data.detail;

    // Erros por campo: { "telemovel": ["erro1", "erro2"], "senha": ["erro3"] }
    const errors = Object.keys(data).map(key => {
      const fieldName = key.charAt(0).toUpperCase() + key.slice(1);
      const messages = Array.isArray(data[key]) ? data[key].join(', ') : data[key];
      return `${fieldName}: ${messages}`;
    });

    return errors.length > 0 ? errors.join(' | ') : 'Erro desconhecido';
  };

  const handleStep1Submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (step1Data.telemovel.length !== 9) {
      setError('O telemóvel deve ter 9 dígitos');
      setIsLoading(false);
      return;
    }

    if (step1Data.senha.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres');
      setIsLoading(false);
      return;
    }

    if (step1Data.senha !== step1Data.senha_confirmacao) {
      setError('As senhas não coincidem');
      setIsLoading(false);
      return;
    }

    try {
      await register({
        telemovel: step1Data.telemovel,
        senha: step1Data.senha,
        senha_confirmacao: step1Data.senha_confirmacao,
      });
      setStep(2);
    } catch (err: any) {
      const errorMsg = formatDjangoError(err.response?.data || err.message || 'Erro ao criar conta');
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStep2Submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!step2Data.first_name || !step2Data.last_name) {
      setError('Nome e sobrenome são obrigatórios');
      setIsLoading(false);
      return;
    }

    try {
      await updateUser({
        tipo: step2Data.tipo,
        first_name: step2Data.first_name,
        last_name: step2Data.last_name,
        nif: step2Data.nif,
        iban: step2Data.iban,
        provincia: step2Data.provincia,
        municipio: step2Data.municipio,
        email: step2Data.email || undefined,
      });
      router.push('/dashboard');
    } catch (err: any) {
      const errorMsg = formatDjangoError(err.response?.data || err.message || 'Erro ao completar perfil');
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const userTypeOptions = [
    { value: 'produtor', label: 'Produtor', icon: 'fa-seedling', description: 'Quero vender produtos', color: 'green' },
    { value: 'comprador', label: 'Comprador', icon: 'fa-shopping-cart', description: 'Quero comprar produtos', color: 'blue' },
  ];

  return (
    <div className="min-h-screen flex">
      <div
        className="hidden lg:flex lg:w-1/2 relative"
        style={{
          backgroundImage: 'url(https://images.pexels.com/photos/7821256/pexels-photo-7821256.jpeg?auto=compress&cs=tinysrgb&w=1920)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-green-900/90 to-green-800/70" />
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-white text-center m-auto p-8"
        >
          <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 className="text-5xl font-bold mb-4">Junte-se ao AgroKongo</h1>
          <p className="text-xl mb-8 text-gray-200">Faça parte da maior plataforma de comércio agrícola de Angola</p>
        </motion.div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-lg"
        >
          <Card className="border-0 shadow-xl">
            <CardContent className="p-8">
              <div className="flex items-center justify-center mb-8">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 1 ? 'bg-green-600 text-white' : 'bg-gray-200'}`}>1</div>
                  <div className={`w-16 h-1 rounded ${step >= 2 ? 'bg-green-600' : 'bg-gray-200'}`} />
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 2 ? 'bg-green-600 text-white' : 'bg-gray-200'}`}>2</div>
                </div>
              </div>

              <div className="mb-8 text-center">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">{step === 1 ? 'Criar Conta' : 'Completar Perfil'}</h2>
                <p className="text-gray-600">{step === 1 ? 'Informe seu telemóvel e senha' : 'Complete seus dados pessoais'}</p>
              </div>

              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  <i className="fas fa-exclamation-circle mr-2"></i>{error}
                </div>
              )}

              <AnimatePresence mode="wait">
                {step === 1 && (
                  <motion.form
                    key="step1"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    onSubmit={handleStep1Submit}
                    className="space-y-5"
                  >
                    <Input label="Telemóvel" type="tel" value={step1Data.telemovel} onChange={(e) => setStep1Data({ ...step1Data, telemovel: e.target.value })} placeholder="9XX XXX XXX" required leftIcon={<i className="fas fa-phone"></i>} maxLength={9} />
                    <Input label="Senha" type="password" value={step1Data.senha} onChange={(e) => setStep1Data({ ...step1Data, senha: e.target.value })} placeholder="••••••••" required leftIcon={<i className="fas fa-lock"></i>} />
                    <Input label="Confirmar Senha" type="password" value={step1Data.senha_confirmacao} onChange={(e) => setStep1Data({ ...step1Data, senha_confirmacao: e.target.value })} placeholder="••••••••" required leftIcon={<i className="fas fa-lock"></i>} />
                    <div className="flex items-start gap-3">
                      <input type="checkbox" id="terms" className="w-4 h-4 text-green-600 rounded mt-1" required />
                      <label htmlFor="terms" className="text-sm text-gray-600">Concordo com os <Link href="/termos" className="text-green-600 underline">Termos de Uso</Link></label>
                    </div>
                    <Button type="submit" variant="primary" fullWidth isLoading={isLoading} className="py-4 text-lg">{isLoading ? 'Criando Conta...' : 'Criar Conta'}</Button>
                  </motion.form>
                )}

                {step === 2 && (
                  <motion.form
                    key="step2"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    onSubmit={handleStep2Submit}
                    className="space-y-5"
                  >
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                      <i className="fas fa-check-circle text-green-600 text-2xl mb-2"></i>
                      <p className="text-green-700 font-medium">Conta criada com sucesso!</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-3">Tipo de Conta:</label>
                      <div className="grid grid-cols-2 gap-3">
                        {userTypeOptions.map((type) => (
                          <button key={type.value} type="button" onClick={() => setStep2Data({ ...step2Data, tipo: type.value as UserType })} className={`p-4 rounded-xl border-2 ${step2Data.tipo === type.value ? 'border-green-600 bg-green-50' : 'border-gray-200'}`}>
                            <i className={`fas ${type.icon} text-2xl mb-2`}></i>
                            <div className="font-semibold">{type.label}</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <Input label="Nome" value={step2Data.first_name} onChange={(e) => setStep2Data({ ...step2Data, first_name: e.target.value })} required />
                      <Input label="Sobrenome" value={step2Data.last_name} onChange={(e) => setStep2Data({ ...step2Data, last_name: e.target.value })} required />
                    </div>

                    <Input label="NIF" value={step2Data.nif} onChange={(e) => setStep2Data({ ...step2Data, nif: e.target.value })} />
                    <Input label="IBAN" value={step2Data.iban} onChange={(e) => setStep2Data({ ...step2Data, iban: e.target.value })} />
                    <div className="grid grid-cols-2 gap-4">
                      <Input label="Província" value={step2Data.provincia} onChange={(e) => setStep2Data({ ...step2Data, provincia: e.target.value })} required />
                      <Input label="Município" value={step2Data.municipio} onChange={(e) => setStep2Data({ ...step2Data, municipio: e.target.value })} required />
                    </div>
                    <Input label="Email (Opcional)" type="email" value={step2Data.email} onChange={(e) => setStep2Data({ ...step2Data, email: e.target.value })} />

                    <Button type="submit" variant="primary" fullWidth isLoading={isLoading} className="py-4 text-lg">{isLoading ? 'Completando...' : 'Completar e Ir para Dashboard'}</Button>
                  </motion.form>
                )}
              </AnimatePresence>

              <div className="mt-8 pt-6 border-t text-center">
                <p className="text-sm text-gray-600">Já tem conta? <Link href="/login" className="text-green-600 font-semibold">Fazer Login</Link></p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}