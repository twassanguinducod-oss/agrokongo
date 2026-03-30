# marketplace/admin.py
from django.contrib import admin
from .models import Categoria, Produto, Safra, ImagemSafra, Reserva, Pagamento


# ===========================================
# CATEGORIA ADMIN
# ===========================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'ativa']
    list_filter = ['ativa']
    search_fields = ['nome']
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ['nome']


# ===========================================
# PRODUTO ADMIN
# ===========================================
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'ativa']
    list_filter = ['categoria', 'ativa']
    search_fields = ['nome']
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ['nome']


# ===========================================
# SAFRA ADMIN
# ===========================================
@admin.register(Safra)
class SafraAdmin(admin.ModelAdmin):
    list_display = [
        'titulo',
        'produtor',
        'produto',
        'quantidade',
        'preco_unitario',
        'status',
    ]
    list_filter = ['status', 'produtor']
    search_fields = ['titulo', 'produtor__username', 'produto__nome']
    readonly_fields = [
        'quantidade_reservada',
        'quantidade_vendida',
    ]
    ordering = ['-id']


# ===========================================
# RESERVA ADMIN
# ===========================================
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'safra',
        'comprador',
        'quantidade',
        'preco_total',
        'status',
        'fatura_ref',
        'data_reserva'
    ]
    list_filter = ['status', 'data_reserva']
    search_fields = ['safra__titulo', 'comprador__username', 'fatura_ref']
    readonly_fields = ['preco_total', 'fatura_ref', 'data_reserva', 'data_expiracao']
    ordering = ['-data_reserva']

    actions = ['confirmar_reservas', 'cancelar_reservas', 'concluir_reservas']

    def confirmar_reservas(self, request, queryset):
        for reserva in queryset.filter(status='pendente'):
            try:
                reserva.confirmar()
            except Exception:
                pass
        self.message_user(request, f'{queryset.count()} reservas confirmadas.')

    confirmar_reservas.short_description = 'Confirmar reservas selecionadas'

    def cancelar_reservas(self, request, queryset):
        for reserva in queryset.exclude(status__in=['concluida', 'cancelada']):
            try:
                reserva.cancelar()
            except Exception:
                pass
        self.message_user(request, f'{queryset.count()} reservas canceladas.')

    cancelar_reservas.short_description = 'Cancelar reservas selecionadas'

    def concluir_reservas(self, request, queryset):
        queryset.filter(status='paga').update(status='concluida')
        self.message_user(request, f'{queryset.count()} reservas concluídas.')

    concluir_reservas.short_description = 'Concluir reservas selecionadas'


# ===========================================
# PAGAMENTO ADMIN
# ===========================================
@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'reserva',
        'valor',
        'status',
        'data_criacao'
    ]
    list_filter = ['status']
    search_fields = ['reserva__fatura_ref']
    readonly_fields = ['data_criacao']
    ordering = ['-data_criacao']

    actions = ['aprovar_pagamentos', 'rejeitar_pagamentos']

    def aprovar_pagamentos(self, request, queryset):
        for pagamento in queryset.filter(status='pendente'):
            pagamento.aprovar(validador=request.user)
        self.message_user(request, f'{queryset.count()} pagamentos aprovados.')

    aprovar_pagamentos.short_description = 'Aprovar pagamentos selecionados'

    def rejeitar_pagamentos(self, request, queryset):
        for pagamento in queryset.filter(status='pendente'):
            pagamento.rejeitar(validador=request.user, motivo='Rejeitado em massa pelo admin')
        self.message_user(request, f'{queryset.count()} pagamentos rejeitados.')

    rejeitar_pagamentos.short_description = 'Rejeitar pagamentos selecionados'