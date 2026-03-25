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
    # Auditoria de entregas estagnadas (a cada 1 hora)
    'auditoria-entregas-cada-hora': {
        'task': 'marketplace.tasks.job_verificar_entregas',
        'schedule': crontab(minute=0, hour='*/1'),  # A cada hora
        'options': {'queue': 'celery'}
    },

    # Limpeza de sessões expiradas (diário às 3 AM)
    'limpar-sessoes-diario': {
        'task': 'core.tasks.limpar_sessoes_expiradas',
        'schedule': crontab(hour=3, minute=0),  # 3 AM
        'options': {'queue': 'celery'}
    },

    # Enviar resumo diário de transações (diário às 8 AM)
    'resumo-diario-transacoes': {
        'task': 'marketplace.tasks.enviar_resumo_diario',
        'schedule': crontab(hour=8, minute=0),  # 8 AM
        'options': {'queue': 'celery'}
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
    task_time_limit=300,  # 5 minutos máximo por tarefa
    task_soft_time_limit=240,  # 4 minutos soft limit
    worker_prefetch_multiplier=1,  # Processa uma tarefa de cada vez
    worker_max_tasks_per_child=1000,  # Recicla workers após 1000 tarefas
)


# ===========================================
# Debug Task (para testes)
# ===========================================
@app.task(bind=True)
def debug_task(self):
    """Tarefa de teste para verificar se Celery está funcional."""
    print(f'Request: {self.request!r}')
    return 'Celery está funcional! ✅'