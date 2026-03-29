# marketplace/views.py
from rest_framework import viewsets, status, permissions, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from .models import Categoria, Produto, Safra, Reserva, Pagamento, ImagemSafra
from .filters import SafraFilter
from .serializers import (
    CategoriaSerializer,
    ProdutoSerializer,
    SafraSerializer,
    SafraListSerializer,
    SafraDetalheSerializer,
    ReservaSerializer,
    ReservaListSerializer,
    ReservaDetalheSerializer,
    PagamentoSerializer,
    ImagemSafraSerializer,
)


# ===========================================
# CATEGORIA VIEWSET
# ===========================================
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.filter(ativa=True)
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['nome']
    ordering = ['nome']


# ===========================================
# PRODUTO VIEWSET
# ===========================================
class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['nome']
    ordering = ['nome']


# ===========================================
# SAFRA VIEWSET
# ===========================================
class SafraViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SafraFilter
    search_fields = ['titulo', 'descricao', 'produto__nome']
    ordering_fields = ['preco_unitario', 'quantidade', 'data_criacao']
    ordering = ['-data_criacao']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Safra.objects.none()
        queryset = Safra.objects.all()
        if self.action == 'list':
            queryset = queryset.filter(status='active')
        return queryset.select_related('produtor', 'produto').prefetch_related('imagens')

    def get_serializer_class(self):
        if self.action == 'list':
            return SafraListSerializer
        elif self.action == 'retrieve':
            return SafraDetalheSerializer
        return SafraSerializer

    def perform_create(self, serializer):
        if self.request.user.tipo != 'produtor':
            raise PermissionError('Apenas produtores podem criar safras')
        serializer.save(produtor=self.request.user)

    @action(detail=True, methods=['post'])
    def favoritar(self, request, pk=None):
        safra = self.get_object()
        safra.favoritos = getattr(safra, 'favoritos', 0) + 1
        safra.save(update_fields=['favoritos'])
        return Response({'success': True, 'favoritos': safra.favoritos})

    @action(detail=True, methods=['post'])
    def visualizar(self, request, pk=None):
        safra = self.get_object()
        safra.visualizacoes = getattr(safra, 'visualizacoes', 0) + 1
        safra.save(update_fields=['visualizacoes'])
        return Response({'success': True, 'visualizacoes': safra.visualizacoes})


# ===========================================
# IMAGEM SAFRA VIEWSET
# ===========================================
class ImagemSafraViewSet(viewsets.ModelViewSet):
    queryset = ImagemSafra.objects.all()
    serializer_class = ImagemSafraSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ImagemSafra.objects.none()
        safra_id = self.request.query_params.get('safra', None)
        if safra_id:
            return ImagemSafra.objects.filter(safra_id=safra_id)
        return ImagemSafra.objects.all()

    def perform_create(self, serializer):
        safra = serializer.validated_data.get('safra')
        if safra and safra.produtor != self.request.user:
            raise PermissionError('Apenas o produtor pode adicionar imagens')
        serializer.save()


