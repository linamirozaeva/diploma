from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from config.permissions import IsAdminUser, IsOwnerOrAdmin
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя - доступно всем"""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование своего профиля - только владелец"""
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями
    
    list: Только админы
    retrieve: Админы или сам пользователь
    create: Только админы
    update: Только админы
    partial_update: Только админы
    destroy: Только админы
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """Динамическое определение прав доступа"""
        if self.action == 'create':
            # Создание пользователя - только админы
            permission_classes = [IsAdminUser]
        elif self.action in ['list', 'destroy']:
            # Список и удаление - только админы
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Просмотр и редактирование - владелец или админ
            permission_classes = [IsOwnerOrAdmin]
        else:
            # По умолчанию - только админы
            permission_classes = [IsAdminUser]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Получить информацию о текущем пользователе
        Доступно любому авторизованному пользователю
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def set_admin(self, request, pk=None):
        """
        Сделать пользователя администратором
        Только для админов
        """
        user = self.get_object()
        user.user_type = 'admin'
        user.is_staff = True
        user.save()
        return Response({
            'status': 'success',
            'message': f'Пользователь {user.username} теперь администратор'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def set_guest(self, request, pk=None):
        """
        Сделать пользователя гостем
        Только для админов
        """
        user = self.get_object()
        user.user_type = 'guest'
        user.is_staff = False
        user.save()
        return Response({
            'status': 'success',
            'message': f'Пользователь {user.username} теперь гость'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_active(self, request, pk=None):
        """
        Активировать/деактивировать пользователя
        Только для админов
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        status_text = 'активирован' if user.is_active else 'деактивирован'
        return Response({
            'status': 'success',
            'message': f'Пользователь {user.username} {status_text}'
        })