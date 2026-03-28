# core/views.py
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notificacao, Mensagem, AlertaPreferencia, LogAuditoria
from .serializers import (
    NotificacaoSerializer,
    NotificacaoCreateSerializer,
    MensagemSerializer,
    MensagemCreateSerializer,
    AlertaPreferenciaSerializer,
    LogAuditoriaSerializer,
)


# ===========================================
# NOTIFICAÇÃO VIEWSET
# ===========================================
class NotificacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para notificações"""
    serializer_class = NotificacaoSerializer
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

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificacaoCreateSerializer
        return NotificacaoSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def minhas(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def marcar_lida(self, request, pk=None):
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save(update_fields=['lida'])
        return Response({'success': True, 'message': 'Notificação marcada como lida'}, status=status.HTTP_200_OK)


# ===========================================
# MENSAGEM VIEWSET
# ===========================================
class MensagemViewSet(viewsets.ModelViewSet):
    """ViewSet para mensagens de suporte"""
    serializer_class = MensagemSerializer
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

    def get_permissions(self):
        if self.action == 'responder':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def minhas(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def responder(self, request, pk=None):
        mensagem = self.get_object()
        resposta = request.data.get('resposta', '')
        mensagem.resposta = resposta
        mensagem.respondido_por = request.user
        mensagem.status = 'respondido'
        mensagem.save()
        return Response({'success': True, 'message': 'Mensagem respondida'}, status=status.HTTP_200_OK)


# ===========================================
# ALERTA PREFERÊNCIA VIEWSET
# ===========================================
class AlertaPreferenciaViewSet(viewsets.ModelViewSet):
    """ViewSet para alertas de preferência"""
    serializer_class = AlertaPreferenciaSerializer
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

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# ===========================================
# LOG AUDITORIA VIEWSET
# ===========================================
class LogAuditoriaViewSet(viewsets.ModelViewSet):
    """ViewSet para logs de auditoria (Apenas Admin)"""
    serializer_class = LogAuditoriaSerializer
    permission_classes = [permissions.IsAdminUser]  # ✅ CLASSE (sem parênteses)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['acao', 'tabela_afetada', 'usuario']
    ordering_fields = ['data_criacao']
    ordering = ['-data_criacao']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LogAuditoria.objects.none()
        return LogAuditoria.objects.all()
