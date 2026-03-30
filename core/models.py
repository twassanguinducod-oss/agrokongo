# core/models.py
import re
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


# ===========================================
# NOTIFICAÇÃO
# ===========================================
class Notificacao(models.Model):
    """Notificações do sistema para usuários"""

    TIPO_CHOICES = [
        ('info', 'Informação'),
        ('aviso', 'Aviso'),
        ('erro', 'Erro'),
        ('sucesso', 'Sucesso'),
    ]

    usuario = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.CASCADE,
        related_name='notificacoes'
    )
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='info'
    )
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_leitura = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notificacoes'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'lida']),
            models.Index(fields=['data_criacao']),
        ]

    def __str__(self):
        return f'{self.titulo} - {self.usuario.username}'

    def marcar_lida(self):
        """Marca notificação como lida"""
        self.lida = True
        self.data_leitura = timezone.now()
        self.save(update_fields=['lida', 'data_leitura'])


# ===========================================
# MENSAGEM (SUPORTE)
# ===========================================
class Mensagem(models.Model):
    """Mensagens de suporte entre usuários e admin"""

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('respondido', 'Respondido'),
        ('fechado', 'Fechado'),
    ]

    usuario = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.CASCADE,
        related_name='mensagens'
    )
    assunto = models.CharField(max_length=200, default='')
    conteudo = models.TextField()
    tipo = models.CharField(max_length=50, default='suporte')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    resposta = models.TextField(null=True, blank=True)
    respondido_por = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mensagens_respondidas',
        limit_choices_to={'tipo': 'admin'}
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'mensagens'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['data_criacao']),
        ]

    def __str__(self):
        return f'{self.assunto} - {self.usuario.username}'

    def responder(self, admin, resposta):
        """Responde à mensagem"""
        self.resposta = resposta
        self.respondido_por = admin
        self.status = 'respondido'
        self.data_resposta = timezone.now()
        self.save(update_fields=['resposta', 'respondido_por', 'status', 'data_resposta'])


# ===========================================
# ALERTA PREFERÊNCIA
# ===========================================
class AlertaPreferencia(models.Model):
    """Alertas de preço para produtos específicos"""

    usuario = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.CASCADE,
        related_name='alertas'
    )
    produto = models.ForeignKey(
        'marketplace.Produto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alertas'
    )
    preco_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    preco_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alertas_preferencia'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'ativo']),
        ]

    def __str__(self):
        return f'{self.usuario.username} - {self.produto}'


# ===========================================
# LOG AUDITORIA
# ===========================================
class LogAuditoria(models.Model):
    """Logs de auditoria para ações críticas"""

    ACAO_CHOICES = [
        ('create', 'Criar'),
        ('update', 'Atualizar'),
        ('delete', 'Eliminar'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    usuario = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='logs_auditoria'
    )
    acao = models.CharField(
        max_length=20,
        choices=ACAO_CHOICES
    )
    tabela_afetada = models.CharField(max_length=100)
    registro_id = models.IntegerField(null=True, blank=True)
    descricao = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    dados_antigos = models.JSONField(null=True, blank=True)
    dados_novos = models.JSONField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'logs_auditoria'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'acao']),
            models.Index(fields=['tabela_afetada', 'data_criacao']),
        ]

    def __str__(self):
        return f'{self.acao} - {self.tabela_afetada} - {self.usuario}'

# ===========================================
# PÁGINA SOBRE (CONTEÚDO ESTÁTICO)
# ===========================================
class PaginaSobre(models.Model):
    """Modelo para conteúdo da página Sobre"""
    titulo = models.CharField(max_length=200, default='Sobre a AgroKongo')
    missao = models.TextField()
    visao = models.TextField()
    valores = models.TextField(help_text='Valores separados por vírgula')
    historia = models.TextField()
    equipa = models.TextField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pagina_sobre'
        verbose_name = 'Página Sobre'
        verbose_name_plural = 'Página Sobre'

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        # Garantir que apenas 1 registro exista
        if not self.pk and PaginaSobre.objects.exists():
            raise ValidationError('Já existe uma página Sobre. Edite o registro existente.')
        super().save(*args, **kwargs)


