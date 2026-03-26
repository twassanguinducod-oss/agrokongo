# core/tasks.py
"""
Tarefas Assíncronas do Celery para Core
Notificações, logs e manutenção.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
import logging

from .models import Notificacao, Mensagem, LogAuditoria
from accounts.models import Usuario

logger = logging.getLogger(__name__)


@shared_task
def limpar_sessoes_expiradas():
    """
    Limpa sessões expiradas do banco de dados.
    Roda diariamente às 3 AM.
    """
    try:
        from django.contrib.sessions.models import Session

        logger.info("🧹 Limpando sessões expiradas...")

        # Django já limpa automaticamente, mas podemos forçar
        Session.objects.filter(expire_date__lt=timezone.now()).delete()

        logger.info("✅ Sessões expiradas limpas")
        return "Sessões limpas"

    except Exception as e:
        logger.error(f"❌ Erro na limpeza de sessões: {str(e)}")
        return f"Erro: {str(e)}"


@shared_task
def limpar_notificacoes_antigas():
    """
    Limpa notificações lidas com mais de 90 dias.
    """
    try:
        logger.info("🧹 Limpando notificações antigas...")

        limite = timezone.now() - timedelta(days=90)

        count = Notificacao.objects.filter(
            lida=True,
            data_criacao__lte=limite
        ).count()

        Notificacao.objects.filter(
            lida=True,
            data_criacao__lte=limite
        ).delete()

        logger.info(f"✅ {count} notificações antigas removidas")
        return f"{count} notificações removidas"

    except Exception as e:
        logger.error(f"❌ Erro na limpeza de notificações: {str(e)}")
        return f"Erro: {str(e)}"


@shared_task(bind=True, max_retries=3)
def enviar_notificacao_push(self, usuario_id, mensagem, link=None):
    """
    Envia notificação para um usuário específico.
    """
    try:
        usuario = Usuario.objects.filter(id=usuario_id).first()

        if not usuario:
            return "Usuário não encontrado."

        Notificacao.objects.create(
            usuario=usuario,
            mensagem=mensagem,
            link=link
        )

        logger.info(f"✅ Notificação enviada para {usuario.username}")
        return "Notificação criada"

    except Exception as exc:
        logger.error(f"❌ Erro ao enviar notificação: {str(exc)}")
        raise self.retry(exc=exc, countdown=30)


@shared_task
def criar_log_auditoria(usuario_id, acao, detalhes=None, ip=None):
    """
    Cria registro de log de auditoria.
    """
    try:
        usuario = Usuario.objects.filter(id=usuario_id).first()

        LogAuditoria.objects.create(
            usuario=usuario,
            acao=acao,
            detalhes=detalhes,
            ip=ip
        )

        return "Log criado"

    except Exception as e:
        logger.error(f"❌ Erro ao criar log: {str(e)}")
        return f"Erro: {str(e)}"