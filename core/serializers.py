# core/serializers.py
from rest_framework import serializers
from .models import Notificacao, Mensagem, AlertaPreferencia, LogAuditoria


# ===========================================
# NOTIFICAÇÃO SERIALIZER
# ===========================================
class NotificacaoSerializer(serializers.ModelSerializer):
    """Serializer para notificações"""

    class Meta:
        model = Notificacao
        fields = [
            'id',
            'usuario',
            'titulo',
            'mensagem',
            'tipo',
            'lida',
            'data_criacao',
            'data_leitura',
        ]
        read_only_fields = ['usuario', 'data_criacao', 'data_leitura']


class NotificacaoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar notificação"""

    class Meta:
        model = Notificacao
        fields = ['titulo', 'mensagem', 'tipo']


# ===========================================
# MENSAGEM SERIALIZER
# ===========================================
class MensagemSerializer(serializers.ModelSerializer):
    """Serializer para mensagens"""
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)
    respondido_por_nome = serializers.CharField(source='respondido_por.username', read_only=True)

    class Meta:
        model = Mensagem
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'assunto',
            'conteudo',
            'tipo',
            'status',
            'resposta',
            'respondido_por',
            'respondido_por_nome',
            'data_criacao',
            'data_resposta',
        ]
        read_only_fields = ['usuario', 'respondido_por', 'data_criacao', 'data_resposta']


class MensagemCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar mensagem"""

    class Meta:
        model = Mensagem
        fields = ['assunto', 'conteudo', 'tipo']


# ===========================================
# ALERTA PREFERÊNCIA SERIALIZER
# ===========================================
class AlertaPreferenciaSerializer(serializers.ModelSerializer):
    """Serializer para alertas de preferência"""
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model = AlertaPreferencia
        fields = [
            'id',
            'usuario',
            'produto',
            'produto_nome',
            'preco_minimo',
            'preco_maximo',
            'ativo',
            'data_criacao',
        ]
        read_only_fields = ['usuario', 'data_criacao']


# ===========================================
# LOG AUDITORIA SERIALIZER
# ===========================================
class LogAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer para logs de auditoria"""
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = LogAuditoria
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'acao',
            'tabela_afetada',
            'registro_id',
            'descricao',
            'ip_address',
            'dados_antigos',
            'dados_novos',
            'data_criacao',
        ]
        read_only_fields = ['usuario', 'data_criacao']