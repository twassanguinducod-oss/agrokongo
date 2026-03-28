# accounts/models.py
from django.db import models, transaction
from django.db.models import F
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
import re


class Usuario(AbstractUser):
    """Modelo de Usuário personalizado."""
    TIPO_CHOICES = [('admin', 'Administrador'), ('produtor', 'Produtor'), ('comprador', 'Comprador')]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, null=False)
    subtipo = models.CharField(max_length=50, null=True, blank=True)
    nif = models.CharField(max_length=20, null=True, blank=True)
    telemovel = models.CharField(max_length=20, unique=True, null=False)
    iban = models.CharField(max_length=34, null=True, blank=True)
    banco = models.CharField(max_length=100, null=True, blank=True)
    saldo_disponivel = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    vendas_concluidas = models.IntegerField(default=0)
    perfil_completo = models.BooleanField(default=False)
    conta_validada = models.BooleanField(default=False)
    provincia = models.ForeignKey('locations.Provincia', on_delete=models.SET_NULL, null=True, blank=True)
    municipio = models.ForeignKey('locations.Municipio', on_delete=models.SET_NULL, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    foto_perfil = models.CharField(max_length=150, default='default_user.svg')
    
    class Meta:
        db_table = 'usuarios'

    def __str__(self): return f'{self.username} ({self.tipo})'

    def clean(self):
        """Executa validações rigorosas, incluindo Checksum de IBAN."""
        if self.iban:
            self.iban = self._validar_iban_angolano(self.iban)
        super().clean()

    def _validar_iban_angolano(self, iban):
        """
        Validação Matemática Rigorosa (ISO 7064 / Modulo 97).
        Garante que o IBAN é estruturalmente e matematicamente válido.
        """
        # 1. Limpeza e Formatação
        iban_limpo = re.sub(r'[^A-Z0-9]', '', iban.upper())

        # Se tiver apenas 17 dígitos, assume-se que falta o prefixo AO06
        if len(iban_limpo) == 17 and iban_limpo.isdigit():
            iban_limpo = 'AO06' + iban_limpo

        # 2. Verificação de Estrutura Básica
        if not iban_limpo.startswith('AO06') or len(iban_limpo) != 21:
            raise ValidationError('IBAN inválido. Deve começar com AO06 e ter 21 caracteres no total.')

        # 3. Algoritmo ISO 7064 (MOD 97-10)
        # O IBAN angolano segue: AO06 + 17 dígitos
        # Reorganizar para validação: 17 dígitos + AO06
        # Converter letras para números: A=10, O=24
        # AO06 vira 102406
        numeros_conta = iban_limpo[4:]
        prefixo_convertido = "102406"
        numero_validacao = int(numeros_conta + prefixo_convertido)

        if numero_validacao % 97 != 1:
            raise ValidationError('O IBAN digitado é matematicamente inválido. Verifique se há erros de digitação.')

        return iban_limpo

    def verificar_e_atualizar_perfil(self):
        if self.tipo == 'produtor' and not self.iban: return False
        self.perfil_completo = True
        self.save(update_fields=['perfil_completo'])
        return True


class Levantamento(models.Model):
    # ... (Modelo Levantamento mantido conforme última versão segura)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='levantamentos')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, default='pendente')
    iban_destino = models.CharField(max_length=34)
    data_pedido = models.DateTimeField(auto_now_add=True)
    # [Omitido métodos aprovar/rejeitar por brevidade]
    class Meta: db_table = 'levantamentos'
