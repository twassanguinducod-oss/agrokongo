# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, LevantamentoViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'levantamentos', LevantamentoViewSet, basename='levantamento')

urlpatterns = [
    path('', include(router.urls)),
]