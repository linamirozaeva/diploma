from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import CinemaHall, Seat
from config.permissions import IsAdminOrReadOnly, IsAdminUser
from .serializers import (
    CinemaHallListSerializer, CinemaHallDetailSerializer,
    CinemaHallCreateSerializer, SeatSerializer, SeatUpdateSerializer
)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение: админы могут всё, остальные только чтение
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_admin_user

class CinemaHallViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления кинозалами
    
    list: Все пользователи (включая гостей)
    retrieve: Все пользователи
    create: Только админы
    update: Только админы
    partial_update: Только админы
    destroy: Только админы
    """
    queryset = CinemaHall.objects.all()
    permission_classes = [IsAdminOrReadOnly]  # Админы могут всё, остальные только чтение
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'rows', 'seats_per_row', 'created_at']
    
    def get_queryset(self):
        """Фильтрация залов по параметрам запроса"""
        queryset = super().get_queryset()
        
        # Все видят только активные залы
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
            # По умолчанию показываем только активные
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return CinemaHallCreateSerializer
        elif self.action == 'list':
            return CinemaHallListSerializer
        elif self.action == 'retrieve':
            return CinemaHallDetailSerializer
        return CinemaHallListSerializer
    
    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        """
        Получить все места конкретного зала
        Доступно всем пользователям
        """
        hall = self.get_object()
        seats = Seat.objects.filter(hall=hall, is_active=True).order_by('row', 'number')
        
        serializer = SeatSerializer(seats, many=True)
        return Response({
            'hall_id': hall.id,
            'hall_name': hall.name,
            'total_seats': hall.total_seats,
            'seats': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_seat_type(self, request, pk=None):
        """
        Обновить тип места - только для админов
        """
        hall = self.get_object()
        seat_id = request.data.get('seat_id')
        seat_type = request.data.get('seat_type')
        
        seat = get_object_or_404(Seat, id=seat_id, hall=hall)
        serializer = SeatUpdateSerializer(seat, data={'seat_type': seat_type}, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(SeatSerializer(seat).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_update_seats(self, request, pk=None):
        """
        Массовое обновление мест - только для админов
        """
        hall = self.get_object()
        seat_ids = request.data.get('seat_ids', [])
        seat_type = request.data.get('seat_type')
        
        seats = Seat.objects.filter(id__in=seat_ids, hall=hall)
        updated = seats.update(seat_type=seat_type)
        
        return Response({
            'message': f'Обновлено {updated} мест'
        })

class SeatViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления местами
    
    list: Все пользователи
    retrieve: Все пользователи
    create: Только админы
    update: Только админы
    partial_update: Только админы
    destroy: Только админы
    """
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    
    def get_permissions(self):
        """Динамическое определение прав доступа"""
        if self.action in ['list', 'retrieve']:
            # Просмотр доступен всем
            permission_classes = [permissions.AllowAny]
        else:
            # Изменение только админам
            permission_classes = [IsAdminUser]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Фильтрация мест"""
        queryset = super().get_queryset()
        
        # Все видят только активные места
        queryset = queryset.filter(is_active=True)
        
        # Фильтр по залу
        hall_id = self.request.query_params.get('hall')
        if hall_id:
            queryset = queryset.filter(hall_id=hall_id)
        
        return queryset
    """
    ViewSet для управления местами (только для админов)
    """
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['hall__name', 'row', 'number']
    ordering_fields = ['hall', 'row', 'number', 'seat_type']
    
    def get_queryset(self):
        """Фильтрация по параметрам запроса"""
        queryset = super().get_queryset()
        
        # Фильтр по залу
        hall_id = self.request.query_params.get('hall')
        if hall_id:
            queryset = queryset.filter(hall_id=hall_id)
        
        # Фильтр по типу
        seat_type = self.request.query_params.get('type')
        if seat_type:
            queryset = queryset.filter(seat_type=seat_type)
        
        # Фильтр по ряду
        row = self.request.query_params.get('row')
        if row:
            queryset = queryset.filter(row=row)
        
        # Фильтр по активности
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('hall', 'row', 'number')