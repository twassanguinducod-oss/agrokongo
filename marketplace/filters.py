import django_filters
from .models import Safra

class SafraFilter(django_filters.FilterSet):
    """
    Filtros avançados para Safras.
    Permite filtrar por preço, quantidade, categoria e localização.
    """
    # Filtros de Preço
    min_price = django_filters.NumberFilter(field_name="preco_unitario", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="preco_unitario", lookup_expr='lte')
    
    # Filtros de Quantidade
    min_qty = django_filters.NumberFilter(field_name="quantidade", lookup_expr='gte')
    
    # Filtro por Categoria (Slug do produto)
    categoria = django_filters.CharFilter(field_name="produto__categoria__slug")
    
    # Filtro por Nome do Produto
    produto_nome = django_filters.CharFilter(field_name="produto__nome", lookup_expr='icontains')

    class Meta:
        model = Safra
        fields = [
            'produto', 'provincia', 'municipio', 'status', 
            'qualidade', 'certificacao_organica', 'min_price', 
            'max_price', 'min_qty', 'categoria', 'produto_nome'
        ]
