# marketplace/views.py
"""
ViewSets para Marketplace (Produtos, Safras, Transações, Avaliações)
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F, Sum, Avg
from django.utils import timezone
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Produto, Safra, Transacao, HistoricoStatus, Avaliacao, TransactionStatus
from .serializers import (
    ProdutoSerializer,
    SafraSerializer, SafraCreateSerializer,
    TransacaoSerializer, TransacaoCreateSerializer, TransacaoStatusUpdateSerializer,
    AvaliacaoSerializer,
    HistoricoStatusSerializer
)


class ProdutoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Produtos (catálogo público).
    """
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'categoria']
    ordering_fields = ['nome', 'categoria']
    ordering = ['nome']
    pagination_class = None

    @extend_schema(
        summary='Listar produtos',
        description='Lista todos os produtos agrícolas do catálogo.',
        tags=['marketplace'],
        responses={200: ProdutoSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SafraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Safras (ofertas de produtores).
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['produto__nome', 'observacoes']
    ordering_fields = ['data_criacao', 'preco_por_unidade', 'quantidade_disponivel']
    ordering = ['-data_criacao']

    def get_queryset(self):
        queryset = Safra.objects.select_related('produto', 'produtor').all()

        produto_id = self.request.query_params.get('produto')
        produtor_id = self.request.query_params.get('produtor')
        status = self.request.query_params.get('status')
        preco_min = self.request.query_params.get('preco_min')
        preco_max = self.request.query_params.get('preco_max')

        if produto_id:
            queryset = queryset.filter(produto_id=produto_id)
        if produtor_id:
            queryset = queryset.filter(produtor_id=produtor_id)
        if status:
            queryset = queryset.filter(status=status)
        if preco_min:
            queryset = queryset.filter(preco_por_unidade__gte=preco_min)
        if preco_max:
            queryset = queryset.filter(preco_por_unidade__lte=preco_max)

        if not self.request.user.is_staff:
            queryset = queryset.filter(status='disponivel')

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return SafraCreateSerializer
        return SafraSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'vitrine']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.tipo != 'produtor':
            raise permissions.PermissionDenied('Apenas produtores podem criar safras.')

        if not self.request.user.perfil_completo:
            raise permissions.PermissionDenied('Complete o seu perfil KYC antes de publicar safras.')

        serializer.save(produtor=self.request.user)

    def perform_update(self, serializer):
        safra = self.get_object()
        if safra.produtor != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied('Apenas o produtor pode editar esta safra.')
        serializer.save()

    def perform_destroy(self, serializer):
        safra = self.get_object()
        if safra.produtor != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied('Apenas o produtor pode remover esta safra.')
        safra.delete()

    @extend_schema(
        summary='Comprar safra',
        description='Cria uma transação de compra para a safra especificada.',
        tags=['marketplace'],
        request=TransacaoCreateSerializer,
        responses={201: TransacaoSerializer},
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comprar(self, request, pk=None):
        """Endpoint para comprar uma safra (cria transação)"""
        safra = self.get_object()

        if safra.status != 'disponivel':
            return Response(
                {'error': 'Esta safra não está disponível para compra.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if safra.produtor == request.user:
            return Response(
                {'error': 'Não podes comprar a tua própria safra.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TransacaoCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        transacao = serializer.save()

        return Response(
            TransacaoSerializer(transacao, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary='Vitrine pública',
        description='Retorna as 20 safras mais recentes em destaque.',
        tags=['marketplace'],
        responses={200: SafraSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def vitrine(self, request):
        """Vitrine pública com safras em destaque"""
        safras = Safra.objects.filter(
            status='disponivel',
            quantidade_disponivel__gt=0
        ).select_related('produto', 'produtor', 'produtor__provincia').order_by('-data_criacao')[:20]

        serializer = SafraSerializer(safras, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary='Minhas safras',
        description='Lista safras do produtor autenticado.',
        tags=['marketplace'],
        responses={200: SafraSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def minhas(self, request):
        """Safras do produtor autenticado"""
        if request.user.tipo != 'produtor':
            return Response([], status=status.HTTP_200_OK)

        safras = Safra.objects.filter(produtor=request.user).order_by('-data_criacao')
        serializer = SafraSerializer(safras, many=True, context={'request': request})
        return Response(serializer.data)


class TransacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Transações (compras e vendas).
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['data_criacao', 'valor_total_pago', 'status']
    ordering = ['-data_criacao']

    def get_queryset(self):
        user = self.request.user
        return Transacao.ativas().filter(
            Q(comprador=user) | Q(vendedor=user)
        ).select_related('safra', 'comprador', 'vendedor')

    def get_serializer_class(self):
        if self.action == 'create':
            return TransacaoCreateSerializer
        elif self.action == 'update_status':
            return TransacaoStatusUpdateSerializer
        return TransacaoSerializer

    def perform_create(self, serializer):
        serializer.save(comprador=self.request.user)

    @extend_schema(
        summary='Atualizar status',
        description='Atualiza o status da transação com validação de transição.',
        tags=['marketplace'],
        request=TransacaoStatusUpdateSerializer,
        responses={200: TransacaoSerializer},
    )
    @action(detail=True, methods=['post'], url_path='atualizar-status')
    def update_status(self, request, pk=None):
        """Atualizar status da transação"""
        transacao = self.get_object()

        if request.user not in [transacao.comprador, transacao.vendedor] and not request.user.is_staff:
            raise permissions.PermissionDenied('Não tens permissão para alterar esta transação.')

        serializer = TransacaoStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        novo_status = serializer.validated_data['status']
        observacao = serializer.validated_data.get('observacao')

        if not transacao.pode_mudar_para(novo_status):
            return Response(
                {'error': f'Transição de {transacao.status} para {novo_status} não permitida.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        historico = transacao.mudar_status(
            novo_status,
            observacao=observacao,
            usuario=request.user
        )
        transacao.save()

        if novo_status == TransactionStatus.ENVIADO.value:
            transacao.calcular_janela_logistica()
            transacao.save(update_fields=['previsao_entrega'])

        return Response({
            'transacao': TransacaoSerializer(transacao, context={'request': request}).data,
            'historico': HistoricoStatusSerializer(historico).data if historico else None
        })

    @extend_schema(
        summary='Avaliar transação',
        description='Avalia transação concluída (1-5 estrelas).',
        tags=['marketplace'],
        request=AvaliacaoSerializer,
        responses={201: AvaliacaoSerializer},
    )
    @action(detail=True, methods=['post'])
    def avaliar(self, request, pk=None):
        """Avaliar transação concluída"""
        transacao = self.get_object()

        if request.user != transacao.comprador:
            raise permissions.PermissionDenied('Apenas o comprador pode avaliar esta transação.')

        if transacao.status != TransactionStatus.FINALIZADO.value:
            return Response(
                {'error': 'Apenas transações finalizadas podem ser avaliadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if hasattr(transacao, 'avaliacao') and transacao.avaliacao:
            return Response(
                {'error': 'Esta transação já foi avaliada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvaliacaoSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        avaliacao = serializer.save(transacao=transacao)

        vendedor = transacao.vendedor
        media = Avaliacao.objects.filter(
            transacao__vendedor=vendedor
        ).aggregate(media=Avg('nota'))['media']

        if media:
            vendedor.rating_vendedor = Decimal(str(media)).quantize(Decimal('0.01'))
            vendedor.vendas_concluidas = F('vendas_concluidas') + 1
            vendedor.save()

        return Response(AvaliacaoSerializer(avaliacao).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='compras')
    def minhas_compras(self, request):
        """Apenas compras do usuário atual"""
        transacoes = self.get_queryset().filter(comprador=request.user)
        serializer = TransacaoSerializer(transacoes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='vendas')
    def minhas_vendas(self, request):
        """Apenas vendas do usuário atual"""
        transacoes = self.get_queryset().filter(vendedor=request.user)
        serializer = TransacaoSerializer(transacoes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='estatisticas')
    def estatisticas(self, request):
        """Estatísticas financeiras do usuário"""
        user = request.user

        compras = Transacao.ativas().filter(comprador=user)
        total_compras = compras.aggregate(total=Sum('valor_total_pago'))['total'] or Decimal('0.00')

        vendas = Transacao.ativas().filter(vendedor=user)
        total_vendas = vendas.aggregate(total=Sum('valor_liquido_vendedor'))['total'] or Decimal('0.00')

        stats = {
            'total_compras': str(total_compras),
            'total_vendas': str(total_vendas),
            'compras_pendentes': compras.filter(status__in=['pendente', 'pendente_pagamento']).count(),
            'vendas_pendentes': vendas.filter(status__in=['pendente', 'analise']).count(),
            'avaliacoes_recebidas': Avaliacao.objects.filter(
                transacao__vendedor=user
            ).count(),
        }

        return Response(stats)


class AvaliacaoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Avaliações (apenas leitura pública)"""
    queryset = Avaliacao.objects.select_related('transacao', 'transacao__vendedor').all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [permissions.AllowAny]
    ordering = ['-data_criacao']

    def get_queryset(self):
        queryset = super().get_queryset()
        vendedor_id = self.request.query_params.get('vendedor')

        if vendedor_id:
            queryset = queryset.filter(transacao__vendedor_id=vendedor_id)

        return queryset