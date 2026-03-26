from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
import uuid
from datetime import timedelta


# --- ENUM de Status (Django TextChoices) ---
class TransactionStatus(models.TextChoices):
    """Estados possíveis de uma transação no marketplace."""
    PENDENTE = 'pendente', 'Pendente'
    AGUARDANDO_PAGAMENTO = 'pendente_pagamento', 'Aguardando Pagamento'
    ANALISE = 'pagamento_sob_analise', 'Em Análise'
    ESCROW = 'pago_escrow', 'Em Escrow'
    ENVIADO = 'mercadoria_enviada', 'Enviado'
    ENTREGUE = 'mercadoria_entregue', 'Entregue'
    FINALIZADO = 'finalizada', 'Finalizada'
    CANCELADO = 'cancelada', 'Cancelada'
    DISPUTA = 'em_disputa', 'Em Disputa'


class Produto(models.Model):
    """Catálogo de Produtos Agrícolas"""
    nome = models.CharField(max_length=50, unique=True, null=False)
    categoria = models.CharField(max_length=50, db_index=True)

    class Meta:
        db_table = 'produtos'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Safra(models.Model):
    """Oferta de Safra de um Produtor"""
    produtor = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.CASCADE,
        related_name='safras',
        null=False
    )
    produto = models.ForeignKey(
        'Produto',
        on_delete=models.CASCADE,
        related_name='safras',
        null=False
    )
    quantidade_disponivel = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    preco_por_unidade = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    status = models.CharField(max_length=20, default='disponivel', db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    imagem = models.CharField(max_length=150, default='default_safra.webp')
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'safras'
        verbose_name = 'Safra'
        verbose_name_plural = 'Safras'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['produto_id', 'status']),
        ]

    def __str__(self):
        return f'Safra #{self.id} - {self.produto.nome} ({self.status})'

    # Validação no clean() em vez de CheckConstraint
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.quantidade_disponivel < 0:
            raise ValidationError('Quantidade não pode ser negativa.')
        if self.preco_por_unidade <= 0:
            raise ValidationError('Preço deve ser maior que zero.')


class Transacao(models.Model):
    """Sistema Transacional - O Motor do Marketplace"""

    # Identificação
    fatura_ref = models.CharField(max_length=50, unique=True, null=False, db_index=True)
    safra = models.ForeignKey('Safra', on_delete=models.PROTECT, related_name='transacoes')
    comprador = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.PROTECT,
        related_name='compras',
        null=False
    )
    vendedor = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.PROTECT,
        related_name='vendas',
        null=False
    )

    # Valores
    quantidade_comprada = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    valor_total_pago = models.DecimalField(max_digits=14, decimal_places=2, null=False)
    comissao_plataforma = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    valor_liquido_vendedor = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)

    # Status e Datas
    status = models.CharField(
        max_length=30,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDENTE,
        db_index=True
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_pagamento_escrow = models.DateTimeField(null=True, blank=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_entrega = models.DateTimeField(null=True, blank=True)
    data_liquidacao = models.DateTimeField(null=True, blank=True)
    previsao_entrega = models.DateTimeField(null=True, blank=True)

    # Comprovativos
    comprovativo_path = models.CharField(max_length=255, null=True, blank=True)
    transferencia_concluida = models.BooleanField(default=False)

    # Soft Delete
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'transacoes'
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['status', 'deleted_at']),
        ]

    def __str__(self):
        return f'Transação {self.fatura_ref}'

    # --- Auto-generação da Fatura Ref ---
    def save(self, *args, **kwargs):
        if not self.fatura_ref:
            self.fatura_ref = f"AK-{timezone.now().year}-{uuid.uuid4().hex[:8].upper()}"
        self.recalcular_financeiro()
        super().save(*args, **kwargs)

    # --- Cálculo Financeiro (95/5) ---
    def recalcular_financeiro(self):
        if self.valor_total_pago:
            total = Decimal(str(self.valor_total_pago))
            taxa = Decimal('0.05')  # 5%
            self.comissao_plataforma = (total * taxa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.valor_liquido_vendedor = (total - self.comissao_plataforma).quantize(Decimal('0.01'),
                                                                                      rounding=ROUND_HALF_UP)

    # --- Logística ---
    def calcular_janela_logistica(self):
        if self.data_envio:
            self.previsao_entrega = self.data_envio + timedelta(days=3)
            self.save(update_fields=['previsao_entrega'])

    # --- Soft Delete Managers ---
    @classmethod
    def ativas(cls):
        return cls.objects.filter(deleted_at=None)

    @classmethod
    def deletadas(cls):
        return cls.objects.filter(deleted_at__isnull=False)

    # --- Mudança de Status com Histórico ---
    def mudar_status(self, novo_status, observacao=None, usuario=None, auto_add=True, validar_transicao=False):
        from django.core.exceptions import ValidationError
        if validar_transicao and not self.pode_mudar_para(novo_status):
            raise ValidationError(f'Transição inválida de {self.status} para {novo_status}')

        if self.status != novo_status:
            historico = HistoricoStatus.objects.create(
                transacao=self,
                status_anterior=self.status,
                status_novo=novo_status,
                observacao=observacao
            )
            self.status = novo_status
            if auto_add:
                self.save(update_fields=['status'])
            return historico
        return None

    # --- Validação de Transição ---
    def pode_mudar_para(self, novo_status):
        transicoes_validas = {
            TransactionStatus.PENDENTE: [TransactionStatus.AGUARDANDO_PAGAMENTO, TransactionStatus.CANCELADO],
            TransactionStatus.AGUARDANDO_PAGAMENTO: [TransactionStatus.ANALISE, TransactionStatus.CANCELADO],
            TransactionStatus.ANALISE: [TransactionStatus.ESCROW, TransactionStatus.AGUARDANDO_PAGAMENTO],
            TransactionStatus.ESCROW: [TransactionStatus.ENVIADO, TransactionStatus.CANCELADO],
            TransactionStatus.ENVIADO: [TransactionStatus.FINALIZADO, TransactionStatus.CANCELADO],
            TransactionStatus.FINALIZADO: [],
            TransactionStatus.CANCELADO: [],
        }
        destinos_permitidos = transicoes_validas.get(self.status, [])
        return novo_status in destinos_permitidos


class HistoricoStatus(models.Model):
    """Histórico de Mudanças de Status da Transação"""
    transacao = models.ForeignKey('Transacao', on_delete=models.CASCADE, related_name='historico_status')
    status_anterior = models.CharField(max_length=30)
    status_novo = models.CharField(max_length=30)
    data_mudanca = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'historico_status'
        verbose_name = 'Histórico de Status'
        ordering = ['-data_mudanca']

    def __str__(self):
        return f'{self.transacao.fatura_ref}: {self.status_anterior} → {self.status_novo}'


class Avaliacao(models.Model):
    """Avaliação da Transação (1-5 estrelas)"""
    transacao = models.ForeignKey('Transacao', on_delete=models.CASCADE, related_name='avaliacao')
    nota = models.IntegerField(null=False)  # 1-5
    comentario = models.TextField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'avaliacoes'
        verbose_name = 'Avaliação'

    def __str__(self):
        return f'Avaliação {self.nota}★ para {self.transacao.fatura_ref}'

    # Validação da nota no clean()
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.nota < 1 or self.nota > 5:
            raise ValidationError('Nota deve ser entre 1 e 5.')
