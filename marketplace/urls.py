# marketplace/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet,
    ProdutoViewSet,
    SafraViewSet,
    ImagemSafraViewSet,
    ReservaViewSet,
    PagamentoViewSet,
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'safras', SafraViewSet, basename='safra')
router.register(r'imagens', ImagemSafraViewSet, basename='imagem-safra')
router.register(r'reservas', ReservaViewSet, basename='reserva')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')

urlpatterns = [
    path('', include(router.urls)),
]