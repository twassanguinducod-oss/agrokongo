from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProdutoViewSet, SafraViewSet, TransacaoViewSet, AvaliacaoViewSet

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'safras', SafraViewSet, basename='safra')
router.register(r'transacoes', TransacaoViewSet, basename='transacao')
router.register(r'avaliacoes', AvaliacaoViewSet, basename='avaliacao')

urlpatterns = [
    path('', include(router.urls)),
]