# agrokongo/__init__.py
# Este ficheiro garante que o app Celery é carregado quando Django inicia

from .celery import app as celery_app

__all__ = ('celery_app',)