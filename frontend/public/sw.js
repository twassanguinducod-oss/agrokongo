// Service Worker para AgroKongo - Implementação Nativa e Segura
const CACHE_NAME = 'agrokongo-v1';
const OFFLINE_URL = '/offline.html';

// Recursos estáticos para cache
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/offline.html',
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Cache aberto durante instalação');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Ativação e limpeza de caches antigos + registro de background sync
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME)
            .map((name) => caches.delete(name))
        );
      })
      .then(() => self.clients.claim())
  );
});

// Background Sync para ações offline
self.addEventListener('sync', (event) => {
  console.log('[SW] Background Sync registrado:', event.tag);
  
  if (event.tag === 'sync-notificacoes') {
    event.waitUntil(syncNotificacoes());
  } else if (event.tag === 'sync-mensagens') {
    event.waitUntil(syncMensagens());
  } else if (event.tag === 'sync-transacoes') {
    event.waitUntil(syncTransacoes());
  }
});

// Funções de sync
async function syncNotificacoes() {
  try {
    // Buscar notificações não lidas quando online
    const response = await fetch('/api/notificacoes', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('[SW] Notificações sincronizadas:', data);
    }
  } catch (error) {
    console.error('[SW] Erro ao sincronizar notificações:', error);
    throw error; // Retry automático
  }
}

async function syncMensagens() {
  try {
    // Enviar mensagens pendentes quando online
    const pendingMessages = await getPendingMessagesFromIndexedDB();
    
    for (const message of pendingMessages) {
      await fetch('/api/mensagens/enviar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });
      
      await removeMessageFromIndexedDB(message.id);
    }
    
    console.log('[SW] Mensagens sincronizadas:', pendingMessages.length);
  } catch (error) {
    console.error('[SW] Erro ao sincronizar mensagens:', error);
    throw error;
  }
}

async function syncTransacoes() {
  try {
    // Sincronizar estado de transações pendentes
    const response = await fetch('/api/transacoes/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      console.log('[SW] Transações sincronizadas');
    }
  } catch (error) {
    console.error('[SW] Erro ao sincronizar transações:', error);
    throw error;
  }
}

// IndexedDB helpers para mensagens pendentes
function getPendingMessagesFromIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('agrokongo-db', 1);
    
    request.onerror = () => reject(request.error);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending_messages')) {
        db.createObjectStore('pending_messages', { keyPath: 'id' });
      }
    };
    
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction(['pending_messages'], 'readonly');
      const store = transaction.objectStore('pending_messages');
      const getAllRequest = store.getAll();
      
      getAllRequest.onsuccess = () => resolve(getAllRequest.result || []);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };
  });
}

function removeMessageFromIndexedDB(id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('agrokongo-db', 1);
    
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction(['pending_messages'], 'readwrite');
      const store = transaction.objectStore('pending_messages');
      store.delete(id);
      
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    };
  });
}

// Interceptação de requisições - Estratégia: Cache First, Network Fallback
self.addEventListener('fetch', (event) => {
  // Ignorar requisições que não são GET
  if (event.request.method !== 'GET') {
    return;
  }

  // Ignorar URLs externas e API
  const url = new URL(event.request.url);
  if (url.origin !== location.origin || url.pathname.startsWith('/api/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }

        return fetch(event.request)
          .then((networkResponse) => {
            // Não cachear respostas inválidas
            if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
              return networkResponse;
            }

            // Clonar a resposta para cache
            const responseToCache = networkResponse.clone();

            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return networkResponse;
          })
          .catch(() => {
            // Fallback para página offline se for navegação
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL);
            }
          });
      })
  );
});
