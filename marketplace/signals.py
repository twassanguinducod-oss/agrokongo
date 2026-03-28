import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Pagamento, ImagemSafra

@receiver(post_delete, sender=Pagamento)
def delete_comprovativo_on_delete(sender, instance, **kwargs):
    """Apaga o arquivo do comprovativo quando o registro de pagamento é deletado."""
    if instance.comprovativo:
        if os.path.isfile(instance.comprovativo.path):
            os.remove(instance.comprovativo.path)

@receiver(post_delete, sender=ImagemSafra)
def delete_imagem_safra_on_delete(sender, instance, **kwargs):
    """Apaga o arquivo da imagem da safra quando o registro é deletado."""
    if instance.imagem:
        # Nota: Como o campo 'imagem' em ImagemSafra pode ser um CharField ou FileField,
        # aqui assumimos a lógica de caminho de arquivo se for local.
        if os.path.isfile(instance.imagem):
            os.remove(instance.imagem)
