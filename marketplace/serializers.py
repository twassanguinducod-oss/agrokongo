from rest_framework import serializers
from decimal import Decimal
from .models import Produto, Safra, Transacao, HistoricoStatus, Avaliacao, TransactionStatus
from accounts.serializers import UsuarioSerializer


class ProdutoSerializer(serializers.ModelSerializer):
    """Serializer para Produtos Agrícolas"""
    safras_disponiveis = serializers.IntegerField(source='safras_rel.filter(status="disponivel").count', read_only=True)

    class Meta:
        model = Produto
        fields = ['id', 'nome', 'categoria', 'safras_disponiveis']
        read_only_fields = ['id']


class SafraSerializer(serializers.ModelSerializer):
    """Serializer para Safras"""
    produtor_nome = serializers.CharField(source='produtor.username', read_only=True)
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    valor_total_estimado = serializers.SerializerMethodField()

    class Meta:
        model = Safra
        fields = [
            'id', 'produtor', 'produtor_nome', 'produto', 'produto_nome',
            'quantidade_disponivel', 'preco_por_unidade', 'valor_total_estimado',
            'status', 'data_criacao', 'imagem', 'observacoes'
        ]
        read_only_fields = ['id', 'data_criacao', 'produtor']

    def get_valor_total_estimado(self, obj):
        if obj.quantidade_disponivel and obj.preco_por_unidade:
            return Decimal(str(obj.quantidade_disponivel)) * Decimal(str(obj.preco_por_unidade))
        return Decimal('0.00')

    def validate_quantidade_disponivel(self, value):
        if value < 0:
            raise serializers.ValidationError('Quantidade não pode ser negativa.')
        return value

    def validate_preco_por_unidade(self, value):
        if value <= 0:
            raise serializers.ValidationError('Preço deve ser maior que zero.')
        return value


class SafraCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar nova safra"""

    class Meta:
        model = Safra
        fields = ['produto', 'quantidade_disponivel', 'preco_por_unidade', 'imagem', 'observacoes']

    def create(self, validated_data):
        # Produtor é o usuário autenticado
        validated_data['produtor'] = self.context['request'].user
        return super().create(validated_data)


class HistoricoStatusSerializer(serializers.ModelSerializer):
    """Serializer para Histórico de Status"""

    class Meta:
        model = HistoricoStatus
        fields = ['id', 'status_anterior', 'status_novo', 'data_mudanca', 'observacao']
        read_only_fields = ['id', 'data_mudanca']


class AvaliacaoSerializer(serializers.ModelSerializer):
    """Serializer para Avaliações"""
    comprador_nome = serializers.CharField(source='transacao.comprador.username', read_only=True)

    class Meta:
        model = Avaliacao
        fields = ['id', 'transacao', 'nota', 'comentario', 'data_criacao', 'comprador_nome']
        read_only_fields = ['id', 'data_criacao']

    def validate_nota(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Nota deve ser entre 1 e 5.')
        return value


class TransacaoSerializer(serializers.ModelSerializer):
    """Serializer para Transações (Leitura)"""
    fatura_ref = serializers.CharField(read_only=True)
    safra = SafraSerializer(read_only=True)
    comprador = UsuarioSerializer(read_only=True)
    vendedor = UsuarioSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    historico_status = HistoricoStatusSerializer(many=True, read_only=True)
    avaliacao = AvaliacaoSerializer(read_only=True)

    class Meta:
        model = Transacao
        fields = [
            'id', 'fatura_ref', 'safra', 'comprador', 'vendedor',
            'quantidade_comprada', 'valor_total_pago', 'comissao_plataforma',
            'valor_liquido_vendedor', 'status', 'status_display',
            'data_criacao', 'data_pagamento_escrow', 'data_envio',
            'data_entrega', 'data_liquidacao', 'previsao_entrega',
            'comprovativo_path', 'transferencia_concluida',
            'historico_status', 'avaliacao'
        ]
        read_only_fields = [
            'id', 'fatura_ref', 'comissao_plataforma', 'valor_liquido_vendedor',
            'data_criacao', 'status'
        ]


class TransacaoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar nova transação"""

    class Meta:
        model = Transacao
        fields = ['safra', 'quantidade_comprada', 'comprovativo_path']

    def validate_quantidade_comprada(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantidade deve ser maior que zero.')
        return value

    def validate(self, attrs):
        safra = attrs.get('safra')
        quantidade = attrs.get('quantidade_comprada')
        request = self.context.get('request')

        if not safra:
            raise serializers.ValidationError({'safra': 'Safra é obrigatória.'})

        if safra.status != 'disponivel':
            raise serializers.ValidationError({'safra': 'Esta safra não está disponível.'})

        if quantidade > safra.quantidade_disponivel:
            raise serializers.ValidationError({
                'quantidade_comprada': f'Quantidade indisponível. Máximo: {safra.quantidade_disponivel}'
            })

        # Comprador não pode ser o próprio vendedor
        if request and request.user == safra.produtor:
            raise serializers.ValidationError({
                'safra': 'Não podes comprar a tua própria safra.'
            })

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        safra = validated_data['safra']
        quantidade = validated_data['quantidade_comprada']

        # Calcula valor total
        valor_total = Decimal(str(quantidade)) * Decimal(str(safra.preco_por_unidade))

        # Calcula comissão (5%)
        comissao = (valor_total * Decimal('0.05')).quantize(Decimal('0.01'))
        valor_liquido = valor_total - comissao

        transacao = Transacao.objects.create(
            safra=safra,
            comprador=request.user,
            vendedor=safra.produtor,
            quantidade_comprada=quantidade,
            valor_total_pago=valor_total,
            comissao_plataforma=comissao,
            valor_liquido_vendedor=valor_liquido,
            comprovativo_path=validated_data.get('comprovativo_path')
        )

        # Atualiza stock da safra
        safra.quantidade_disponivel -= quantidade
        if safra.quantidade_disponivel <= 0:
            safra.status = 'indisponivel'
        safra.save()

        return transacao


class TransacaoStatusUpdateSerializer(serializers.Serializer):
    """Serializer para atualizar status da transação"""
    status = serializers.ChoiceField(choices=TransactionStatus.choices)
    observacao = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        # Validação adicional pode ser feita aqui
        return value