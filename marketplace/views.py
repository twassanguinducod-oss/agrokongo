# marketplace/views.py
from rest_framework import viewsets, status, permissions, filters, serializers # ✅ Importado serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Categoria, Produto, Safra, Reserva, Pagamento
from .filters import SafraFilter
from .serializers import (
    CategoriaSerializer,
    ProdutoSerializer,
    SafraSerializer, SafraListSerializer, SafraDetalheSerializer,
    ReservaSerializer,
    PagamentoSerializer,
)


class SafraViewSet(viewsets.ModelViewSet):
    """ViewSet para safras com proteção de dados do produtor."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # 🛡️ SEGURANÇA: Aberto apenas para leitura
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SafraFilter
    search_fields = ['titulo', 'descricao', 'produto__nome']
    ordering_fields = ['preco_unitario', 'quantidade', 'data_criacao']
    ordering = ['-data_criacao']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False): return Safra.objects.none()
        queryset = Safra.objects.all()
        if self.action == 'list': queryset = queryset.filter(status='active')
        return queryset.select_related('produtor', 'produto').prefetch_related('imagens')

    def get_serializer_class(self):
        if self.action == 'list': return SafraListSerializer
        elif self.action == 'retrieve': return SafraDetalheSerializer
        return SafraSerializer


class ReservaViewSet(viewsets.ModelViewSet):
    """ViewSet para reservas com otimização de queries e tratamento de erro correto."""
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated] # 🛡️ Garantido pelo settings mas explícito aqui
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['safra', 'comprador', 'status']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False): return Reserva.objects.none()
        user = self.request.user
        # ✅ N+1 Query Fix: select_related nos dados do comprador e safra
        base_qs = Reserva.objects.select_related('comprador', 'safra', 'safra__produtor', 'safra__produto')
        
        if user.tipo == 'comprador': return base_qs.filter(comprador=user)
        elif user.tipo == 'produtor': return base_qs.filter(safra__produtor=user)
        return base_qs.all()

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.comprador != request.user and reserva.safra.produtor != request.user:
            return Response({'error': 'Não autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            reserva.cancelar(usuario=request.user)
            return Response({'success': True, 'message': 'Reserva cancelada com sucesso.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def confirmar_rececao(self, request, pk=None):
        reserva = self.get_object()
        if reserva.comprador != request.user:
            return Response({'error': 'Apenas o comprador pode confirmar.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            reserva.confirmar_rececao()
            return Response({'success': True, 'message': 'Receção confirmada. Aguardando liberação de pagamento.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def liberar_pagamento(self, request, pk=None):
        reserva = self.get_object()
        try:
            reserva.liberar_pagamento(admin=request.user)
            return Response({'success': True, 'message': 'Pagamento liberado para o produtor.', 'status': reserva.status})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PagamentoViewSet(viewsets.ModelViewSet):
    """ViewSet para pagamentos com proteção contra upload duplicado e validação correta."""
    serializer_class = PagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        reserva = serializer.validated_data.get('reserva')
        if Pagamento.objects.filter(reserva=reserva).exists():
            # ✅ CORREÇÃO: Usar ValidationError para retornar 400 Bad Request
            raise serializers.ValidationError({'reserva': 'Já existe um pagamento para esta reserva.'})
        if reserva.status not in ['pendente', 'confirmada']:
            raise serializers.ValidationError({'reserva': 'Esta reserva não permite mais pagamentos.'})
        serializer.save()

    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAdminUser])
    def aprovar(self, request, pk=None):
        pagamento = self.get_object()
        pagamento.aprovar(validador=request.user)
        return Response({'success': True, 'status': pagamento.status})
