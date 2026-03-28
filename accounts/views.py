# accounts/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.cache import cache # ✅ Importar cache
from .models import Usuario, Levantamento
from marketplace.models import Safra, Reserva, Pagamento
from core.models import Notificacao, Mensagem
from .serializers import (
    UsuarioSerializer,
    UsuarioRegistroSerializer,
    UsuarioPerfilSerializer,
    UsuarioLoginSerializer,
    UsuarioUpdatePasswordSerializer,
    UsuarioListSerializer,
    LevantamentoSerializer,
    UsuarioPublicoSerializer, # ✅ Importar o novo serializer público
)


# ===========================================
# USUÁRIO VIEWSET (GESTÃO E DASHBOARD)
# ===========================================
class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestão de usuários e Dashboards."""
    queryset = Usuario.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioRegistroSerializer
        elif self.action == 'list': # ✅ Usar o ListSerializer para listagem de admin
            return UsuarioListSerializer
        elif self.action == 'retrieve': # ✅ Usar o PublicoSerializer para visualização pública
            return UsuarioPublicoSerializer
        return UsuarioSerializer

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
        elif self.action in ['me', 'update_perfil', 'dashboard']: # ✅ Adicionar dashboard aqui
            return [permissions.IsAuthenticated()]
        elif self.action in ['list', 'retrieve']: # ✅ List e Retrieve podem ser públicos ou restritos
            return [permissions.AllowAny()] # Ou IsAdminUser para list, IsAuthenticated para retrieve
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login com telemóvel/email + senha."""
        serializer = UsuarioLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data.get('username') or 
                     serializer.validated_data.get('email') or 
                     serializer.validated_data.get('telemovel'),
            password=serializer.validated_data['password']
        )

        if not user:
            return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.conta_validada:
            return Response({'error': 'Conta não validada.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UsuarioSerializer(user, context={'request': request}).data,
            'tokens': {'access': str(refresh.access_token), 'refresh': str(refresh)}
        })

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        ENDPOINT CENTRAL DE ESTATÍSTICAS (Dashboard) com CACHE.
        Retorna dados baseados no tipo de usuário.
        """
        user = request.user
        cache_key = f'dashboard_stats_{user.tipo}_{user.id}' # Chave de cache única por usuário e tipo
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        data = {
            'tipo_perfil': user.tipo,
            'notificacoes_nao_lidas': Notificacao.objects.filter(usuario=user, lida=False).count(),
        }

        # --- DASHBOARD PRODUTOR ---
        if user.tipo == 'produtor':
            safras = Safra.objects.filter(produtor=user)
            reservas = Reserva.objects.filter(safra__produtor=user)
            
            data.update({
                'saldo_disponivel': user.saldo_disponivel,
                'vendas_concluidas': user.vendas_concluidas,
                'safras_ativas': safras.filter(status='active').count(),
                'valor_em_escrow': reservas.filter(status='paga').aggregate(Sum('preco_total'))['preco_total__sum'] or 0,
                'pedidos_para_entrega': reservas.filter(status='paga').count(),
            })

        # --- DASHBOARD COMPRADOR ---
        elif user.tipo == 'comprador':
            compras = Reserva.objects.filter(comprador=user)
            
            data.update({
                'total_reservas': compras.count(),
                'compras_concluidas': compras.filter(status='concluida').count(),
                'aguardando_pagamento': compras.filter(status='confirmada').count(),
                'total_gasto': compras.filter(status='concluida').aggregate(Sum('preco_total'))['preco_total__sum'] or 0,
                'favoritos': 0, # Implementar futuramente
            })

        # --- DASHBOARD ADMIN ---
        elif user.tipo == 'admin':
            data.update({
                'total_usuarios': Usuario.objects.count(),
                'pagamentos_pendentes': Pagamento.objects.filter(status='pendente').count(),
                'reservas_recebidas_aguardando_liberacao': Reserva.objects.filter(status='recebida').count(),
                'mensagens_suporte_pendentes': Mensagem.objects.filter(status='pendente').count(),
                'gmv_total': Reserva.objects.filter(status='concluida').aggregate(Sum('preco_total'))['preco_total__sum'] or 0,
                'comissao_total_acumulada': Reserva.objects.filter(status='concluida').aggregate(Sum('comissao_plataforma'))['comissao_plataforma__sum'] or 0,
            })
        
        cache.set(cache_key, data, timeout=300) # Cache por 5 minutos (300 segundos)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UsuarioSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_perfil(self, request):
        serializer = UsuarioPerfilSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        request.user.verificar_e_atualizar_perfil()
        return Response(UsuarioSerializer(request.user).data)


# ===========================================
# LEVANTAMENTO VIEWSET (SAQUE DE SALDO)
# ===========================================
class LevantamentoViewSet(viewsets.ModelViewSet):
    """ViewSet para pedidos de levantamento de saldo."""
    serializer_class = LevantamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.tipo == 'admin':
            return Levantamento.objects.all()
        return Levantamento.objects.filter(usuario=self.request.user)

    def get_permissions(self):
        if self.action in ['aprovar', 'rejeitar']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.tipo != 'produtor':
            raise PermissionError('Apenas produtores podem solicitar levantamentos de saldo.')
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        levantamento = self.get_object()
        comprovativo = request.data.get('comprovativo', '')
        
        try:
            levantamento.aprovar(admin=request.user, comprovativo=comprovativo)
            
            Notificacao.objects.create(
                usuario=levantamento.usuario,
                titulo='Levantamento Concluído! ✅',
                mensagem=f'O seu pedido de levantamento de {levantamento.valor} Kz foi processado com sucesso. Verifique a sua conta bancária.',
                tipo='sucesso'
            )
            
            return Response({
                'success': True, 
                'message': 'Levantamento aprovado e saldo subtraído do produtor.',
                'status': levantamento.status
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def rejeitar(self, request, pk=None):
        levantamento = self.get_object()
        motivo = request.data.get('motivo', 'Motivo não especificado.')
        
        try:
            levantamento.rejeitar(admin=request.user, motivo=motivo)
            
            Notificacao.objects.create(
                usuario=levantamento.usuario,
                titulo='Levantamento Rejeitado ❌',
                mensagem=f'O seu pedido de levantamento de {levantamento.valor} Kz foi rejeitado. Motivo: {motivo}',
                tipo='erro'
            )
            
            return Response({'success': True, 'message': 'Levantamento rejeitado.', 'motivo': motivo})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
