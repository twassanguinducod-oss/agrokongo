# accounts/views.py
"""
ViewSets para Gestão de Usuários e Autenticação JWT
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Usuario
from .serializers import (
    UsuarioSerializer,
    UsuarioRegistroSerializer,
    UsuarioLoginSerializer,
    UsuarioUpdatePasswordSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestão de Usuários.

    Endpoints:
    - POST /api/accounts/usuarios/ - Registro
    - POST /api/accounts/usuarios/login/ - Login (JWT)
    - GET /api/accounts/usuarios/me/ - Perfil atual
    - PUT /api/accounts/usuarios/me/ - Atualizar perfil
    - POST /api/accounts/usuarios/me/change-password/ - Mudar senha
    """
    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'telemovel', 'nif']
    ordering_fields = ['data_cadastro', 'username', 'rating_vendedor']
    ordering = ['-data_cadastro']

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioRegistroSerializer
        elif self.action == 'login':
            return UsuarioLoginSerializer
        elif self.action == 'change_password':
            return UsuarioUpdatePasswordSerializer
        return UsuarioSerializer

    def get_permissions(self):
        """Permissões específicas por ação"""
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
        elif self.action in ['me', 'change_password']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'list':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Cada usuário só vê o seu próprio perfil (exceto admin)"""
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return Usuario.objects.filter(id=user.id)
        return super().get_queryset()

    @extend_schema(
        summary='Registro de novo usuário',
        description='Cria um novo usuário no sistema AgroKongo e retorna tokens JWT.',
        tags=['auth'],
        request=UsuarioRegistroSerializer,
        responses={201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    )
    def create(self, request, *args, **kwargs):
        """Registro de novo usuário com retorno de tokens JWT"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Marcar como validada temporariamente ou por padrão se necessário
        # user.conta_validada = True 
        # user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UsuarioSerializer(user, context={'request': request}).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary='Login com JWT',
        description='Autentica usuário e retorna tokens de acesso (60 min) e refresh (1 dia).',
        tags=['auth'],
        request=UsuarioLoginSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            401: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        },
    )
    # accounts/views.py
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    @csrf_exempt
    def login(self, request):
        """Login com username/telemóvel/email + password, retorna tokens JWT"""
        print("🔐 LOGIN HIT!")

        serializer = UsuarioLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ✅ Aceita username, telemóvel OU email
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data['password']

        # Tenta autenticar
        user = authenticate(
            username=username if username and '@' not in username else None,
            email=email if email else (username if username and '@' in username else None),
            password=password
        )

        if not user:
            return Response(
                {'error': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.conta_validada:
            return Response(
                {'error': 'Conta não validada. Contacte o suporte.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': 'Login realizado com sucesso',
            'user': UsuarioSerializer(user, context={'request': request}).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'expires_in': 3600
            }
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Perfil do usuário atual',
        description='Obter ou atualizar perfil do usuário autenticado.',
        tags=['auth'],
        responses={200: UsuarioSerializer},
    )
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Obter ou atualizar perfil do usuário atual"""
        user = request.user

        if request.method == 'GET':
            serializer = UsuarioSerializer(user, context={'request': request})
            return Response(serializer.data)

        serializer = UsuarioSerializer(user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.verificar_e_atualizar_perfil()

        return Response(UsuarioSerializer(user, context={'request': request}).data)

    @extend_schema(
        summary='Mudar senha',
        description='Alterar senha do usuário autenticado.',
        tags=['auth'],
        request=UsuarioUpdatePasswordSerializer,
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Mudar senha do usuário atual"""
        serializer = UsuarioUpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data['senha_atual']):
            return Response(
                {'senha_atual': 'Senha atual incorreta.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['nova_senha'])
        user.save()

        return Response({'message': 'Senha atualizada com sucesso.'})

    @extend_schema(
        summary='Estatísticas do usuário',
        description='Estatísticas detalhadas do usuário (apenas admin).',
        tags=['auth'],
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request, pk=None):
        """Estatísticas do usuário (apenas admin)"""
        user = self.get_object()

        stats = {
            'total_compras': user.compras.count(),
            'total_vendas': user.vendas.count(),
            'safras_ativas': user.safras.filter(status='disponivel').count(),
            'notificacoes_nao_lidas': user.notificacoes.filter(lida=False).count(),
            'rating_medio': float(user.rating_vendedor),
        }

        return Response(stats)
