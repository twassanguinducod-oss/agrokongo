# marketplace/models.py
from django.db import models, transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.files.storage import FileSystemStorage
from django.core.validators import FileExtensionValidator
from decimal import Decimal, ROUND_HALF_UP
import os
import re
import magic  # ✅ Requer python-magic

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    ativa = models.BooleanField(default=True)
    class Meta: db_table = 'categorias'
    def __str__(self): return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta: db_table = 'produtos'
    def __str__(self): return self.nome

class Safra(models.Model):
    STATUS_CHOICES = [('active', 'Ativa'), ('sold', 'Esgotada'), ('cancelled', 'Cancelada')]
    produtor = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='safras')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='safras')
    titulo = models.CharField(max_length=200)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_reservada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantidade_vendida = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    def quantidade_disponivel(self): 
        return self.quantidade - self.quantidade_reservada - self.quantidade_vendida
    
    @transaction.atomic
    def atualizar_status(self):
        # ✅ PROTEÇÃO CONTRA RACE CONDITION: Recarrega do banco com lock
        safra = Safra.objects.select_for_update().get(pk=self.pk)
        if safra.quantidade_disponivel() <= 0: 
            safra.status = 'sold'
        else:
            safra.status = 'active'
        safra.save(update_fields=['status'])
        self.status = safra.status

    class Meta: db_table = 'safras'

class Reserva(models.Model):
    STATUS_CHOICES = [('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('paga', 'Paga'), ('recebida', 'Recebida'), ('em_disputa', 'Em Disputa'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada'), ('reembolsada', 'Reembolsada')]
    safra = models.ForeignKey(Safra, on_delete=models.CASCADE, related_name='reservas')
    comprador = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='reservas')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_total = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    valor_liquido_vendedor = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    comissao_plataforma = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    def confirmar_rececao(self): 
        self.status = 'recebida'
        self.save()

    @transaction.atomic
    def liberar_pagamento(self, admin):
        """Libera o saldo para o produtor e conclui a reserva."""
        from accounts.models import Usuario # Import local para evitar circularidade
        if self.status != 'recebida':
            raise ValidationError("O pagamento só pode ser liberado após a receção ser confirmada.")
            
        produtor = Usuario.objects.select_for_update().get(pk=self.safra.produtor.pk)
        produtor.saldo_disponivel = F('saldo_disponivel') + self.valor_liquido_vendedor
        produtor.vendas_concluidas = F('vendas_concluidas') + 1
        produtor.save()
        
        self.status = 'concluida'
        self.save()

    class Meta: db_table = 'reservas'

# ===========================================
# PAGAMENTO - COM SEGURANÇA DE CONTEÚDO
# ===========================================
comprovativo_storage = FileSystemStorage(location='media/comprovativos')

def validate_file_mime(file):
    """Validação profunda do tipo de arquivo usando python-magic (Prevenção RCE/Spoofing)"""
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('Arquivo muito grande. Limite de 5MB.')
    
    # Ler os primeiros bytes para detecção de tipo real
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos)
    
    allowed_mimes = ['application/pdf', 'image/jpeg', 'image/png']
    if mime_type not in allowed_mimes:
        raise ValidationError(f'Tipo de ficheiro não permitido: {mime_type}. Use apenas JPG, PNG ou PDF.')

class Pagamento(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='pagamento')
    status = models.CharField(max_length=20, default='pendente')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    
    comprovativo = models.FileField(
        upload_to='comprovativos/%Y/%m/%d/',
        storage=comprovativo_storage,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']),
            validate_file_mime
        ],
        null=True
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    @transaction.atomic
    def aprovar(self, validador):
        if self.status == 'aprovado':
            return
        self.status = 'aprovado'
        self.save()
        
        reserva = Reserva.objects.select_for_update().get(pk=self.reserva.pk)
        reserva.status = 'paga'
        reserva.save()

    class Meta: db_table = 'pagamentos'
