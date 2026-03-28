# marketplace/apps.py
from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'
    verbose_name = 'Marketplace'

    def ready(self):
        """Carrega os signals de limpeza de ficheiros ao iniciar a app."""
        import marketplace.signals
