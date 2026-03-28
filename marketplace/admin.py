# marketplace/admin.py
from django.contrib import admin
from .models import Categoria, Produto, Safra, ImagemSafra, Reserva, Pagamento


# ===========================================
# CATEGORIA ADMIN
# ===========================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'icone', 'ordem', 'ativa', 'data_criacao']
    list_filter = ['ativa', 'data_criacao']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ['ordem', 'nome']


# ===========================================
# PRODUTO ADMIN
# ===========================================
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'unidade_medida', 'preco_referencia', 'ativa', 'data_criacao']
    list_filter = ['categoria', 'unidade_medida', 'ativa']
    search_fields = ['nome', 'descricao']
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
        'provincia',
        'data_criacao'
    ]
    list_filter = ['status', 'qualidade', 'certificacao_organica', 'provincia', 'data_criacao']
    search_fields = ['titulo', 'descricao', 'produtor__username', 'produto__nome']
    readonly_fields = [
        'preco_total',
        'quantidade_reservada',
        'quantidade_vendida',
        'visualizacoes',
        'favoritos',
        'data_publicacao',
        'data_expiracao',
    ]
    ordering = ['-data_criacao']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('produtor', 'produto', 'titulo', 'descricao')
        }),
        ('Quantidade e Preço', {
            'fields': ('quantidade', 'unidade_medida', 'preco_unitario', 'preco_total')
        }),
        ('Localização', {
            'fields': ('provincia', 'municipio', 'endereco')
        }),
        ('Status e Qualidade', {
            'fields': ('status', 'qualidade', 'motivo_rejeicao')
        }),
        ('Validade', {
            'fields': ('data_colheita', 'data_validade', 'certificacao_organica')
        }),
        ('Imagens', {
            'fields': ('imagem_principal', 'imagem_alta_resolucao')
        }),
        ('Estatísticas', {
            'fields': ('quantidade_reservada', 'quantidade_vendida', 'visualizacoes', 'favoritos'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('data_publicacao', 'data_expiracao', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


# ===========================================
# IMAGEM SAFRA ADMIN
# ===========================================
@admin.register(ImagemSafra)
class ImagemSafraAdmin(admin.ModelAdmin):
    list_display = ['id', 'safra', 'legenda', 'principal', 'ordem', 'data_upload']
    list_filter = ['principal', 'data_upload']
    search_fields = ['safra__titulo', 'legenda']
    ordering = ['ordem', '-principal']


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
    list_filter = ['status', 'data_reserva', 'data_expiracao']
    search_fields = ['safra__titulo', 'comprador__username', 'fatura_ref']
    readonly_fields = ['preco_total', 'fatura_ref', 'data_reserva', 'data_expiracao']
    ordering = ['-data_reserva']

    fieldsets = (
        ('Informações da Reserva', {
            'fields': ('safra', 'comprador', 'quantidade', 'preco_unitario', 'preco_total')
        }),
        ('Status e Validação', {
            'fields': ('status', 'fatura_ref', 'validado_por', 'data_validacao', 'motivo_rejeicao')
        }),
        ('Observações', {
            'fields': ('observacoes_comprador', 'observacoes_vendedor'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('data_reserva', 'data_atualizacao', 'data_expiracao'),
            'classes': ('collapse',)
        }),
    )

    actions = ['confirmar_reservas', 'cancelar_reservas', 'concluir_reservas']

    def confirmar_reservas(self, request, queryset):
        queryset.filter(status='pendente').update(status='confirmada')
        self.message_user(request, f'{queryset.count()} reservas confirmadas.')

    confirmar_reservas.short_description = 'Confirmar reservas selecionadas'

    def cancelar_reservas(self, request, queryset):
        queryset.update(status='cancelada')
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
        'metodo',
        'valor',
        'status',
        'validado_por',
        'data_validacao',
        'data_criacao'
    ]
    list_filter = ['status', 'metodo', 'data_criacao', 'data_validacao']
    search_fields = ['reserva__fatura_ref', 'referencia_bancaria', 'comprovativo']
    readonly_fields = ['data_criacao', 'data_atualizacao', 'data_validacao']
    ordering = ['-data_criacao']

    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('reserva', 'metodo', 'valor', 'data_pagamento')
        }),
        ('Comprovativo', {
            'fields': ('comprovativo', 'referencia_bancaria')
        }),
        ('Validação', {
            'fields': ('status', 'validado_por', 'data_validacao', 'motivo_rejeicao')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

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