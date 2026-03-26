from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import re


class Usuario(AbstractUser):
    """Modelo de Usuário personalizado (substitui Flask-Login)"""

    TIPO_CHOICES = [
        ('admin', 'Administrador'),
        ('produtor', 'Produtor'),
        ('comprador', 'Comprador'),
    ]

    # Campos personalizados
    telemovel = models.CharField(max_length=20, unique=True, null=False)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, null=False)
    nif = models.CharField(max_length=20, unique=True, null=True, blank=True)
    iban = models.CharField(max_length=34, null=True, blank=True)

    # Rating e estatísticas
    rating_vendedor = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    vendas_concluidas = models.IntegerField(default=0)

    # Perfil
    foto_perfil = models.CharField(max_length=150, default='default_user.svg')
    documento_pdf = models.CharField(max_length=150, null=True, blank=True)
    perfil_completo = models.BooleanField(default=False)
    conta_validada = models.BooleanField(default=False)

    # Localização
    provincia = models.ForeignKey(
        'locations.Provincia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )
    municipio = models.ForeignKey(
        'locations.Municipio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )

    # Financeiro
    saldo_disponivel = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)

    # Timestamp
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        indexes = [
            models.Index(fields=['telemovel']),
            models.Index(fields=['email']),
            models.Index(fields=['tipo']),
            models.Index(fields=['conta_validada']),
        ]

    def __str__(self):
        return f'{self.username} ({self.tipo})'

    # --- Validação de Telemóvel ---
    def clean(self):
        if self.telemovel:
            num = re.sub(r'\D', '', self.telemovel)
            if num.startswith('244'):
                num = num[3:]
            if not re.match(r'^9\d{8}$', num):
                raise ValidationError('Formato de telemóvel angolano inválido (9xxxxxxxx).')

    # --- Verificação de Perfil Completo (KYC) ---
    def verificar_e_atualizar_perfil(self):
        """Valida se os dados obrigatórios de KYC foram preenchidos."""
        campos_comuns = [self.first_name, self.nif, self.provincia_id, self.municipio_id]

        if not all(campos_comuns):
            return False

        if self.tipo == 'produtor' and not self.iban:
            return False

        self.perfil_completo = True
        self.save(update_fields=['perfil_completo'])
        return True

    # --- Notificações ---
    def notificacoes_nao_lidas(self):
        from core.models import Notificacao
        return Notificacao.objects.filter(usuario=self, lida=False).count()

    def ultimas_notificacoes(self, limite=5):
        from core.models import Notificacao
        return Notificacao.objects.filter(usuario=self).order_by('-data_criacao')[:limite]