# ===========================================
# CONTATO / MENSAGENS DE SUPORTE
# ===========================================
class Contato(models.Model):
    """Modelo para mensagens de contato do formulário"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('respondido', 'Respondido'),
        ('arquivado', 'Arquivado'),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telemovel = models.CharField(max_length=20, null=True, blank=True)
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    resposta = models.TextField(null=True, blank=True)
    respondido_por = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'contatos'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'{self.assunto} - {self.nome}'

    def responder(self, admin, resposta):
        """Responde à mensagem de contato"""
        from django.utils import timezone
        self.resposta = resposta
        self.respondido_por = admin
        self.status = 'respondido'
        self.data_resposta = timezone.now()
        self.save()


# ===========================================
# INFORMAÇÕES DE CONTATO DA EMPRESA
# ===========================================
class InfoContato(models.Model):
    """Informações de contato da empresa (WhatsApp, email, etc.)"""
    whatsapp = models.CharField(max_length=20, help_text='Ex: +244923456789')
    email_suporte = models.EmailField()
    email_comercial = models.EmailField()
    endereco = models.TextField(null=True, blank=True)
    horario_atendimento = models.CharField(max_length=200, default='Segunda a Sexta, 8h às 17h')
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'info_contato'
        verbose_name = 'Informações de Contato'
        verbose_name_plural = 'Informações de Contato'

    def __str__(self):
        return f'Contato - {self.whatsapp}'

    def save(self, *args, **kwargs):
        # Garantir que apenas 1 registro exista
        if not self.pk and InfoContato.objects.exists():
            raise ValidationError('Já existe um registro de informações de contato.')
        super().save(*args, **kwargs)

# ===========================================
# PÁGINA SOBRE (CONTEÚDO ESTÁTICO)
# ===========================================
class PaginaSobre(models.Model):
    """Modelo para conteúdo da página Sobre"""
    titulo = models.CharField(max_length=200, default='Sobre a AgroKongo')
    missao = models.TextField()
    visao = models.TextField()
    valores = models.TextField(help_text='Valores separados por vírgula')
    historia = models.TextField()
    equipa = models.TextField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pagina_sobre'
        verbose_name = 'Página Sobre'
        verbose_name_plural = 'Página Sobre'

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        # Garantir que apenas 1 registro exista
        if not self.pk and PaginaSobre.objects.exists():
            raise ValidationError('Já existe uma página Sobre. Edite o registro existente.')
        super().save(*args, **kwargs)


# ===========================================
# CONTATO / MENSAGENS DE SUPORTE
# ===========================================
class Contato(models.Model):
    """Modelo para mensagens de contato do formulário"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('respondido', 'Respondido'),
        ('arquivado', 'Arquivado'),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telemovel = models.CharField(max_length=20, null=True, blank=True)
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    resposta = models.TextField(null=True, blank=True)
    respondido_por = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'contatos'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'{self.assunto} - {self.nome}'

    def responder(self, admin, resposta):
        """Responde à mensagem de contato"""
        self.resposta = resposta
        self.respondido_por = admin
        self.status = 'respondido'
        self.data_resposta = timezone.now()
        self.save()


# ===========================================
# INFORMAÇÕES DE CONTATO DA EMPRESA
# ===========================================
class InfoContato(models.Model):
    """Informações de contato da empresa (WhatsApp, email, etc.)"""
    whatsapp = models.CharField(max_length=20, help_text='Ex: +244923456789')
    email_suporte = models.EmailField()
    email_comercial = models.EmailField()
    endereco = models.TextField(null=True, blank=True)
    horario_atendimento = models.CharField(max_length=200, default='Segunda a Sexta, 8h às 17h')
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'info_contato'
        verbose_name = 'Informações de Contato'
        verbose_name_plural = 'Informações de Contato'

    def __str__(self):
        return f'Contato - {self.whatsapp}'

    def save(self, *args, **kwargs):
        # Garantir que apenas 1 registro exista
        if not self.pk and InfoContato.objects.exists():
            raise ValidationError('Já existe um registro de informações de contato.')
        super().save(*args, **kwargs)