from django.contrib import admin
from .models import Provincia, Municipio


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'municipios_count']
    list_display_links = ['nome']
    search_fields = ['nome']
    ordering = ['nome']

    def municipios_count(self, obj):
        return obj.municipios.count()

    municipios_count.short_description = 'Municípios'


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'provincia']
    list_display_links = ['nome']
    search_fields = ['nome', 'provincia__nome']
    list_filter = ['provincia']
    ordering = ['provincia__nome', 'nome']