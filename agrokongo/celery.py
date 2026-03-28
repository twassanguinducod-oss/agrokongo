# agrokongo/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Define o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrokongo.settings')

# Cria a instância do Celery
app = Celery('agrokongo')

# Carrega configurações do Django (prefixo CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descobre tarefas em todos os apps instalados
app.autodiscover_tasks()

# ===========================================
# Configuração de Tarefas Agendadas (Celery Beat)
# ===========================================
app.conf.beat_schedule = {
    # ⏱️ CANCELAR RESERVAS EXPIRADAS (A cada 30 minutos)
    'cancelar-reservas-expiradas-30m': {
        'task': 'marketplace.tasks.verificar_reservas_expiradas',
        'schedule': 1800.0,  # 30 minutos em segundos
    },

    # ⏱️ EXPIRAR SAFRAS ANTIGAS (Diariamente às 00:05)
    'expirar-safras-diario': {
        'task': 'marketplace.tasks.verificar_safras_expiradas',
        'schedule': crontab(hour=0, minute=5),
    },

    # Auditoria de entregas estagnadas (A cada 2 horas)
    'auditoria-entregas-2h': {
        'task': 'marketplace.tasks.job_verificar_entregas',
        'schedule': crontab(minute=0, hour='*/2'),
    },

    # Enviar resumo diário de transações (Diário às 8 AM)
    'resumo-diario-transacoes': {
        'task': 'marketplace.tasks.enviar_resumo_diario',
        'schedule': crontab(hour=8, minute=0),
    },
}

# ===========================================
# Configurações Adicionais
# ===========================================
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Luanda',
    enable_utc=False,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return 'Celery está funcional! ✅'
