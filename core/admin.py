# core/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Notificacao, Mensagem, AlertaPreferencia, LogAuditoria


# ===========================================
# NOTIFICAÇÃO ADMIN
# ===========================================
@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'titulo', 'tipo', 'lida', 'data_criacao']
    list_filter = ['lida', 'tipo', 'data_criacao']
    search_fields = ['titulo', 'mensagem', 'usuario__username']
    readonly_fields = ['data_criacao', 'data_leitura']
    ordering = ['-data_criacao']

    actions = ['marcar_como_lida', 'marcar_como_nao_lida']

    def marcar_como_lida(self, request, queryset):
        queryset.update(lida=True, data_leitura=timezone.now())
        self.message_user(request, f'{queryset.count()} notificações marcadas como lidas.')

    marcar_como_lida.short_description = 'Marcar como lida'

    def marcar_como_nao_lida(self, request, queryset):
        queryset.update(lida=False, data_leitura=None)
        self.message_user(request, f'{queryset.count()} notificações marcadas como não lidas.')

    marcar_como_nao_lida.short_description = 'Marcar como não lida'


# ===========================================
# MENSAGEM ADMIN
# ===========================================
@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'assunto', 'tipo', 'status', 'data_criacao']
    list_filter = ['status', 'tipo', 'data_criacao']
    search_fields = ['assunto', 'conteudo', 'usuario__username']
    readonly_fields = ['data_criacao', 'data_resposta']
    ordering = ['-data_criacao']

    actions = ['marcar_como_respondido', 'marcar_como_pendente']

    def marcar_como_respondido(self, request, queryset):
        queryset.update(status='respondido')
        self.message_user(request, f'{queryset.count()} mensagens marcadas como respondidas.')

    marcar_como_respondido.short_description = 'Marcar como respondido'

    def marcar_como_pendente(self, request, queryset):
        queryset.update(status='pendente')
        self.message_user(request, f'{queryset.count()} mensagens marcadas como pendentes.')

    marcar_como_pendente.short_description = 'Marcar como pendente'


# ===========================================
# ALERTA PREFERÊNCIA ADMIN
# ===========================================
@admin.register(AlertaPreferencia)
class AlertaPreferenciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'produto', 'preco_maximo', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['usuario__username', 'produto__nome']
    readonly_fields = ['data_criacao']
    ordering = ['-data_criacao']


# ===========================================
# LOG AUDITORIA ADMIN
# ===========================================
@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'acao', 'tabela_afetada', 'registro_id', 'data_criacao']
    list_filter = ['acao', 'tabela_afetada', 'data_criacao']
    search_fields = ['usuario__username', 'descricao']
    readonly_fields = ['data_criacao', 'dados_antigos', 'dados_novos', 'ip_address']
    ordering = ['-data_criacao']