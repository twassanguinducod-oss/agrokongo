# core/urls.py (SUBSTITUIR TODAS AS ROTAS)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificacaoViewSet,
    MensagemViewSet,
    AlertaPreferenciaViewSet,
    LogAuditoriaViewSet,
    PaginaSobreViewSet,
    ContatoViewSet,
    InfoContatoViewSet,
)

router = DefaultRouter()
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')
router.register(r'mensagens', MensagemViewSet, basename='mensagem')
router.register(r'alertas', AlertaPreferenciaViewSet, basename='alerta')
router.register(r'logs', LogAuditoriaViewSet, basename='log')

# 🆕 SPRINT 8: Conteúdo Estático
router.register(r'sobre', PaginaSobreViewSet, basename='sobre')
router.register(r'contato', ContatoViewSet, basename='contato')
router.register(r'info-contato', InfoContatoViewSet, basename='info-contato')

urlpatterns = [
    path('', include(router.urls)),
]