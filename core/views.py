# core/views.py
"""
ViewSets para Core (Notificações, Mensagens, Logs, Alertas)
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Notificacao, Mensagem, LogAuditoria, AlertaPreferencia
from .serializers import (
    NotificacaoSerializer, NotificacaoMarkAsReadSerializer,
    MensagemSerializer,
    LogAuditoriaSerializer,
    AlertaPreferenciaSerializer
)


class NotificacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Notificações do usuário.
    """
    serializer_class = NotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-data_criacao']

    def get_queryset(self):
        return Notificacao.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @extend_schema(
        summary='Marcar notificações como lidas',
        description='Marca múltiplas notificações como lidas.',
        tags=['core'],
        request=NotificacaoMarkAsReadSerializer,
        responses={200: {'type': 'object', 'properties': {'atualizadas': {'type': 'integer'}}}},
    )
    @action(detail=False, methods=['post'], url_path='marcar-lidas')
    def mark_as_read(self, request):
        """Marcar múltiplas notificações como lidas"""
        serializer = NotificacaoMarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        atualizadas = Notificacao.objects.filter(
            usuario=request.user,
            id__in=ids
        ).update(lida=True)

        return Response({'atualizadas': atualizadas})

    @action(detail=False, methods=['get'], url_path='nao-lidas/count')
    def count_unread(self, request):
        """Contagem rápida de notificações não lidas"""
        count = Notificacao.objects.filter(
            usuario=request.user,
            lida=False
        ).count()
        return Response({'count': count})


class MensagemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Mensagens (Chat por transação).
    """
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['data_envio']

    def get_queryset(self):
        transacao_id = self.request.query_params.get('transacao')

        if transacao_id:
            return Mensagem.objects.filter(
                transacao_id=transacao_id,
                transacao__in=[
                    t.id for t in self.request.user.compras.all() | self.request.user.vendas.all()
                ]
            )

        return Mensagem.objects.filter(
            Q(remetente=self.request.user) | Q(destinatario=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(remetente=self.request.user)

    @action(detail=False, methods=['post'], url_path='marcar-lidas')
    def mark_as_read(self, request):
        """Marcar mensagens recebidas como lidas"""
        transacao_id = request.data.get('transacao_id')

        if not transacao_id:
            return Response(
                {'error': 'transacao_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        atualizadas = Mensagem.objects.filter(
            destinatario=request.user,
            transacao_id=transacao_id,
            lida=False
        ).update(lida=True)

        return Response({'atualizadas': atualizadas})


class AlertaPreferenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Alertas de Preferência de Produto.
    """
    serializer_class = AlertaPreferenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AlertaPreferencia.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Logs de Auditoria (APENAS ADMIN).
    """
    queryset = LogAuditoria.objects.select_related('usuario').all()
    serializer_class = LogAuditoriaSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['acao', 'detalhes', 'ip']
    ordering_fields = ['data_criacao']
    ordering = ['-data_criacao']
