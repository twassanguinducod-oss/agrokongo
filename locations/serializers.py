from rest_framework import serializers
from .models import Provincia, Municipio


class MunicipioSerializer(serializers.ModelSerializer):
    """Serializer para Municípios"""
    provincia_nome = serializers.CharField(source='provincia.nome', read_only=True)

    class Meta:
        model = Municipio
        fields = ['id', 'nome', 'provincia', 'provincia_nome']
        read_only_fields = ['id']


class ProvinciaSerializer(serializers.ModelSerializer):
    """Serializer para Províncias"""
    municipios = MunicipioSerializer(many=True, read_only=True)
    municipios_count = serializers.IntegerField(source='municipios.count', read_only=True)

    class Meta:
        model = Provincia
        fields = ['id', 'nome', 'municipios', 'municipios_count']
        read_only_fields = ['id']


class ProvinciaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem"""

    class Meta:
        model = Provincia
        fields = ['id', 'nome']