# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    # Campos do BaseUserAdmin + campos personalizados
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Pessoais', {
            # ✅ REMOVIDO: documento_pdf (não existe)
            'fields': ('telemovel', 'tipo', 'nif', 'iban', 'foto_perfil')
        }),
        ('Perfil & Validação', {
            # ✅ REMOVIDO: rating_vendedor (não existe)
            'fields': ('vendas_concluidas', 'perfil_completo', 'conta_validada')
        }),
        ('Localização', {
            'fields': ('provincia', 'municipio')
        }),
        ('Financeiro', {
            'fields': ('saldo_disponivel',)
        }),
    )

    # Campos para criar novo usuário
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Pessoais', {
            'fields': ('telemovel', 'tipo', 'nif', 'first_name', 'last_name')
        }),
    )

    list_display = [
        'username', 'email', 'telemovel', 'tipo', 'perfil_completo',
        'conta_validada', 'provincia', 'saldo_disponivel', 'data_cadastro'
    ]
    list_display_links = ['username', 'email']
    list_filter = ['tipo', 'perfil_completo', 'conta_validada', 'provincia', 'data_cadastro']
    search_fields = ['username', 'email', 'telemovel', 'nif', 'first_name', 'last_name']
    ordering = ['-data_cadastro']
    readonly_fields = ['data_cadastro', 'saldo_disponivel', 'vendas_concluidas']

    # Ações em massa
    actions = ['validar_contas', 'marcar_perfil_completo', 'exportar_usuarios']

    def validar_contas(self, request, queryset):
        atualizados = queryset.update(conta_validada=True)
        self.message_user(request, f'{atualizados} contas validadas com sucesso.')

    validar_contas.short_description = '✅ Validar contas selecionadas'

    def marcar_perfil_completo(self, request, queryset):
        for usuario in queryset:
            usuario.verificar_e_atualizar_perfil()
        self.message_user(request, 'Perfis verificados e atualizados.')

    marcar_perfil_completo.short_description = '✓ Verificar perfis completos'

    def exportar_usuarios(self, request, queryset):
        self.message_user(request, 'Exportação iniciada (em desenvolvimento).')

    exportar_usuarios.short_description = '📥 Exportar usuários'