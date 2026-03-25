from django.db import models
from django.utils import timezone


class Notificacao(models.Model):
    """Sistema de Notificações do Usuário"""
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.CharField(max_length=255, null=False)
    link = models.CharField(max_length=255, null=True, blank=True)
    lida = models.BooleanField(default=False, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificacoes'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'{self.usuario.username}: {self.mensagem[:50]}'


class Mensagem(models.Model):
    """Mensagens entre Usuários (Chat por Transação)"""
    transacao = models.ForeignKey('marketplace.Transacao', on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='mensagens_recebidas')
    conteudo = models.TextField(null=False)
    data_envio = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        db_table = 'mensagens'
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['data_envio']

    def __str__(self):
        return f'{self.remetente.username} → {self.destinatario.username}'


class LogAuditoria(models.Model):
    """Logs de Auditoria do Sistema"""
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=100, null=False)
    detalhes = models.TextField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'logs_auditoria'
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'{self.acao} - {self.data_criacao}'


class AlertaPreferencia(models.Model):
    """Alertas de Preferência de Produto"""
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE)
    produto = models.ForeignKey('marketplace.Produto', on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alertas_preferencias'
        verbose_name = 'Alerta de Preferência'
        unique_together = ['usuario', 'produto']

    def __str__(self):
        return f'{self.usuario.username} - {self.produto.nome}'


from django.db import models

# Create your models here.
