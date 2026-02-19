from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from config.permissions import IsAdminOrReadOnly, IsAdminUser
from datetime import datetime, timedelta
from screenings.models import Screening
from rest_framework import viewsets, permissions, status, filters
from .serializers import (
    ScreeningListSerializer, ScreeningDetailSerializer,
    ScreeningCreateUpdateSerializer, ScreeningDateFilterSerializer
)
from cinemas.models import Seat
from bookings.models import Booking
from movies.models import Movie  
from cinemas.models import CinemaHall  
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
    
    list: Все пользователи
    retrieve: Все пользователи
    create: Только админы
    update: Только админы
    partial_update: Только админы
    destroy: Только админы
    """
    queryset = Screening.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['movie__title', 'hall__name']
    ordering_fields = ['start_time', 'end_time', 'price_standard']
    
    def get_queryset(self):
        """Фильтрация сеансов"""
        queryset = super().get_queryset()
        
        # Все видят только активные сеансы
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
            queryset = queryset.filter(is_active=True)
        
        # Фильтр по дате (будущие сеансы)
        time_filter = self.request.query_params.get('time')
        if time_filter == 'upcoming':
            queryset = queryset.filter(start_time__gte=timezone.now())
        
        return queryset
    
    def get_serializer_class(self):
        """Выбор сериализатора"""
        if self.action in ['create', 'update', 'partial_update']:
            return ScreeningCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ScreeningDetailSerializer
        return ScreeningListSerializer
    
    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """
        Информация о доступных местах - доступно всем
        """
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
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny]) 
    def check_seats(self, request, pk=None):
        """
        Проверить доступность мест - доступно всем
        """
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

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """
        Сеансы по датам - доступно всем
        """
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days)
        
        screenings = self.get_queryset().filter(
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        ).order_by('start_time')
        
        from collections import OrderedDict
        result = OrderedDict()
        
        for screening in screenings:
            date_str = screening.start_time.strftime('%Y-%m-%d')
            if date_str not in result:
                result[date_str] = {
                    'date': date_str,
                    'screenings': []
                }
            
            serializer = ScreeningListSerializer(screening)
            result[date_str]['screenings'].append(serializer.data)
        
        return Response(list(result.values()))    
        """
        ViewSet для управления сеансами
    
        list: Получить список всех сеансов
        retrieve: Получить детальную информацию о сеансе
        create: Создать новый сеанс (только админ)
        update: Обновить сеанс (только админ)
        partial_update: Частично обновить сеанс (только админ)
        destroy: Удалить сеанс (только админ)
        """

    queryset = Screening.objects.filter(is_active=True).order_by('start_time')
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action in ['create', 'update', 'partial_update']:
            return ScreeningCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ScreeningDetailSerializer
        return ScreeningListSerializer

    def get_queryset(self):
        """Фильтрация сеансов по параметрам запроса"""
        queryset = super().get_queryset()
        
        # Фильтр по дате
        date = self.request.query_params.get('date')
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date=date_obj)
            except ValueError:
                pass
        
        # Фильтр по фильму
        movie_id = self.request.query_params.get('movie')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        
        # Фильтр по залу
        hall_id = self.request.query_params.get('hall')
        if hall_id:
            queryset = queryset.filter(hall_id=hall_id)
        
        # Фильтр по времени (будущие/прошедшие)
        time_filter = self.request.query_params.get('time')
        now = timezone.now()
        
        if time_filter == 'upcoming':
            queryset = queryset.filter(start_time__gte=now)
        elif time_filter == 'past':
            queryset = queryset.filter(start_time__lt=now)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """
        Получить информацию о доступных местах на сеанс
        GET /api/screenings/{id}/available_seats/
        """
        screening = self.get_object()
        
        # Все места в зале
        all_seats = Seat.objects.filter(hall=screening.hall, is_active=True)
        
        # Занятые места (подтвержденные бронирования)
        booked_seats = Booking.objects.filter(
            screening=screening,
            status__in=['confirmed', 'pending']
        ).values_list('seat_id', flat=True)
        
        # Выбранные места (временная блокировка - можно добавить позже)
        # selected_seats = []
        
        result = []
        for seat in all_seats:
            seat_info = {
                'id': seat.id,
                'row': seat.row,
                'number': seat.number,
                'seat_type': seat.seat_type,
                'status': 'booked' if seat.id in booked_seats else 'available',
                'price': screening.price_vip if seat.seat_type == 'vip' else screening.price_standard
            }
            result.append(seat_info)
        
        # Группировка по рядам для удобства
        seats_by_row = {}
        for seat in result:
            row = seat['row']
            if row not in seats_by_row:
                seats_by_row[row] = []
            seats_by_row[row].append(seat)
        
        # Сортировка рядов и мест
        for row in seats_by_row:
            seats_by_row[row].sort(key=lambda x: x['number'])
        
        return Response({
            'screening_id': screening.id,
            'hall_name': screening.hall.name,
            'total_seats': len(result),
            'available_seats': sum(1 for s in result if s['status'] == 'available'),
            'booked_seats': sum(1 for s in result if s['status'] == 'booked'),
            'seats_by_row': dict(sorted(seats_by_row.items()))
        })
    
    @action(detail=True, methods=['post'])
    def check_seats(self, request, pk=None):
        """
        Проверить доступность конкретных мест
        POST /api/screenings/{id}/check_seats/
        {
            "seat_ids": [1, 2, 3, 4]
        }
        """
        screening = self.get_object()
        seat_ids = request.data.get('seat_ids', [])
        
        if not seat_ids:
            return Response(
                {'error': 'Необходимо указать seat_ids'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, что места существуют в этом зале
        seats = Seat.objects.filter(id__in=seat_ids, hall=screening.hall)
        if seats.count() != len(seat_ids):
            found_ids = [s.id for s in seats]
            missing_ids = set(seat_ids) - set(found_ids)
            return Response(
                {'error': f'Места {missing_ids} не найдены в этом зале'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, свободны ли места
        booked_seats = Booking.objects.filter(
            screening=screening,
            seat_id__in=seat_ids,
            status__in=['confirmed', 'pending']
        ).values_list('seat_id', flat=True)
        
        if booked_seats:
            return Response({
                'available': False,
                'booked_seats': list(booked_seats),
                'message': f'Места {list(booked_seats)} уже заняты'
            })
        
        # Рассчитываем стоимость
        total_price = 0
        seats_info = []
        for seat in seats:
            price = screening.price_vip if seat.seat_type == 'vip' else screening.price_standard
            total_price += price
            seats_info.append({
                'id': seat.id,
                'row': seat.row,
                'number': seat.number,
                'type': seat.seat_type,
                'price': price
            })
        
        return Response({
            'available': True,
            'seats': seats_info,
            'total_price': total_price,
            'message': 'Все места свободны'
        })
    
    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """
        Получить сеансы с группировкой по датам
        GET /api/screenings/by_date/
        """
        days = int(request.query_params.get('days', 7))
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days)
        
        screenings = self.get_queryset().filter(
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        ).order_by('start_time')
        
        # Группировка по датам
        result = {}
        for screening in screenings:
            date_str = screening.start_time.strftime('%Y-%m-%d')
            if date_str not in result:
                result[date_str] = {
                    'date': date_str,
                    'weekday': screening.start_time.strftime('%A'),
                    'screenings': []
                }
            
            serializer = ScreeningListSerializer(screening)
            result[date_str]['screenings'].append(serializer.data)
        
        return Response(list(result.values()))
    
    @action(detail=False, methods=['get'])
    def now_playing(self, request):
        """
        Сеансы, идущие прямо сейчас
        """
        now = timezone.now()
        screenings = self.queryset.filter(
            start_time__lte=now,
            end_time__gte=now
        ).order_by('start_time')
        
        serializer = self.get_serializer(screenings, many=True)
        return Response(serializer.data)