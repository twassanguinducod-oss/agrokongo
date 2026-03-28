# marketplace/tasks.py
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import Reserva, Safra
import logging

logger = logging.getLogger(__name__)

# ===========================================
# 1. CANCELAR RESERVAS EXPIRADAS (24h)
# ===========================================
@shared_task(name='marketplace.tasks.verificar_reservas_expiradas')
def verificar_reservas_expiradas():
    """
    Cancela automaticamente reservas que não foram pagas em 24h.
    Libera a quantidade_reservada na Safra original.
    """
    agora = timezone.now()
    
    # Busca reservas pendentes ou confirmadas que já passaram da data de expiração
    # skip_locked=True evita que múltiplos workers processem a mesma reserva
    reservas_expiradas = Reserva.objects.select_for_update(skip_locked=True).filter(
        status__in=['pendente', 'confirmada'],
        data_expiracao__lte=agora
    )[:100]  # Limitamos a 100 por execução para evitar travar o processo
    
    contador = 0
    for reserva in reservas_expiradas:
        try:
            with transaction.atomic():
                reserva.cancelar()
                contador += 1
                logger.info(f"Reserva #{reserva.id} cancelada por expiração de tempo (24h).")
                
                # Criar Notificação para o Comprador
                from core.models import Notificacao
                Notificacao.objects.create(
                    usuario=reserva.comprador,
                    titulo='Reserva Expirada ⏳',
                    mensagem=f'A sua reserva #{reserva.id} foi cancelada porque o pagamento não foi confirmado em 24h.',
                    tipo='erro'
                )
        except Exception as e:
            logger.error(f"Erro ao cancelar reserva #{reserva.id}: {str(e)}")
            
    return f"{contador} reservas expiradas foram canceladas."


# ===========================================
# 2. EXPIRAR SAFRAS ANTIGAS
# ===========================================
@shared_task(name='marketplace.tasks.verificar_safras_expiradas')
def verificar_safras_expiradas():
    """
    Muda o status de safras cuja data de validade ou expiração passou.
    """
    agora = timezone.now()
    
    # Safras ativas que já passaram da data de expiração
    safras_expiradas = Safra.objects.filter(
        status='active',
        data_expiracao__lte=agora
    )
    
    contador = safras_expiradas.update(status='expired')
    logger.info(f"{contador} safras marcadas como expiradas.")
    
    return f"{contador} safras expiradas."


# ===========================================
# 3. ENVIAR RESUMO DIÁRIO (MOCKUP)
# ===========================================
@shared_task(name='marketplace.tasks.enviar_resumo_diario')
def enviar_resumo_diario():
    """Gera um resumo das vendas do dia para os administradores."""
    hoje = timezone.now().date()
    vendas_hoje = Reserva.objects.filter(status='concluida', data_conclusao__date=hoje).count()
    return f"Resumo do dia {hoje}: {vendas_hoje} vendas concluídas."

@shared_task(name='marketplace.tasks.job_verificar_entregas')
def job_verificar_entregas():
    """Placeholder para auditoria de entregas estagnadas."""
    return "Verificação de entregas concluída."
