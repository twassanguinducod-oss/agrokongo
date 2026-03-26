from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal
from .models import Produto, Safra, Transacao, HistoricoStatus, Avaliacao, TransactionStatus


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'categoria', 'safras_ativas']
    list_display_links = ['nome']
    search_fields = ['nome', 'categoria']
    list_filter = ['categoria']
    ordering = ['nome']

    def safras_ativas(self, obj):
        return obj.safras_rel.filter(status='disponivel').count()

    safras_ativas.short_description = 'Safras Disponíveis'


@admin.register(Safra)
class SafraAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'produto', 'produtor', 'quantidade_disponivel',
        'preco_por_unidade', 'valor_total', 'status', 'data_criacao'
    ]
    list_display_links = ['id', 'produto']
    search_fields = ['produto__nome', 'produtor__username', 'produtor__telemovel']
    list_filter = ['status', 'produto', 'data_criacao']
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao', 'produtor']

    def valor_total(self, obj):
        if obj.quantidade_disponivel and obj.preco_por_unidade:
            return Decimal(str(obj.quantidade_disponivel)) * Decimal(str(obj.preco_por_unidade))
        return Decimal('0.00')

    valor_total.short_description = 'Valor Total (KZ)'

    # Ações em massa
    actions = ['marcar_disponivel', 'marcar_indisponivel']

    def marcar_disponivel(self, request, queryset):
        atualizados = queryset.update(status='disponivel')
        self.message_user(request, f'{atualizados} safras marcadas como disponíveis.')

    marcar_disponivel.short_description = '✓ Marcar como disponível'

    def marcar_indisponivel(self, request, queryset):
        atualizados = queryset.update(status='indisponivel')
        self.message_user(request, f'{atualizados} safras marcadas como indisponíveis.')

    marcar_indisponivel.short_description = '✗ Marcar como indisponível'


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = [
        'fatura_ref', 'comprador_link', 'vendedor_link', 'produto_nome',
        'quantidade_comprada', 'valor_total_pago', 'comissao', 'status',
        'data_criacao', 'transferencia_concluida'
    ]
    list_display_links = ['fatura_ref']
    search_fields = ['fatura_ref', 'comprador__username', 'vendedor__username', 'safra__produto__nome']
    list_filter = ['status', 'transferencia_concluida', 'data_criacao', 'safra__produto']
    ordering = ['-data_criacao']
    readonly_fields = [
        'fatura_ref', 'comissao_plataforma', 'valor_liquido_vendedor',
        'data_criacao', 'comprador', 'vendedor', 'safra'
    ]

    # Fieldsets para organização
    fieldsets = (
        ('Identificação', {
            'fields': ('fatura_ref', 'safra', 'comprador', 'vendedor')
        }),
        ('Valores', {
            'fields': ('quantidade_comprada', 'valor_total_pago', 'comissao_plataforma', 'valor_liquido_vendedor')
        }),
        ('Status & Datas', {
            'fields': ('status', 'data_criacao', 'data_pagamento_escrow', 'data_envio', 'data_entrega',
                       'data_liquidacao', 'previsao_entrega')
        }),
        ('Comprovativos', {
            'fields': ('comprovativo_path', 'transferencia_concluida')
        }),
        ('Soft Delete', {
            'fields': ('deleted_at',),
            'classes': ('collapse',)
        }),
    )

    # Links para usuários
    def comprador_link(self, obj):
        return format_html('<a href="/admin/accounts/usuario/{}/change/">{}</a>', obj.comprador.id,
                           obj.comprador.username)

    comprador_link.short_description = 'Comprador'

    def vendedor_link(self, obj):
        return format_html('<a href="/admin/accounts/usuario/{}/change/">{}</a>', obj.vendedor.id,
                           obj.vendedor.username)

    vendedor_link.short_description = 'Vendedor'

    def produto_nome(self, obj):
        return obj.safra.produto.nome if obj.safra else '-'

    produto_nome.short_description = 'Produto'

    def comissao(self, obj):
        return f"{obj.comissao_plataforma} KZ"

    comissao.short_description = 'Comissão (5%)'

    # Ações em massa
    actions = [
        'marcar_como_pago',
        'marcar_como_enviado',
        'marcar_como_entregue',
        'cancelar_transacoes',
        'exportar_transacoes'
    ]

    def marcar_como_pago(self, request, queryset):
        from .models import TransactionStatus
        atualizados = queryset.filter(
            status=TransactionStatus.AGUARDANDO_PAGAMENTO
        ).update(status=TransactionStatus.ANALISE)
        self.message_user(request, f'{atualizados} transações marcadas como pagas.')

    marcar_como_pago.short_description = '💰 Marcar como pago'

    def marcar_como_enviado(self, request, queryset):
        from .models import TransactionStatus
        atualizados = queryset.filter(
            status=TransactionStatus.ESCROW
        ).update(status=TransactionStatus.ENVIADO)
        self.message_user(request, f'{atualizados} transações marcadas como enviadas.')

    marcar_como_enviado.short_description = '📦 Marcar como enviado'

    def marcar_como_entregue(self, request, queryset):
        from .models import TransactionStatus
        atualizados = queryset.filter(
            status=TransactionStatus.ENVIADO
        ).update(status=TransactionStatus.FINALIZADO)
        self.message_user(request, f'{atualizados} transações marcadas como entregues.')

    marcar_como_entregue.short_description = '✅ Marcar como entregue'

    def cancelar_transacoes(self, request, queryset):
        from .models import TransactionStatus
        atualizados = queryset.exclude(
            status__in=[TransactionStatus.FINALIZADO, TransactionStatus.CANCELADO]
        ).update(status=TransactionStatus.CANCELADO)
        self.message_user(request, f'{atualizados} transações canceladas.')

    cancelar_transacoes.short_description = '❌ Cancelar transações'

    def exportar_transacoes(self, request, queryset):
        # Implementar exportação CSV/Excel
        self.message_user(request, 'Exportação iniciada (em desenvolvimento).')

    exportar_transacoes.short_description = '📥 Exportar transações'


@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'transacao', 'status_anterior', 'status_novo', 'data_mudanca']
    list_display_links = ['id']
    search_fields = ['transacao__fatura_ref', 'status_anterior', 'status_novo']
    list_filter = ['status_novo', 'data_mudanca']
    ordering = ['-data_mudanca']
    readonly_fields = ['data_mudanca']


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'transacao', 'nota', 'comprador', 'data_criacao']
    list_display_links = ['id']
    search_fields = ['transacao__fatura_ref', 'comentario']
    list_filter = ['nota', 'data_criacao']
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao']

    def comprador(self, obj):
        return obj.transacao.comprador.username if obj.transacao else '-'

    comprador.short_description = 'Comprador'