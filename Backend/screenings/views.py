from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from config.permissions import IsAdminOrReadOnly, IsAdminUser
from .models import Screening
from .serializers import (
    ScreeningListSerializer, ScreeningDetailSerializer,
    ScreeningCreateUpdateSerializer
)
from cinemas.models import Seat
# Не импортируем Booking здесь, будем импортировать внутри функций


class ScreeningViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления сеансами
    
    list: Все пользователи (включая гостей)
    retrieve: Все пользователи
    available_seats: Все пользователи
    create: Только админы
    update: Только админы
    partial_update: Только админы
    destroy: Только админы
    stats: Только админы
    """
    queryset = Screening.objects.all()
    permission_classes = [IsAdminOrReadOnly]  # Админы могут всё, остальные только чтение
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['movie__title', 'hall__name']
    ordering_fields = ['start_time', 'price_standard', 'created_at']

    def get_queryset(self):
        """Фильтрация сеансов по параметрам запроса"""
        queryset = super().get_queryset()
        
        # Все видят только активные сеансы (кроме админов в админке)
        if not self.request.query_params.get('include_inactive'):
            queryset = queryset.filter(is_active=True)
        
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
        
        # Только будущие сеансы
        future_only = self.request.query_params.get('future_only')
        if future_only and future_only.lower() == 'true':
            queryset = queryset.filter(start_time__gte=timezone.now())
        
        return queryset.select_related('movie', 'hall').order_by('start_time')

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action in ['create', 'update', 'partial_update']:
            return ScreeningCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ScreeningDetailSerializer
        return ScreeningListSerializer

    def create(self, request, *args, **kwargs):
        """Создание сеанса (только для админов)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Проверка пересечений сеансов выполняется в сериализаторе
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """
        Информация о доступных местах на сеанс
        GET /api/screenings/{id}/available_seats/
        Доступно всем пользователям
        """
        screening = self.get_object()
        
        # Получаем все места в зале
        all_seats = Seat.objects.filter(hall=screening.hall, is_active=True).order_by('row', 'number')
        
        # Получаем занятые места
        from bookings.models import Booking
        booked_seats = Booking.objects.filter(
            screening=screening,
            status='confirmed'
        ).values_list('seat_id', flat=True)
        
        result = []
        for seat in all_seats:
            result.append({
                'seat_id': seat.id,
                'row': seat.row,
                'number': seat.number,
                'seat_type': seat.seat_type,
                'is_available': seat.id not in booked_seats,
                'price': screening.price_vip if seat.seat_type == 'vip' else screening.price_standard
            })
        
        return Response(result)

    @action(detail=True, methods=['post'])
    def book_seats(self, request, pk=None):
        """
        Забронировать места на сеанс
        POST /api/screenings/{id}/book_seats/
        Только для авторизованных пользователей
        """
        from bookings.models import Booking  # ← ВАЖНО: импорт внутри функции!
        import uuid
        
        screening = self.get_object()
        
        # Проверка авторизации
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Необходимо авторизоваться'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Проверка, что сеанс еще не начался
        if screening.start_time < timezone.now():
            return Response(
                {'error': 'Нельзя забронировать билеты на прошедший сеанс'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seat_ids = request.data.get('seat_ids', [])
        if not seat_ids:
            return Response(
                {'error': 'Не выбраны места'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, что места существуют в этом зале
        seats = Seat.objects.filter(
            id__in=seat_ids,
            hall=screening.hall,
            is_active=True
        )
        
        if len(seats) != len(seat_ids):
            return Response(
                {'error': 'Некоторые места не найдены или недоступны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, что места свободны
        booked_seats = Booking.objects.filter(
            screening=screening,
            seat_id__in=seat_ids,
            status='confirmed'
        ).exists()
        
        if booked_seats:
            return Response(
                {'error': 'Некоторые места уже заняты'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем бронирования
        bookings = []
        for seat in seats:
            booking = Booking.objects.create(
                screening=screening,
                user=request.user,
                seat=seat,
                booking_code=str(uuid.uuid4())[:8].upper(),
                status='confirmed'
            )
            bookings.append(booking)
        
        from bookings.serializers import BookingListSerializer as BookingSerializer
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request, pk=None):
        """
        Статистика по сеансу
        GET /api/screenings/{id}/stats/
        Только для админов
        """
        from bookings.models import Booking
        
        screening = self.get_object()
        
        total_seats = screening.hall.total_seats
        booked_seats = Booking.objects.filter(
            screening=screening,
            status='confirmed'
        ).count()
        
        revenue = Booking.objects.filter(
            screening=screening,
            status='confirmed'
        ).aggregate(total=Sum('price'))['total'] or 0
        
        return Response({
            'screening_id': screening.id,
            'total_seats': total_seats,
            'booked_seats': booked_seats,
            'available_seats': total_seats - booked_seats,
            'revenue': revenue,
            'occupancy_percentage': round((booked_seats / total_seats * 100), 2) if total_seats > 0 else 0
        })