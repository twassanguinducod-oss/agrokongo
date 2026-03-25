# agrokongo/views.py
from django.http import JsonResponse, HttpResponse
from django.utils import timezone  # ← IMPORTANTE: Importar timezone do Django
import json


def index(request):
    """
    Página inicial da API AgroKongo.
    Retorna JSON para APIs ou HTML simples para navegador.
    """
    # Se for requisição API (Accept: application/json), retorna JSON
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'online',
            'project': 'AgroKongo API',
            'version': '1.0.0',
            'docs': {
                'admin': '/admin/',
                'api_token': '/api/token/',
                'api_docs': '/api/schema/'
            },
            'endpoints': {
                'auth': '/api/token/',
                'accounts': '/api/accounts/',
                'marketplace': '/api/marketplace/',
                'locations': '/api/locations/',
                'core': '/api/core/'
            }
        })

    # Se for navegador, retorna HTML simples
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="pt-AO">
    <head>
        <meta charset="UTF-8">
        <title>🌾 AgroKongo API</title>
        <style>
            body { font-family: system-ui, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f8f9fa; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
            h1 { color: #2E7D32; margin-bottom: 20px; }
            .endpoint { background: #e8f5e9; padding: 10px 15px; border-radius: 6px; margin: 8px 0; font-family: monospace; }
            a { color: #1976D2; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .status { display: inline-block; padding: 4px 12px; background: #4CAF50; color: white; border-radius: 20px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🌾 AgroKongo API</h1>
            <p><span class="status">● Online</span></p>
            <p><strong>Backend:</strong> Django 6.0.3 + Django REST Framework</p>
            <p><strong>Banco:</strong> PostgreSQL</p>
            <p><strong>Autenticação:</strong> JWT (SimpleJWT)</p>

            <h3>🔗 Endpoints Disponíveis:</h3>
            <div class="endpoint"><a href="/admin/">/admin/</a> — Painel Administrativo</div>
            <div class="endpoint">/api/token/ — Obter Token JWT</div>
            <div class="endpoint">/api/token/refresh/ — Refresh Token</div>
            <div class="endpoint">/api/accounts/ — Gestão de Usuários</div>
            <div class="endpoint">/api/marketplace/ — Produtos, Safras, Transações</div>
            <div class="endpoint">/api/locations/ — Províncias e Municípios</div>
            <div class="endpoint">/api/core/ — Notificações, Logs, Chat</div>

            <h3>📚 Documentação:</h3>
            <p>Em desenvolvimento. Em breve: Swagger/OpenAPI em <code>/api/schema/</code></p>

            <hr>
            <p><small>AgroKongo © 2026 — Marketplace Agrícola para Angola 🇦🇴</small></p>
        </div>
    </body>
    </html>
    """)


def health_check(request):
    """Endpoint para health check (Kubernetes, load balancers, etc.)"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': str(timezone.now())  # ← Agora timezone está importado
    })