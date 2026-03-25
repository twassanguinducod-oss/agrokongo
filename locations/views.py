# locations/views.py
"""
ViewSets para Localização (Províncias e Municípios de Angola)
"""
from rest_framework import viewsets, permissions, filters
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Provincia, Municipio
from .serializers import ProvinciaSerializer, MunicipioSerializer, ProvinciaListSerializer


class ProvinciaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Províncias (apenas leitura).

    Endpoints:
    - GET /api/locations/provincias/ - Listar todas
    - GET /api/locations/provincias/{id}/ - Detalhes com municípios
    """
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['nome']
    ordering = ['nome']

    @extend_schema(
        summary='Listar províncias',
        description='Lista todas as províncias de Angola.',
        tags=['locations'],
        responses={200: ProvinciaListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProvinciaListSerializer
        return ProvinciaSerializer


class MunicipioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Municípios (apenas leitura).

    Endpoints:
    - GET /api/locations/municipios/ - Listar todos
    - GET /api/locations/municipios/?provincia=1 - Filtrar por província
    - GET /api/locations/municipios/{id}/ - Detalhes
    """
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'provincia__nome']
    ordering_fields = ['nome', 'provincia__nome']
    ordering = ['provincia__nome', 'nome']

    @extend_schema(
        summary='Listar municípios',
        description='Lista municípios, opcionalmente filtrados por província.',
        tags=['locations'],
        parameters=[
            OpenApiParameter(
                name='provincia',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filtrar por ID da província'
            ),
        ],
        responses={200: MunicipioSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        provincia_id = self.request.query_params.get('provincia')

        if provincia_id:
            queryset = queryset.filter(provincia_id=provincia_id)

        return queryset
