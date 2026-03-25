from rest_framework import serializers
from .models import Notificacao, Mensagem, LogAuditoria, AlertaPreferencia
from accounts.serializers import UsuarioSerializer
from marketplace.serializers import ProdutoSerializer, TransacaoSerializer


class NotificacaoSerializer(serializers.ModelSerializer):
    """Serializer para Notificações"""

    class Meta:
        model = Notificacao
        fields = ['id', 'usuario', 'mensagem', 'link', 'lida', 'data_criacao']
        read_only_fields = ['id', 'usuario', 'data_criacao']


class NotificacaoMarkAsReadSerializer(serializers.Serializer):
    """Serializer para marcar notificação como lida"""
    ids = serializers.ListField(child=serializers.IntegerField(), required=True)


class MensagemSerializer(serializers.ModelSerializer):
    """Serializer para Mensagens (Chat)"""
    remetente_nome = serializers.CharField(source='remetente.username', read_only=True)
    destinatario_nome = serializers.CharField(source='destinatario.username', read_only=True)

    class Meta:
        model = Mensagem
        fields = [
            'id', 'transacao', 'remetente', 'destinatario',
            'remetente_nome', 'destinatario_nome', 'conteudo', 'data_envio', 'lida'
        ]
        read_only_fields = ['id', 'data_envio', 'remetente']

    def validate(self, attrs):
        request = self.context.get('request')
        transacao = attrs.get('transacao')

        if request and transacao:
            # Apenas participantes da transação podem enviar mensagens
            if request.user not in [transacao.comprador, transacao.vendedor]:
                raise serializers.ValidationError('Apenas participantes da transação podem enviar mensagens.')

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        transacao = validated_data['transacao']

        # Define destinatário automaticamente
        if request.user == transacao.comprador:
            validated_data['destinatario'] = transacao.vendedor
        else:
            validated_data['destinatario'] = transacao.comprador

        validated_data['remetente'] = request.user
        return super().create(validated_data)


class LogAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer para Logs de Auditoria (Admin)"""
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = LogAuditoria
        fields = ['id', 'usuario', 'usuario_nome', 'acao', 'detalhes', 'ip', 'data_criacao']
        read_only_fields = ['id', 'data_criacao']


class AlertaPreferenciaSerializer(serializers.ModelSerializer):
    """Serializer para Alertas de Preferência"""
    produto = ProdutoSerializer(read_only=True)

    class Meta:
        model = AlertaPreferencia
        fields = ['id', 'usuario', 'produto', 'data_criacao']
        read_only_fields = ['id', 'usuario', 'data_criacao']

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)