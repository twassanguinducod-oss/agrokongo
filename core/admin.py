from django.contrib import admin
from .models import Notificacao, Mensagem, LogAuditoria, AlertaPreferencia


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'mensagem_curta', 'lida', 'data_criacao']
    list_display_links = ['id']
    search_fields = ['usuario__username', 'mensagem']
    list_filter = ['lida', 'data_criacao']
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao']

    def mensagem_curta(self, obj):
        return obj.mensagem[:50] + '...' if len(obj.mensagem) > 50 else obj.mensagem

    mensagem_curta.short_description = 'Mensagem'

    actions = ['marcar_como_lidas', 'marcar_como_nao_lidas']

    def marcar_como_lidas(self, request, queryset):
        atualizados = queryset.update(lida=True)
        self.message_user(request, f'{atualizados} notificações marcadas como lidas.')

    marcar_como_lidas.short_description = '✓ Marcar como lidas'

    def marcar_como_nao_lidas(self, request, queryset):
        atualizados = queryset.update(lida=False)
        self.message_user(request, f'{atualizados} notificações marcadas como não lidas.')

    marcar_como_nao_lidas.short_description = '✗ Marcar como não lidas'


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ['id', 'transacao', 'remetente', 'destinatario', 'conteudo_curto', 'lida', 'data_envio']
    list_display_links = ['id']
    search_fields = ['remetente__username', 'destinatario__username', 'conteudo']
    list_filter = ['lida', 'data_envio']
    ordering = ['-data_envio']
    readonly_fields = ['data_envio', 'remetente', 'destinatario']

    def conteudo_curto(self, obj):
        return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo

    conteudo_curto.short_description = 'Conteúdo'


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'acao', 'ip', 'data_criacao']
    list_display_links = ['id']
    search_fields = ['usuario__username', 'acao', 'ip']
    list_filter = ['acao', 'data_criacao']
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao', 'ip']

    actions = ['exportar_logs']

    def exportar_logs(self, request, queryset):
        self.message_user(request, 'Exportação de logs iniciada (em desenvolvimento).')

    exportar_logs.short_description = '📥 Exportar logs'


@admin.register(AlertaPreferencia)
class AlertaPreferenciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'produto', 'data_criacao']
    list_display_links = ['id']
    search_fields = ['usuario__username', 'produto__nome']
    list_filter = ['data_criacao']
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao']