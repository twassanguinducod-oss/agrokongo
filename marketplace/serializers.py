# marketplace/serializers.py
from rest_framework import serializers
from .models import Categoria, Produto, Safra, Reserva, Pagamento, ImagemSafra
from accounts.serializers import UsuarioPublicoSerializer
from drf_spectacular.utils import extend_schema_field


# ===========================================
# CATEGORIA
# ===========================================
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug', 'ativa']


# ===========================================
# PRODUTO
# ===========================================
class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = Produto
        fields = ['id', 'nome', 'slug', 'categoria_nome', 'categoria']


# ===========================================
# IMAGEM SAFRA
# ===========================================
class ImagemSafraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemSafra
        fields = ['id', 'safra', 'imagem', 'legenda', 'principal', 'ordem', 'data_upload']


# ===========================================
# SAFRA LIST (PARA LISTAGEM)
# ===========================================
class SafraListSerializer(serializers.ModelSerializer):
    produtor_nome = serializers.CharField(source='produtor.username', read_only=True)
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    quantidade_disponivel = serializers.SerializerMethodField()

    @extend_schema_field(float)
    def get_quantidade_disponivel(self, obj):
        return float(obj.quantidade_disponivel())

    class Meta:
        model = Safra
        fields = [
            'id', 'titulo', 'produtor_nome', 'produto_nome',
            'quantidade', 'unidade_medida', 'preco_unitario',
            'status', 'quantidade_disponivel', 'data_criacao'
        ]


# ===========================================
# SAFRA DETALHE (PARA VISUALIZAÇÃO)
# ===========================================
class SafraDetalheSerializer(serializers.ModelSerializer):
    produtor = UsuarioPublicoSerializer(read_only=True)
    produto = ProdutoSerializer(read_only=True)
    quantidade_disponivel = serializers.SerializerMethodField()

    @extend_schema_field(float)
    def get_quantidade_disponivel(self, obj):
        return float(obj.quantidade_disponivel())

    class Meta:
        model = Safra
        fields = [
            'id', 'titulo', 'produtor', 'produto', 'descricao',
            'quantidade', 'unidade_medida', 'preco_unitario',
            'quantidade_disponivel', 'status',
            'data_criacao', 'data_atualizacao'
        ]


# ===========================================
# SAFRA (PARA CRIAÇÃO/EDIÇÃO)
# ===========================================
class SafraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Safra
        fields = [
            'id', 'produtor', 'produto', 'titulo', 'descricao',
            'quantidade', 'unidade_medida', 'preco_unitario',
            'status', 'data_criacao'
        ]
        read_only_fields = ['produtor', 'status']


# ===========================================
# RESERVA LIST
# ===========================================
class ReservaListSerializer(serializers.ModelSerializer):
    safra_titulo = serializers.CharField(source='safra.titulo', read_only=True)
    safra_produto = serializers.CharField(source='safra.produto.nome', read_only=True)
    safra_produtor_nome = serializers.CharField(source='safra.produtor.username', read_only=True)
    pagamento_status = serializers.CharField(source='pagamento.status', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'safra_titulo', 'safra_produto', 'safra_produtor_nome',
            'quantidade', 'preco_total', 'valor_liquido_vendedor',
            'comissao_plataforma', 'status', 'pagamento_status',
            'fatura_ref', 'data_reserva', 'data_expiracao'
        ]


# ===========================================
# RESERVA DETALHE
# ===========================================
class ReservaDetalheSerializer(serializers.ModelSerializer):
    comprador = UsuarioPublicoSerializer(read_only=True)
    safra_titulo = serializers.CharField(source='safra.titulo', read_only=True)
    safra_produto = serializers.CharField(source='safra.produto.nome', read_only=True)
    safra_produtor = UsuarioPublicoSerializer(source='safra.produtor', read_only=True)
    pagamento_status = serializers.CharField(source='pagamento.status', read_only=True)
    pagamento_comprovativo = serializers.CharField(source='pagamento.comprovativo', read_only=True)
    pagamento_valor = serializers.DecimalField(source='pagamento.valor', read_only=True, max_digits=14,
                                               decimal_places=2)

    class Meta:
        model = Reserva
        fields = [
            'id', 'safra', 'safra_titulo', 'safra_produto', 'safra_produtor',
            'comprador', 'quantidade', 'unidade_medida', 'preco_unitario',
            'preco_total', 'valor_liquido_vendedor', 'comissao_plataforma',
            'status', 'fatura_ref',
            'pagamento_status', 'pagamento_comprovativo', 'pagamento_valor',
            'observacoes_comprador', 'observacoes_vendedor',
            'data_reserva', 'data_expiracao', 'data_atualizacao'
        ]


# ===========================================
# RESERVA (PARA CRIAÇÃO)
# ===========================================
class ReservaSerializer(serializers.ModelSerializer):
    comprador = UsuarioPublicoSerializer(read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'safra', 'comprador', 'quantidade', 'preco_total',
            'status', 'valor_liquido_vendedor', 'comissao_plataforma',
            'observacoes_comprador'
        ]
        read_only_fields = ['comprador', 'status', 'valor_liquido_vendedor', 'comissao_plataforma']

    def validate_quantidade(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantidade deve ser maior que zero.')
        safra = self.initial_data.get('safra')
        if safra:
            disponivel = safra.quantidade_disponivel()
            if value > disponivel:
                raise serializers.ValidationError(
                    f'Quantidade indisponível. Apenas {disponivel} {safra.unidade_medida} disponível(is).'
                )
        return value


# ===========================================
# PAGAMENTO
# ===========================================
class PagamentoSerializer(serializers.ModelSerializer):
    reserva_fatura_ref = serializers.CharField(source='reserva.fatura_ref', read_only=True)
    reserva_valor = serializers.DecimalField(source='reserva.preco_total', read_only=True, max_digits=14,
                                             decimal_places=2)

    class Meta:
        model = Pagamento
        fields = [
            'id', 'reserva', 'reserva_fatura_ref', 'reserva_valor',
            'valor', 'comprovativo', 'metodo', 'referencia_bancaria',
            'status', 'data_criacao'
        ]
        read_only_fields = ['status', 'data_criacao', 'reserva_fatura_ref', 'reserva_valor']

    def validate_comprovativo(self, value):
        if value:
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            ext = value.name[-4:].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f'Formato não permitido. Use: {", ".join(allowed_extensions)}'
                )
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError('Ficheiro muito grande. Máximo 5MB.')
        return value

    def validate_reserva(self, value):
        if value.status not in ['pendente', 'confirmada']:
            raise serializers.ValidationError('Esta reserva não aceita mais pagamentos.')
        return value

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError('Valor deve ser maior que zero.')
        reserva = self.initial_data.get('reserva')
        if reserva and value != reserva.preco_total:
            raise serializers.ValidationError(
                f'Valor deve ser igual ao total da reserva ({reserva.preco_total} Kz).'
            )
        return value