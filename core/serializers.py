# core/serializers.py
from rest_framework import serializers
from .models import Notificacao, Mensagem, AlertaPreferencia, LogAuditoria


# ===========================================
# NOTIFICAÇÃO
# ===========================================
class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = [
            'id', 'usuario', 'titulo', 'mensagem', 'tipo',
            'lida', 'data_criacao', 'data_leitura'
        ]
        read_only_fields = ['usuario', 'data_criacao', 'data_leitura']


class NotificacaoBadgeSerializer(serializers.Serializer):
    """Serializer para badge de notificações"""
    nao_lidas = serializers.IntegerField()
    total = serializers.IntegerField()


# ===========================================
# MENSAGEM
# ===========================================
class MensagemSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)
    respondido_por_nome = serializers.CharField(source='respondido_por.username', read_only=True)

    class Meta:
        model = Mensagem
        fields = [
            'id', 'usuario', 'usuario_nome', 'assunto', 'conteudo',
            'tipo', 'status', 'resposta', 'respondido_por',
            'respondido_por_nome', 'data_criacao', 'data_resposta'
        ]
        read_only_fields = ['usuario', 'respondido_por', 'data_criacao', 'data_resposta']


class MensagemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensagem
        fields = ['assunto', 'conteudo', 'tipo']


# ===========================================
# ALERTA PREFERÊNCIA
# ===========================================
class AlertaPreferenciaSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model = AlertaPreferencia
        fields = [
            'id', 'usuario', 'produto', 'produto_nome',
            'preco_minimo', 'preco_maximo', 'ativo', 'data_criacao'
        ]
        read_only_fields = ['usuario', 'data_criacao']


# ===========================================
# LOG AUDITORIA
# ===========================================
class LogAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = LogAuditoria
        fields = [
            'id', 'usuario', 'usuario_nome', 'acao', 'tabela_afetada',
            'registro_id', 'descricao', 'ip_address', 'dados_antigos',
            'dados_novos', 'data_criacao'
        ]
        read_only_fields = ['usuario', 'data_criacao']