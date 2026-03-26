from django.db import models


class Provincia(models.Model):
    """Províncias de Angola"""
    nome = models.CharField(max_length=50, unique=True, null=False)

    class Meta:
        db_table = 'provincias'
        verbose_name = 'Província'
        verbose_name_plural = 'Províncias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Municipio(models.Model):
    """Municípios associados às Províncias"""
    nome = models.CharField(max_length=50, null=False)
    provincia = models.ForeignKey(
        'Provincia',
        on_delete=models.CASCADE,
        related_name='municipios',
        null=False
    )

    class Meta:
        db_table = 'municipios'
        verbose_name = 'Município'
        verbose_name_plural = 'Municípios'
        ordering = ['nome']
        unique_together = ['nome', 'provincia']

    def __str__(self):
        return f'{self.nome} - {self.provincia.nome}'


from django.db import models

# Create your models here.
