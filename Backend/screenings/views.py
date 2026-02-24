from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from config.permissions import IsAdminUser
from .models import Screening
from .serializers import (
    ScreeningListSerializer, ScreeningDetailSerializer,
    ScreeningCreateUpdateSerializer
)
from cinemas.models import Seat
from bookings.models import Booking

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение: админы могут всё, остальные только чтение
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_admin_user

class ScreeningViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления сеансами
    """
    queryset = Screening.objects.all()
    serializer_class = ScreeningListSerializer
    
    def get_permissions(self):
        """Динамическое определение прав доступа"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Только админы могут изменять
            from rest_framework.permissions import IsAdminUser
            return [IsAdminUser()]
        # Остальные могут просматривать
        from rest_framework.permissions import AllowAny
        return [AllowAny()]
    
    def get_queryset(self):
        """Фильтрация сеансов"""
        queryset = super().get_queryset()
        
        # Все видят только активные сеансы
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
            queryset = queryset.filter(is_active=True)
        
        # Фильтр по дате
        date = self.request.query_params.get('date')
        if date:
            from datetime import datetime
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date=date_obj)
            except ValueError:
                pass
        
        return queryset.order_by('start_time')
    
    def create(self, request, *args, **kwargs):
        """Создание сеанса"""
        try:
            # Проверка прав
            if not request.user or not request.user.is_staff:
                return Response(
                    {'detail': 'Только администраторы могут создавать сеансы'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Создаём объект
            screening = Screening.objects.create(
                movie_id=request.data.get('movie'),
                hall_id=request.data.get('hall'),
                start_time=request.data.get('start_time'),
                end_time=request.data.get('end_time'),
                price_standard=request.data.get('price_standard', 250),
                price_vip=request.data.get('price_vip', 350),
                is_active=True
            )
            
            # Возвращаем созданный объект
            serializer = self.get_serializer(screening)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """Информация о доступных местах"""
        screening = self.get_object()
        
        all_seats = Seat.objects.filter(hall=screening.hall, is_active=True)
        booked_seats = Booking.objects.filter(
            screening=screening,
            status__in=['confirmed', 'pending']
        ).values_list('seat_id', flat=True)
        
        result = []
        for seat in all_seats:
            result.append({
                'id': seat.id,
                'row': seat.row,
                'number': seat.number,
                'seat_type': seat.seat_type,
                'status': 'booked' if seat.id in booked_seats else 'available',
                'price': screening.price_vip if seat.seat_type == 'vip' else screening.price_standard
            })
        
        return Response({
            'screening_id': screening.id,
            'seats': result
        })
    
    @action(detail=True, methods=['post'])
    def check_seats(self, request, pk=None):
        """Проверить доступность мест"""
        screening = self.get_object()
        seat_ids = request.data.get('seat_ids', [])
        
        booked_seats = Booking.objects.filter(
            screening=screening,
            seat_id__in=seat_ids,
            status__in=['confirmed', 'pending']
        ).values_list('seat_id', flat=True)
        
        if booked_seats:
            return Response({
                'available': False,
                'booked_seats': list(booked_seats)
            })
        
        return Response({'available': True})