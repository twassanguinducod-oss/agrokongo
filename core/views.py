# core/views.py
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Notificacao, Mensagem, AlertaPreferencia, LogAuditoria
from .serializers import (
    NotificacaoSerializer,
    NotificacaoBadgeSerializer,
    MensagemSerializer,
    MensagemCreateSerializer,
    AlertaPreferenciaSerializer,
    LogAuditoriaSerializer,
)


# ===========================================
# NOTIFICAÇÃO VIEWSET
# ===========================================
class NotificacaoViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lida', 'tipo']
    ordering_fields = ['data_criacao']
    ordering = ['-data_criacao']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notificacao.objects.none()
        if self.request.user.is_authenticated:
            return Notificacao.objects.filter(usuario=self.request.user)
        return Notificacao.objects.none()

    # ===========================================
    # 🆕 SPRINT 7: BADGE DE NOTIFICAÇÕES (Cláudio)
    # ===========================================
    @action(detail=False, methods=['get'], url_path='nao-lidas/count')
    def nao_lidas_count(self, request):
        """Retorna contagem de notificações não lidas (para badge)"""
        count = Notificacao.objects.filter(
            usuario=request.user,
            lida=False
        ).count()

        return Response({
            'nao_lidas': count,
            'total': Notificacao.objects.filter(usuario=request.user).count()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def minhas(self, request):
        """Lista notificações do usuário autenticado"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def marcar_lida(self, request, pk=None):
        """Marca notificação como lida"""
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.data_leitura = timezone.now()
        notificacao.save(update_fields=['lida', 'data_leitura'])
        return Response({'success': True, 'message': 'Notificação marcada como lida'})

    @action(detail=False, methods=['post'], url_path='marcar-todas-lidas')
    def marcar_todas_lidas(self, request):
        """Marca TODAS as notificações como lidas"""
        count = Notificacao.objects.filter(
            usuario=request.user,
            lida=False
        ).update(lida=True, data_leitura=timezone.now())
        return Response({
            'success': True,
            'message': f'{count} notificações marcadas como lidas'
        })


# ===========================================
# MENSAGEM VIEWSET
# ===========================================
class MensagemViewSet(viewsets.ModelViewSet):
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'tipo']
    ordering_fields = ['data_criacao']
    ordering = ['-data_criacao']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Mensagem.objects.none()
        if not self.request.user.is_authenticated:
            return Mensagem.objects.none()
        if self.request.user.tipo == 'admin':
            return Mensagem.objects.all()
        return Mensagem.objects.filter(usuario=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return MensagemCreateSerializer
        return MensagemSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def minhas(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def responder(self, request, pk=None):
        mensagem = self.get_object()
        resposta = request.data.get('resposta', '')
        mensagem.resposta = resposta
        mensagem.respondido_por = request.user
        mensagem.status = 'respondido'
        mensagem.save()
        return Response({'success': True, 'message': 'Mensagem respondida'})


# ===========================================
# ALERTA PREFERÊNCIA VIEWSET
# ===========================================
class AlertaPreferenciaViewSet(viewsets.ModelViewSet):
    serializer_class = AlertaPreferenciaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ativo', 'produto']
    ordering_fields = ['data_criacao']
    ordering = ['-data_criacao']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AlertaPreferencia.objects.none()
        if self.request.user.is_authenticated:
            return AlertaPreferencia.objects.filter(usuario=self.request.user)
        return AlertaPreferencia.objects.none()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# ===========================================
# LOG AUDITORIA VIEWSET
# ===========================================
class LogAuditoriaViewSet(viewsets.ModelViewSet):
    serializer_class = LogAuditoriaSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['acao', 'tabela_afetada', 'usuario']
    ordering_fields = ['data_criacao']
    ordering = ['-data_criacao']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LogAuditoria.objects.none()
        return LogAuditoria.objects.all()
