# marketplace/models.py
from django.db import models, transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.files.storage import FileSystemStorage
from django.core.validators import FileExtensionValidator
from decimal import Decimal
import os
import re
import magic


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True, related_name='produtos')
    unidade_medida = models.CharField(max_length=20, default='kg')
    preco_referencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    imagem = models.CharField(max_length=200, null=True, blank=True)
    ativa = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'produtos'

    def __str__(self):
        return self.nome


class Safra(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('sold', 'Esgotada'),
        ('cancelled', 'Cancelada'),
    ]

    produtor = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='safras')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='safras')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(null=True, blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    unidade_medida = models.CharField(max_length=20, default='kg')
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_reservada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantidade_vendida = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    provincia = models.ForeignKey('locations.Provincia', on_delete=models.SET_NULL, null=True, blank=True)
    municipio = models.ForeignKey('locations.Municipio', on_delete=models.SET_NULL, null=True, blank=True)
    endereco = models.CharField(max_length=200, null=True, blank=True)
    qualidade = models.CharField(max_length=50, null=True, blank=True)
    data_colheita = models.DateField(null=True, blank=True)
    data_validade = models.DateField(null=True, blank=True)
    certificacao_organica = models.BooleanField(default=False)
    imagem_principal = models.CharField(max_length=200, null=True, blank=True)
    visualizacoes = models.IntegerField(default=0)
    favoritos = models.IntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_publicacao = models.DateTimeField(null=True, blank=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)

    def quantidade_disponivel(self):
        return self.quantidade - self.quantidade_reservada - self.quantidade_vendida

    def is_disponivel(self):
        return self.quantidade_disponivel() > 0 and self.status == 'active'

    def is_expirado(self):
        if self.data_expiracao:
            return timezone.now().date() > self.data_expiracao
        return False

    @transaction.atomic
    def atualizar_status(self):
        safra = Safra.objects.select_for_update().get(pk=self.pk)
        if safra.quantidade_disponivel() <= 0:
            safra.status = 'sold'
        elif safra.is_expirado():
            safra.status = 'cancelled'
        else:
            safra.status = 'active'
        safra.save(update_fields=['status'])
        self.status = safra.status

    class Meta:
        db_table = 'safras'

    def __str__(self):
        return f'{self.titulo} - {self.produtor.username}'


class ImagemSafra(models.Model):
    safra = models.ForeignKey(Safra, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='safras/%Y/%m/%d/', null=True, blank=True)
    imagem_alta_resolucao = models.ImageField(upload_to='safras/hd/%Y/%m/%d/', null=True, blank=True)
    legenda = models.CharField(max_length=200, null=True, blank=True)
    principal = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'imagens_safra'
        ordering = ['ordem', '-principal']

    def __str__(self):
        return f'Imagem {self.id} - {self.safra.titulo}'


class Reserva(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('paga', 'Paga'),
        ('recebida', 'Recebida'),
        ('em_disputa', 'Em Disputa'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
        ('reembolsada', 'Reembolsada'),
    ]

    safra = models.ForeignKey(Safra, on_delete=models.CASCADE, related_name='reservas')
    comprador = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='reservas')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    unidade_medida = models.CharField(max_length=20, default='kg')
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    preco_total = models.DecimalField(max_digits=14, decimal_places=2)
    valor_liquido_vendedor = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    comissao_plataforma = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    fatura_ref = models.CharField(max_length=50, unique=True, null=True, blank=True)
    validado_por = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='reservas_validadas')
    data_validacao = models.DateTimeField(null=True, blank=True)
    motivo_rejeicao = models.TextField(null=True, blank=True)
    observacoes_comprador = models.TextField(null=True, blank=True)
    observacoes_vendedor = models.TextField(null=True, blank=True)
    data_reserva = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.fatura_ref:
            self.fatura_ref = f'FAC-{timezone.now().strftime("%Y%m%d%H%M%S")}-{get_random_string(6).upper()}'
        if not self.valor_liquido_vendedor:
            comissao = self.preco_total * Decimal('0.05')
            self.comissao_plataforma = comissao
            self.valor_liquido_vendedor = self.preco_total - comissao
        if not self.data_expiracao:
            self.data_expiracao = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    @transaction.atomic
    def confirmar(self):
        if self.status != 'pendente':
            raise ValidationError('Reserva já foi processada.')
        self.status = 'confirmada'
        self.safra.quantidade_reservada += self.quantidade
        self.safra.save()
        self.save()
        self.safra.atualizar_status()

    @transaction.atomic
    def cancelar(self, usuario=None):
        if self.status in ['concluida', 'cancelada']:
            raise ValidationError('Reserva não pode ser cancelada.')
        self.status = 'cancelada'
        self.safra.quantidade_reservada -= self.quantidade
        self.safra.save()
        self.save()
        self.safra.atualizar_status()

    def confirmar_rececao(self):
        if self.status != 'paga':
            raise ValidationError('Apenas reservas pagas podem ter receção confirmada.')
        self.status = 'recebida'
        self.save()

    @transaction.atomic
    def liberar_pagamento(self, admin):
        from accounts.models import Usuario
        if self.status != 'recebida':
            raise ValidationError('O pagamento só pode ser liberado após a receção ser confirmada.')

        produtor = Usuario.objects.select_for_update().get(pk=self.safra.produtor.pk)
        produtor.saldo_disponivel = F('saldo_disponivel') + self.valor_liquido_vendedor
        produtor.vendas_concluidas = F('vendas_concluidas') + 1
        produtor.save()

        self.status = 'concluida'
        self.save()

    class Meta:
        db_table = 'reservas'
        ordering = ['-data_reserva']

    def __str__(self):
        return f'{self.fatura_ref} - {self.comprador.username}'


