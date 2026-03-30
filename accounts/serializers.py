# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, Levantamento


# ===========================================
# USUÁRIO SERIALIZERS
# ===========================================
class UsuarioPublicoSerializer(serializers.ModelSerializer):
    """
    Serializer para exibição pública (Vitrine/Marketplace).
    Exclui dados sensíveis como IBAN, Saldo e NIF.
    """

    class Meta:
        model = Usuario
        # ✅ REMOVIDO: rating_vendedor (não existe no model)
        fields = ['id', 'username', 'foto_perfil', 'tipo', 'provincia', 'municipio']


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer completo e PRIVADO.
    Usado apenas no endpoint /me/ ou pelo próprio usuário.
    """

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'telemovel', 'tipo', 'nif', 'iban', 'banco',
            'saldo_disponivel', 'vendas_concluidas', 'perfil_completo', 'conta_validada',
            'provincia', 'municipio', 'data_cadastro', 'first_name', 'last_name', 'foto_perfil'
        ]
        read_only_fields = ['id', 'saldo_disponivel', 'vendas_concluidas', 'conta_validada', 'data_cadastro']


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro Passo 1"""
    senha = serializers.CharField(write_only=True, required=True, min_length=6)
    senha_confirmacao = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'telemovel', 'senha', 'senha_confirmacao']
        extra_kwargs = {'username': {'required': False}}

    def validate(self, attrs):
        if attrs['senha'] != attrs['senha_confirmacao']:
            raise serializers.ValidationError({'senha_confirmacao': 'As senhas não coincidem.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('senha_confirmacao')
        senha = validated_data.pop('senha')
        username = validated_data.get('username') or validated_data.get('telemovel')
        user = Usuario.objects.create_user(username=username, password=senha, **validated_data)
        user.conta_validada = True
        user.save()
        return user


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """Serializer para registro Passo 2"""

    class Meta:
        model = Usuario
        fields = ['tipo', 'first_name', 'last_name', 'nif', 'iban', 'banco', 'provincia', 'municipio', 'foto_perfil']
        extra_kwargs = {'tipo': {'required': True}}


class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para login"""
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    telemovel = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=True)


class UsuarioUpdatePasswordSerializer(serializers.Serializer):
    """Serializer para mudar senha"""
    senha_atual = serializers.CharField(write_only=True, required=True)
    nova_senha = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    nova_senha_confirmacao = serializers.CharField(write_only=True, required=True)


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem (Admin)"""

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'tipo', 'telemovel', 'saldo_disponivel', 'conta_validada']


# ===========================================
# LEVANTAMENTO SERIALIZERS
# ===========================================
class LevantamentoSerializer(serializers.ModelSerializer):
    """Serializer para pedidos de levantamento"""
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Levantamento
        # ✅ REMOVIDO: banco_destino (não existe no model)
        fields = [
            'id', 'usuario', 'usuario_nome', 'valor', 'iban_destino',
            'status', 'data_pedido', 'data_processamento',
            'comprovativo_transferencia', 'observacoes'
        ]
        read_only_fields = ['id', 'usuario', 'status', 'data_pedido', 'data_processamento']

    def validate_valor(self, value):
        if value < 500:
            raise serializers.ValidationError('O valor mínimo de levantamento é 500 Kz.')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if user.saldo_disponivel < attrs['valor']:
            raise serializers.ValidationError({'valor': 'Saldo insuficiente para realizar este levantamento.'})
        return attrs

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        validated_data['iban_destino'] = validated_data.get('iban_destino') or validated_data['usuario'].iban

        if not validated_data['iban_destino']:
            raise serializers.ValidationError({'iban_destino': 'Informe o IBAN de destino no seu perfil ou no pedido.'})

        return super().create(validated_data)
