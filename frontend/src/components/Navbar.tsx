// frontend/src/components/Navbar.tsx
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const pathname = usePathname();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const getNavLinks = () => {
    const publicLinks = [
      { href: '/', label: 'Início' },
      { href: '/mercado', label: 'Mercado' },
      { href: '/sobre', label: 'Sobre' },
      { href: '/contacto', label: 'Contacto' },
    ];

    if (user?.tipo === 'admin') {
      return [...publicLinks, { href: '/admin/dashboard', label: 'Painel Admin' }];
    }
    if (user?.tipo === 'produtor') {
      return [...publicLinks, { href: '/produtor/dashboard', label: 'Dashboard' }, { href: '/produtor/safras', label: 'Minhas Safras' }];
    }
    if (user?.tipo === 'comprador') {
      return [...publicLinks, { href: '/comprador/dashboard', label: 'Dashboard' }, { href: '/comprador/compras', label: 'Compras' }];
    }

    return publicLinks;
  };

  const getUserBadgeConfig = () => {
    switch (user?.tipo) {
      case 'admin': return { color: 'bg-purple-100 text-purple-700', icon: 'fa-shield-alt', label: 'Admin' };
      case 'produtor': return { color: 'bg-green-100 text-green-700', icon: 'fa-tractor', label: 'Produtor' };
      case 'comprador': return { color: 'bg-blue-100 text-blue-700', icon: 'fa-shopping-cart', label: 'Comprador' };
      default: return { color: 'bg-gray-100 text-gray-700', icon: 'fa-user', label: 'Usuário' };
    }
  };

  const badgeConfig = getUserBadgeConfig();
  const navLinks = getNavLinks();

  return (
    <nav className={`fixed w-full top-0 z-50 transition-all duration-300 ${isScrolled ? 'bg-white/95 backdrop-blur-md shadow-lg' : 'bg-white/90'}`}>
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo Profissional */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-700 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-green-500/50 transition-all duration-300 group-hover:scale-105">
                <span className="text-xl">🌾</span>
              </div>
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                <span className="text-[8px]">🌱</span>
              </div>
            </div>
            <div className="flex flex-col">
              <h1 className="text-xl font-bold bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent group-hover:from-green-700 group-hover:to-green-900 transition-all">
                AgroKongo
              </h1>
              <span className="text-[10px] text-gray-500 font-medium tracking-wider -mt-1">ANGOLA</span>
            </div>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            <div className="flex gap-6">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`relative font-medium transition-colors ${pathname === link.href ? 'text-green-600' : 'text-gray-700 hover:text-green-600'}`}
                >
                  {link.label}
                  {pathname === link.href && (
                    <motion.div layoutId="navbar-indicator" className="absolute -bottom-1 left-0 right-0 h-0.5 bg-green-600" />
                  )}
                </Link>
              ))}
            </div>

            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${badgeConfig.color}`}>
                  <i className={`fas ${badgeConfig.icon} text-sm`}></i>
                  <span className="text-sm font-medium">{user?.username}</span>
                </div>
                <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors font-medium">
                  <i className="fas fa-sign-out-alt mr-2"></i>Sair
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login" className="text-gray-700 hover:text-green-600 font-medium px-4 py-2">Entrar</Link>
                <Link href="/registro" className="bg-gradient-to-r from-green-600 to-green-700 text-white px-5 py-2.5 rounded-lg hover:from-green-700 hover:to-green-800 transition-all font-medium shadow-md hover:shadow-lg">
                  <i className="fas fa-user-plus mr-2"></i>Criar Conta
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button className="md:hidden p-2 text-gray-700 hover:text-green-600 transition-colors" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            <i className={`fas ${isMobileMenuOpen ? 'fa-times' : 'fa-bars'} text-2xl`}></i>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="md:hidden bg-white border-t border-gray-100">
            <div className="container mx-auto px-4 py-4 space-y-4">
              {navLinks.map((link) => (
                <Link key={link.href} href={link.href} onClick={() => setIsMobileMenuOpen(false)} className={`block py-2 font-medium ${pathname === link.href ? 'text-green-600' : 'text-gray-700 hover:text-green-600'}`}>
                  {link.label}
                </Link>
              ))}
              <div className="border-t border-gray-100 pt-4">
                {isAuthenticated ? (
                  <button onClick={() => { logout(); setIsMobileMenuOpen(false); }} className="block w-full text-center bg-red-500 text-white py-3 rounded-lg hover:bg-red-600 transition-colors font-medium">Sair</button>
                ) : (
                  <>
                    <Link href="/login" onClick={() => setIsMobileMenuOpen(false)} className="block w-full text-center border-2 border-green-600 text-green-600 py-3 rounded-lg hover:bg-green-50 transition-colors font-medium">Entrar</Link>
                    <Link href="/registro" onClick={() => setIsMobileMenuOpen(false)} className="block w-full text-center bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors font-medium mt-3">Criar Conta</Link>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}