# marketplace/tasks.py
"""
Tarefas Assíncronas do Celery para Marketplace
Processamento em background para operações pesadas.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Sum, Avg
from django.core.mail import send_mail
from decimal import Decimal
import logging

from .models import Transacao, TransactionStatus, Safra, Avaliacao
from accounts.models import Usuario

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def job_verificar_entregas(self):
    """
    Tarefa agendada para confirmar entregas estagnadas automaticamente.
    Roda a cada 1 hora via Celery Beat.
    """
    try:
        logger.info("---  Iniciando Auditoria de Entregas Automáticas ---")

        # Transações em ANÁLISE há mais de 24 horas
        limite = timezone.now() - timedelta(hours=24)
        estagnadas = Transacao.ativas().filter(
            status=TransactionStatus.ANALISE,
            data_criacao__lte=limite
        )

        count = 0
        for transacao in estagnadas:
            try:
                # Muda para ESCROW automaticamente
                transacao.mudar_status(
                    TransactionStatus.ESCROW,
                    observacao='Confirmação automática por auditoria (24h sem ação)',
                    auto_add=True
                )
                transacao.save()

                # Notifica comprador e vendedor
                enviar_notificacao_auditoria.delay(transacao.id)

                count += 1
                logger.info(f"✅ Transação {transacao.fatura_ref} atualizada para ESCROW")

            except Exception as e:
                logger.error(f"❌ Erro ao processar transação {transacao.fatura_ref}: {str(e)}")
                continue

        logger.info(f"--- ✅ Auditoria Concluída: {count} transações processadas ---")
        return f"{count} entregas verificadas."

    except Exception as exc:
        logger.error(f"❌ Erro crítico na tarefa de auditoria: {str(exc)}")
        raise self.retry(exc=exc, countdown=120)  # Retry em 2 minutos


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def enviar_fatura_email(self, transacao_id):
    """
    Tarefa assíncrona para gerar e enviar fatura por email.
    """
    try:
        transacao = Transacao.ativas().filter(id=transacao_id).first()

        if not transacao:
            logger.warning(f"Transação {transacao_id} não encontrada para envio de email")
            return "Transação não encontrada."

        logger.info(f"📧 Gerando fatura para Ref: {transacao.fatura_ref}")

        # Assunto e corpo do email
        assunto = f"Fatura AgroKongo - {transacao.fatura_ref}"
        mensagem = f"""
        Olá {transacao.comprador.username},

        Sua transação foi confirmada!

        Detalhes:
        - Fatura: {transacao.fatura_ref}
        - Produto: {transacao.safra.produto.nome}
        - Quantidade: {transacao.quantidade_comprada}
        - Valor Total: {transacao.valor_total_pago} KZ
        - Comissão: {transacao.comissao_plataforma} KZ

        Obrigado por usar AgroKongo!
        """

        # Enviar email
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email='noreply@agrokongo.ao',
            recipient_list=[transacao.comprador.email],
            fail_silently=False,
        )

        # Também envia para o vendedor
        send_mail(
            subject=f"Venda Confirmada - {transacao.fatura_ref}",
            message=f"Olá {transacao.vendedor.username},\n\nSua venda foi confirmada!\n\nValor Líquido: {transacao.valor_liquido_vendedor} KZ",
            from_email='noreply@agrokongo.ao',
            recipient_list=[transacao.vendedor.email],
            fail_silently=False,
        )

        logger.info(f"✅ Emails enviados para {transacao.comprador.email} e {transacao.vendedor.email}")
        return f"Faturas enviadas com sucesso."

    except Exception as exc:
        logger.error(f"❌ Erro ao enviar email da fatura {transacao_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)  # Retry em 5 minutos


@shared_task(bind=True, max_retries=3)
def enviar_notificacao_auditoria(self, transacao_id):
    """
    Envia notificação interna sobre auditoria automática.
    """
    from core.models import Notificacao

    try:
        transacao = Transacao.ativas().filter(id=transacao_id).first()
        if not transacao:
            return

        # Notifica comprador
        Notificacao.objects.create(
            usuario=transacao.comprador,
            mensagem=f'Auditoria automática: Sua transação {transacao.fatura_ref} foi atualizada para ESCROW.',
            link=f'/transacoes/{transacao.id}/'
        )

        # Notifica vendedor
        Notificacao.objects.create(
            usuario=transacao.vendedor,
            mensagem=f'Auditoria automática: Transação {transacao.fatura_ref} atualizada para ESCROW.',
            link=f'/transacoes/{transacao.id}/'
        )

        logger.info(f"✅ Notificações de auditoria enviadas para {transacao.fatura_ref}")

    except Exception as exc:
        logger.error(f"❌ Erro ao enviar notificação de auditoria: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def enviar_resumo_diario():
    """
    Envia resumo diário de transações para admins.
    Roda diariamente às 8 AM.
    """
    try:
        logger.info("📊 Gerando resumo diário de transações...")

        ontem = timezone.now().date() - timedelta(days=1)

        # Estatísticas do dia anterior
        transacoes_ontem = Transacao.ativas().filter(
            data_criacao__date=ontem
        )

        total_transacoes = transacoes_ontem.count()
        total_valor = transacoes_ontem.aggregate(total=Sum('valor_total_pago'))['total'] or Decimal('0.00')
        total_comissao = transacoes_ontem.aggregate(total=Sum('comissao_plataforma'))['total'] or Decimal('0.00')

        # Envia para admins
        admins = Usuario.objects.filter(tipo='admin', is_active=True)

        for admin in admins:
            send_mail(
                subject=f'Resumo Diário AgroKongo - {ontem}',
                message=f"""
                Olá {admin.username},

                Resumo de {ontem}:

                📦 Total de Transações: {total_transacoes}
                💰 Valor Total: {total_valor} KZ
                🏦 Comissão da Plataforma: {total_comissao} KZ

                AgroKongo - Marketplace Agrícola
                """,
                from_email='noreply@agrokongo.ao',
                recipient_list=[admin.email],
                fail_silently=False,
            )

        logger.info(f"✅ Resumo diário enviado para {admins.count()} admins")
        return f"Resumo enviado para {admins.count()} admins"

    except Exception as e:
        logger.error(f"❌ Erro no resumo diário: {str(e)}")
        return f"Erro: {str(e)}"


@shared_task(bind=True, max_retries=3)
def atualizar_rating_vendedor(self, vendedor_id):
    """
    Atualiza o rating médio de um vendedor após nova avaliação.
    """
    try:
        vendedor = Usuario.objects.filter(id=vendedor_id, tipo='produtor').first()

        if not vendedor:
            return "Vendedor não encontrado."

        # Calcula média de todas as avaliações
        media = Avaliacao.objects.filter(
            transacao__vendedor=vendedor
        ).aggregate(media=Avg('nota'))['media']

        if media:
            vendedor.rating_vendedor = Decimal(str(media)).quantize(Decimal('0.01'))
            vendedor.save(update_fields=['rating_vendedor'])

            logger.info(f"✅ Rating de {vendedor.username} atualizado para {vendedor.rating_vendedor}")
            return f"Rating atualizado: {vendedor.rating_vendedor}"

        return "Sem avaliações para calcular média."

    except Exception as exc:
        logger.error(f"❌ Erro ao atualizar rating: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def limpar_transacoes_canceladas():
    """
    Limpa transações canceladas com mais de 30 dias (soft delete).
    """
    try:
        logger.info("🧹 Limpando transações canceladas antigas...")

        limite = timezone.now() - timedelta(days=30)

        transacoes = Transacao.ativas().filter(
            status=TransactionStatus.CANCELADO,
            data_criacao__lte=limite
        )

        count = transacoes.count()

        # Soft delete
        transacoes.update(deleted_at=timezone.now())

        logger.info(f"✅ {count} transações canceladas arquivadas")
        return f"{count} transações arquivadas"

    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {str(e)}")
        return f"Erro: {str(e)}"