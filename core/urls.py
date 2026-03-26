from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificacaoViewSet, MensagemViewSet, AlertaPreferenciaViewSet, LogAuditoriaViewSet

router = DefaultRouter()
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')
router.register(r'mensagens', MensagemViewSet, basename='mensagem')
router.register(r'alertas', AlertaPreferenciaViewSet, basename='alerta')
router.register(r'logs', LogAuditoriaViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]