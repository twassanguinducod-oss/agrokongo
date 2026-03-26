from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProvinciaViewSet, MunicipioViewSet

router = DefaultRouter()
router.register(r'provincias', ProvinciaViewSet, basename='provincia')
router.register(r'municipios', MunicipioViewSet, basename='municipio')

urlpatterns = [
    path('', include(router.urls)),
]