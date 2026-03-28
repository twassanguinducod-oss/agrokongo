# marketplace/serializers.py
from rest_framework import serializers
from .models import Categoria, Produto, Safra, Reserva, Pagamento
from accounts.serializers import UsuarioPublicoSerializer
from drf_spectacular.utils import extend_schema_field


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug', 'ativa'] # ✅ Whitelist em vez de __all__

class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'slug', 'categoria_nome', 'categoria']

# ===========================================
# SAFRA SERIALIZERS - PROTEÇÃO DE DADOS
# ===========================================
class SafraListSerializer(serializers.ModelSerializer):
    produtor_nome = serializers.CharField(source='produtor.username', read_only=True)
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    
    quantidade_disponivel = serializers.SerializerMethodField()
    @extend_schema_field(float)
    def get_quantidade_disponivel(self, obj): return float(obj.quantidade_disponivel())

    class Meta:
        model = Safra
        fields = ['id', 'titulo', 'produtor_nome', 'produto_nome', 'quantidade', 'unidade_medida', 'preco_unitario', 'status', 'quantidade_disponivel', 'data_criacao']

class SafraDetalheSerializer(serializers.ModelSerializer):
    # 🛡️ SEGURANÇA: Não expõe IBAN/Saldo do produtor para o comprador
    produtor = UsuarioPublicoSerializer(read_only=True) 
    produto = ProdutoSerializer(read_only=True)
    
    # Campo calculado com precisão
    quantidade_disponivel = serializers.SerializerMethodField()
    @extend_schema_field(float)
    def get_quantidade_disponivel(self, obj): return float(obj.quantidade_disponivel())

    class Meta:
        model = Safra
        fields = [
            'id', 'titulo', 'produtor', 'produto', 'quantidade', 'preco_unitario', 
            'quantidade_disponivel', 'status', 'data_criacao'
        ] # ✅ Whitelist explícita

# ===========================================
# RESERVA E PAGAMENTO (MANTIDOS COM PROTEÇÃO)
# ===========================================
class ReservaSerializer(serializers.ModelSerializer):
    comprador = UsuarioPublicoSerializer(read_only=True) # 🛡️ SEGURANÇA: Não expõe dados sensíveis
    class Meta:
        model = Reserva
        fields = [
            'id', 'safra', 'comprador', 'quantidade', 'preco_total', 
            'status', 'valor_liquido_vendedor', 'comissao_plataforma'
        ]
        read_only_fields = ['status', 'valor_liquido_vendedor', 'comissao_plataforma']

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = ['id', 'reserva', 'valor', 'comprovativo', 'status', 'data_criacao']
        read_only_fields = ['status', 'data_criacao']

    def validate_reserva(self, value):
        # Validação extra no serializer para feedback instantâneo ao frontend
        if value.status not in ['pendente', 'confirmada']:
            raise serializers.ValidationError('Esta reserva não aceita mais pagamentos.')
        return value