# ===========================================
# 🆕 RESERVA VIEWSET (SPRINT 7 - 13 PTS)
# ===========================================
class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para reservas/compras.

    Endpoints Sprint 7:
    - GET /api/marketplace/reservas/minhas-encomendas/ (Minhas encomendas)
    - GET /api/marketplace/reservas/{id}/detalhes/ (Detalhes da encomenda)
    """
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['safra', 'comprador', 'status']
    ordering_fields = ['data_reserva', 'preco_total']
    ordering = ['-data_reserva']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Reserva.objects.none()

        user = self.request.user
        base_qs = Reserva.objects.select_related(
            'comprador', 'safra', 'safra__produtor', 'safra__produto'
        ).prefetch_related('pagamento')

        if user.tipo == 'comprador':
            return base_qs.filter(comprador=user)
        elif user.tipo == 'produtor':
            return base_qs.filter(safra__produtor=user)
        return base_qs.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservaListSerializer
        elif self.action in ['retrieve', 'detalhes_encomenda', 'minhas_encomendas']:
            return ReservaDetalheSerializer
        return ReservaSerializer

    # ===========================================
    # 🆕 SPRINT 7: MINHAS ENCOMENDAS (8 PTS)
    # ===========================================
    @action(detail=False, methods=['get'], url_path='minhas-encomendas')
    def minhas_encomendas(self, request):
        """
        Lista TODAS as encomendas do comprador autenticado.
        Endpoint dedicado para o comprador ver seu histórico.
        """
        if request.user.tipo != 'comprador':
            return Response(
                {'error': 'Apenas compradores podem acessar este endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        encomendas = Reserva.objects.filter(
            comprador=request.user
        ).select_related(
            'safra', 'safra__produto', 'safra__produtor'
        ).prefetch_related('pagamento').order_by('-data_reserva')

        serializer = ReservaDetalheSerializer(encomendas, many=True)

        # Contagem por status (para badges/filtros)
        stats = {
            'total': encomendas.count(),
            'pendente': encomendas.filter(status='pendente').count(),
            'confirmada': encomendas.filter(status='confirmada').count(),
            'paga': encomendas.filter(status='paga').count(),
            'recebida': encomendas.filter(status='recebida').count(),
            'concluida': encomendas.filter(status='concluida').count(),
            'cancelada': encomendas.filter(status='cancelada').count(),
        }

        return Response({
            'encomendas': serializer.data,
            'stats': stats
        }, status=status.HTTP_200_OK)

    # ===========================================
    # 🆕 SPRINT 7: DETALHES DA ENCOMENDA (5 PTS)
    # ===========================================
    @action(detail=True, methods=['get'], url_path='detalhes')
    def detalhes_encomenda(self, request, pk=None):
        """
        Detalhes COMPLETOS de uma encomenda específica.
        Inclui dados do produtor, produto e pagamento.
        """
        reserva = self.get_object()

        # Verificar permissão (apenas comprador ou produtor da safra)
        if request.user.tipo == 'comprador' and reserva.comprador != request.user:
            return Response(
                {'error': 'Não autorizado a ver esta encomenda.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user.tipo == 'produtor' and reserva.safra.produtor != request.user:
            return Response(
                {'error': 'Não autorizado a ver esta encomenda.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReservaDetalheSerializer(reserva)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ===========================================
    # ENDPOINTS EXISTENTES (MANTER)
    # ===========================================
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
            return Response({'success': True, 'message': 'Receção confirmada.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def liberar_pagamento(self, request, pk=None):
        reserva = self.get_object()
        try:
            reserva.liberar_pagamento(admin=request.user)
            return Response({'success': True, 'message': 'Pagamento liberado.', 'status': reserva.status})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ===========================================
# PAGAMENTO VIEWSET
# ===========================================
class PagamentoViewSet(viewsets.ModelViewSet):
    serializer_class = PagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reserva', 'status', 'metodo']
    ordering_fields = ['data_criacao', 'valor']
    ordering = ['-data_criacao']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Pagamento.objects.none()

        user = self.request.user
        if user.tipo == 'comprador':
            return Pagamento.objects.filter(reserva__comprador=user)
        elif user.tipo == 'produtor':
            return Pagamento.objects.filter(reserva__safra__produtor=user)
        return Pagamento.objects.all()

    def perform_create(self, serializer):
        reserva = serializer.validated_data.get('reserva')
        if Pagamento.objects.filter(reserva=reserva).exists():
            raise serializers.ValidationError({'reserva': 'Já existe um pagamento para esta reserva.'})
        if reserva.status not in ['pendente', 'confirmada']:
            raise serializers.ValidationError({'reserva': 'Esta reserva não permite mais pagamentos.'})
        if reserva.comprador != self.request.user:
            raise PermissionError('Apenas o comprador pode fazer upload do comprovativo')
        serializer.save()

    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAdminUser])
    def aprovar(self, request, pk=None):
        pagamento = self.get_object()
        pagamento.aprovar(validador=request.user)

        # Criar notificações
        from core.models import Notificacao
        Notificacao.objects.create(
            usuario=pagamento.reserva.comprador,
            titulo='Pagamento Aprovado ✅',
            mensagem=f'Seu pagamento da reserva #{pagamento.reserva.id} foi aprovado.',
            tipo='sucesso'
        )
        Notificacao.objects.create(
            usuario=pagamento.reserva.safra.produtor,
            titulo='Pagamento Recebido 💰',
            mensagem=f'Pagamento da reserva #{pagamento.reserva.id} foi aprovado.',
            tipo='info'
        )

        return Response({'success': True, 'status': pagamento.status})

    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAdminUser])
    def rejeitar(self, request, pk=None):
        pagamento = self.get_object()
        motivo = request.data.get('motivo', 'Motivo não especificado')
        pagamento.rejeitar(validador=request.user, motivo=motivo)

        # Criar notificação
        from core.models import Notificacao
        Notificacao.objects.create(
            usuario=pagamento.reserva.comprador,
            titulo='Pagamento Rejeitado ❌',
            mensagem=f'Seu pagamento foi rejeitado. Motivo: {motivo}',
            tipo='erro'
        )

        return Response({'success': True, 'status': pagamento.status, 'motivo': motivo})