from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import re
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para leitura/edição de perfil de usuário"""
    provincia_nome = serializers.CharField(source='provincia.nome', read_only=True)
    municipio_nome = serializers.CharField(source='municipio.nome', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'telemovel', 'tipo', 'nif', 'iban',
            'rating_vendedor', 'vendas_concluidas', 'foto_perfil', 'documento_pdf',
            'perfil_completo', 'conta_validada', 'provincia', 'municipio',
            'provincia_nome', 'municipio_nome', 'saldo_disponivel', 'data_cadastro',
            'first_name', 'last_name'
        ]
        read_only_fields = [
            'id', 'data_cadastro', 'saldo_disponivel', 'rating_vendedor',
            'vendas_concluidas', 'conta_validada'
        ]


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de novos usuários"""
    senha = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'}
    )
    senha_confirmacao = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'telemovel', 'senha', 'senha_confirmacao',
            'tipo', 'nif', 'first_name', 'last_name'
        ]
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True},
            'telemovel': {'required': True},
            'tipo': {'required': False},
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_telemovel(self, value):
        """Valida formato de telemóvel angolano"""
        num = re.sub(r'\D', '', value)
        if num.startswith('244'):
            num = num[3:]
        if not re.match(r'^9\d{8}$', num):
            raise serializers.ValidationError('Formato de telemóvel angolano inválido (9xxxxxxxx).')
        
        if Usuario.objects.filter(telemovel=value).exists():
            raise serializers.ValidationError('Este número de telemóvel já está registrado.')
        return value

    def validate_senha(self, value):
        """Valida a senha usando os validadores do Django"""
        try:
            # Passamos o usuário como None pois ele ainda não existe
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Valida se as senhas coincidem e define o username"""
        if attrs.get('senha') != attrs.get('senha_confirmacao'):
            raise serializers.ValidationError({'senha_confirmacao': 'As senhas não coincidem.'})

        # Define username como telemovel se não for fornecido
        if not attrs.get('username'):
            attrs['username'] = attrs.get('telemovel')

        # Verifica se o username já existe
        if Usuario.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Este nome de usuário ou telemóvel já está em uso.'})

        # Valida tipo de usuário (se fornecido)
        tipo = attrs.get('tipo')
        if tipo and tipo not in ['admin', 'produtor', 'comprador']:
            raise serializers.ValidationError({'tipo': 'Tipo de usuário inválido.'})

        return attrs

    def create(self, validated_data):
        """Cria usuário com senha hasheada automaticamente"""
        validated_data.pop('senha_confirmacao')
        senha = validated_data.pop('senha')

        # Lógica para simplificar o Passo 1 do registro
        username = validated_data.get('username') or validated_data.get('telemovel')
        email = validated_data.get('email', '')
        tipo = validated_data.get('tipo', 'produtor')

        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            telemovel=validated_data['telemovel'],
            tipo=tipo,
            nif=validated_data.get('nif'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=senha
        )

        # Por padrão para facilitar testes, vamos validar a conta (opcional)
        # Em produção, isto seria feito via SMS ou Admin
        usuario.conta_validada = True 
        usuario.save()

        # Verifica se o perfil está completo
        usuario.verificar_e_atualizar_perfil()

        return usuario



class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para login com username/telemóvel/email + password"""
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    telemovel = serializers.CharField(required=False, max_length=9)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        # Pelo menos um campo é obrigatório
        if not data.get('username') and not data.get('email') and not data.get('telemovel'):
            raise serializers.ValidationError(
                'Informe username, email ou telemóvel para fazer login.'
            )
        return data


class UsuarioUpdatePasswordSerializer(serializers.Serializer):
    """Serializer para mudar senha do usuário"""
    senha_atual = serializers.CharField(write_only=True, required=True)
    nova_senha = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    nova_senha_confirmacao = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['nova_senha'] != attrs['nova_senha_confirmacao']:
            raise serializers.ValidationError({"nova_senha": "As novas senhas não coincidem."})
        return attrs