# ===========================================
# PAGAMENTO - COM SEGURANÇA DE CONTEÚDO
# ===========================================
comprovativo_storage = FileSystemStorage(location='media/comprovativos')


def validate_file_mime(file):
    """Validação profunda do tipo de arquivo usando python-magic"""
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('Arquivo muito grande. Limite de 5MB.')

    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos)

    allowed_mimes = ['application/pdf', 'image/jpeg', 'image/png']
    if mime_type not in allowed_mimes:
        raise ValidationError(f'Tipo de ficheiro não permitido: {mime_type}. Use apenas JPG, PNG ou PDF.')


class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]

    METODO_CHOICES = [
        ('transferencia', 'Transferência Bancária'),
        ('multicaixa', 'Multicaixa'),
        ('deposito', 'Depósito'),
    ]

    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='pagamento')
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES, default='transferencia')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    comprovativo = models.FileField(
        upload_to='comprovativos/%Y/%m/%d/',
        storage=comprovativo_storage,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']),
            validate_file_mime
        ],
        null=True,
        blank=True
    )
    referencia_bancaria = models.CharField(max_length=100, null=True, blank=True)
    motivo_rejeicao = models.TextField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    validado_por = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='pagamentos_validados')
    data_validacao = models.DateTimeField(null=True, blank=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    @transaction.atomic
    def aprovar(self, validador):
        if self.status == 'aprovado':
            return
        self.status = 'aprovado'
        self.validado_por = validador
        self.data_validacao = timezone.now()
        self.save()

        reserva = Reserva.objects.select_for_update().get(pk=self.reserva.pk)
        reserva.status = 'paga'
        reserva.save()

    @transaction.atomic
    def rejeitar(self, validador, motivo):
        if self.status == 'rejeitado':
            return
        self.status = 'rejeitado'
        self.motivo_rejeicao = motivo
        self.validado_por = validador
        self.data_validacao = timezone.now()
        self.save()

        reserva = Reserva.objects.select_for_update().get(pk=self.reserva.pk)
        if reserva.status == 'paga':
            reserva.status = 'confirmada'
        reserva.save()

    class Meta:
        db_table = 'pagamentos'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'Pagamento {self.reserva.fatura_ref} - {self.status}'