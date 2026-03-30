# core/serializers.py
import re

from rest_framework import serializers
from .models import Notificacao, Mensagem, AlertaPreferencia, LogAuditoria, InfoContato, Contato, PaginaSobre


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


# ===========================================
# PÁGINA SOBRE
# ===========================================
class PaginaSobreSerializer(serializers.ModelSerializer):
    valores_lista = serializers.SerializerMethodField()

    def get_valores_lista(self, obj):
        return [v.strip() for v in obj.valores.split(',')] if obj.valores else []

    class Meta:
        model = PaginaSobre
        fields = [
            'id', 'titulo', 'missao', 'visao', 'valores', 'valores_lista',
            'historia', 'equipa', 'data_atualizacao'
        ]


# ===========================================
# CONTATO
# ===========================================
class ContatoSerializer(serializers.ModelSerializer):
    respondido_por_nome = serializers.CharField(source='respondido_por.username', read_only=True)

    class Meta:
        model = Contato
        fields = [
            'id', 'nome', 'email', 'telemovel', 'assunto', 'mensagem',
            'status', 'resposta', 'respondido_por', 'respondido_por_nome',
            'data_criacao', 'data_resposta'
        ]
        read_only_fields = ['id', 'status', 'resposta', 'respondido_por', 'data_criacao', 'data_resposta']


class ContatoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar mensagem de contato (público)"""

    class Meta:
        model = Contato
        fields = ['nome', 'email', 'telemovel', 'assunto', 'mensagem']

    def create(self, validated_data):
        # Enviar email de confirmação (opcional)
        # from django.core.mail import send_mail
        # send_mail(...)
        return super().create(validated_data)


# ===========================================
# INFORMAÇÕES DE CONTATO
# ===========================================
class InfoContatoSerializer(serializers.ModelSerializer):
    whatsapp_link = serializers.SerializerMethodField()

    def get_whatsapp_link(self, obj):
        if obj.whatsapp:
            numero_limpo = re.sub(r'[^\d]', '', obj.whatsapp)
            return f'https://wa.me/{numero_limpo}'
        return None

    class Meta:
        model = InfoContato
        fields = [
            'id', 'whatsapp', 'whatsapp_link', 'email_suporte',
            'email_comercial', 'endereco', 'horario_atendimento',
            'facebook', 'instagram', 'linkedin', 'data_atualizacao'
        ]