from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404
from bookings.models import Booking
from config.permissions import (
    IsAdminUser, IsOwnerOrAdminForBooking, 
    CanCreateBooking, CanCancelBooking, CanViewBookings
)
from .serializers import (
    BookingListSerializer, BookingDetailSerializer,
    BookingCreateSerializer, BookingCancelSerializer
)
from screenings.models import Screening  
from cinemas.models import Seat

class IsAdminOrOwner(permissions.BasePermission):
    """
    Разрешение: админы могут всё, владельцы только свои брони
    """
    def has_object_permission(self, request, view, obj):
        # Админы могут всё
        if request.user.is_admin_user:
            return True
        # Владельцы могут просматривать свои брони
        return obj.user == request.user

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления бронированиями
    
    list: Админы - все, пользователи - свои
    retrieve: Админы - все, пользователи - свои
    create: Авторизованные пользователи
    update: Не разрешено
    partial_update: Не разрешено
    destroy: Только админы
    """
    serializer_class = BookingListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['booking_code', 'screening__movie__title']
    ordering_fields = ['created_at', 'screening__start_time', 'price']
    
    def get_queryset(self):
        """Фильтрация бронирований в зависимости от роли"""
        user = self.request.user
        
        # Анонимные пользователи ничего не видят
        if not user or not user.is_authenticated:
            return Booking.objects.none()
        
        # Админы видят все
        if user.is_admin_user:
            queryset = Booking.objects.all()
        else:
            # Обычные пользователи видят только свои
            queryset = Booking.objects.filter(user=user)
        
        # Фильтрация по статусу
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related(
            'user', 'screening', 'seat', 
            'screening__movie', 'screening__hall'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """Выбор сериализатора"""
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        elif self.action == 'cancel':
            return BookingCancelSerializer
        return BookingListSerializer
    
    def get_permissions(self):
        """Динамическое определение прав доступа"""
        if self.action == 'create':
            # Создание бронирования - авторизованные пользователи
            permission_classes = [CanCreateBooking]
        elif self.action in ['list', 'retrieve']:
            # Просмотр - админы все, пользователи свои
            permission_classes = [CanViewBookings]
        elif self.action == 'cancel':
            # Отмена - владелец или админ (с проверкой времени)
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminForBooking]
        elif self.action == 'destroy':
            # Удаление - только админы
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminUser]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Создание бронирования
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.context['request'] = request
        
        booking = serializer.save()
        response_serializer = BookingDetailSerializer(booking)
        
        return Response({
            'status': 'success',
            'booking': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """
        Свои бронирования - доступно авторизованным
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Требуется авторизация'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        
        serializer = BookingDetailSerializer(bookings, many=True)
        return Response({
            'total': bookings.count(),
            'active': bookings.filter(status='confirmed').count(),
            'bookings': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Отмена бронирования - владелец или админ
        """
        booking = self.get_object()
        
        # Дополнительная проверка прав через permission classes уже есть
        serializer = BookingCancelSerializer(booking, data={}, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Бронирование отменено'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """
        Получить QR-код - владелец или админ
        """
        booking = self.get_object()
        
        # Проверка прав
        if not (request.user.is_admin_user or booking.user == request.user):
            return Response(
                {'error': 'Нет доступа'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not booking.qr_code:
            return Response(
                {'error': 'QR-код не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'qr_code_url': booking.qr_code.url
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def verify(self, request):
        """
        Проверить бронирование по коду - только для админов (контроллеры)
        POST /api/bookings/verify/
        {
            "booking_code": "BK12345678"
        }
        """
        booking_code = request.data.get('booking_code')
    
        try:
            booking = Booking.objects.get(booking_code=booking_code)
        except Booking.DoesNotExist:
            return Response(
                {'valid': False, 'error': 'Бронирование не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
    
        # Проверка статуса
        if booking.status == 'used':
            return Response({
                'valid': False,
                'message': 'Билет уже использован'
            })
    
        if booking.status == 'cancelled':
            return Response({
                'valid': False,
                'message': 'Бронирование отменено'
            })
    
        # Если билет действителен
        if request.data.get('mark_as_used'):
            booking.status = 'used'
            booking.save()
            return Response({
                'valid': True,
                'message': 'Билет действителен и отмечен как использованный'
            })
    
        return Response({
            'valid': True,
            'message': 'Билет действителен'
        })  # <- Здесь должна быть только эта строка
    
        """
    ViewSet для управления бронированиями
    
    list: Получить список бронирований (админ - все, пользователь - свои)
    retrieve: Получить детальную информацию о бронировании
    create: Создать новое бронирование (авторизованный пользователь)
    update: Обновить бронирование (не рекомендуется)
    partial_update: Частично обновить бронирование
    destroy: Удалить бронирование
    """
    serializer_class = BookingListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['booking_code', 'screening__movie__title']
    ordering_fields = ['created_at', 'screening__start_time', 'price']
    
    def get_queryset(self):
        """Фильтрация бронирований в зависимости от роли"""
        user = self.request.user
        
        if user.is_admin_user:
            # Админ видит все бронирования
            queryset = Booking.objects.all()
        else:
            # Обычный пользователь видит только свои
            queryset = Booking.objects.filter(user=user)
        
        # Фильтрация по статусу
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Фильтрация по дате создания
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Фильтрация по дате сеанса
        screening_date = self.request.query_params.get('screening_date')
        if screening_date:
            queryset = queryset.filter(screening__start_time__date=screening_date)
        
        # Фильтрация по фильму
        movie_id = self.request.query_params.get('movie')
        if movie_id:
            queryset = queryset.filter(screening__movie_id=movie_id)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        elif self.action == 'cancel':
            return BookingCancelSerializer
        return BookingListSerializer
    
    def get_permissions(self):
        """Права доступа для разных действий"""
        if self.action == 'create':
            # Создавать могут авторизованные пользователи
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            # Просматривать с дополнительной фильтрацией
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Остальное только для админов или владельцев
            permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Создание бронирования с полной валидацией
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.context['request'] = request
        
        try:
            booking = serializer.save()
            response_serializer = BookingDetailSerializer(booking)
            return Response({
                'status': 'success',
                'message': 'Бронирование успешно создано',
                'booking': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """
        Получить все бронирования текущего пользователя
        GET /api/bookings/my_bookings/
        """
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        
        # Фильтрация по статусу
        status = request.query_params.get('status')
        if status:
            bookings = bookings.filter(status=status)
        
        # Фильтрация по дате сеанса
        date = request.query_params.get('date')
        if date:
            bookings = bookings.filter(screening__start_time__date=date)
        
        # Пагинация
        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = BookingDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BookingDetailSerializer(bookings, many=True)
        
        # Добавляем статистику
        return Response({
            'total': bookings.count(),
            'active': bookings.filter(status='confirmed').count(),
            'cancelled': bookings.filter(status='cancelled').count(),
            'used': bookings.filter(status='used').count(),
            'bookings': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Отменить бронирование
        POST /api/bookings/{id}/cancel/
        """
        booking = self.get_object()
        
        serializer = BookingCancelSerializer(booking, data={}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Бронирование успешно отменено',
                'booking': BookingDetailSerializer(booking).data
            })
        
        return Response({
            'status': 'error',
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """
        Получить QR-код для бронирования
        GET /api/bookings/{id}/qr_code/?format=base64
        """
        booking = self.get_object()
        
        if not booking.qr_code:
            return Response(
                {'error': 'QR-код не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Возвращаем URL или base64
        if request.query_params.get('format') == 'base64':
            import base64
            try:
                with open(booking.qr_code.path, 'rb') as f:
                    qr_base64 = base64.b64encode(f.read()).decode()
                return Response({
                    'qr_code_base64': qr_base64,
                    'booking_id': booking.id,
                    'booking_code': booking.booking_code
                })
            except Exception as e:
                return Response({
                    'error': f'Не удалось прочитать QR-код: {str(e)}'
                }, status=500)
        
        return Response({
            'qr_code_url': booking.qr_code.url if booking.qr_code else None,
            'booking_id': booking.id,
            'booking_code': booking.booking_code
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Статистика по бронированиям (только для админов)
        GET /api/bookings/stats/
        """
        if not request.user.is_admin_user:
            return Response(
                {'error': 'Только для администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Общая статистика
        total_bookings = Booking.objects.count()
        total_revenue = Booking.objects.filter(status='confirmed').aggregate(
            total=Sum('price')
        )['total'] or 0
        
        # Статистика по статусам
        status_stats = Booking.objects.values('status').annotate(
            count=Count('id'),
            revenue=Sum('price')
        )
        
        # Статистика по дням (последние 7 дней)
        from datetime import timedelta
        last_week = timezone.now().date() - timedelta(days=7)
        daily_stats = Booking.objects.filter(
            created_at__date__gte=last_week
        ).values('created_at__date').annotate(
            count=Count('id'),
            revenue=Sum('price')
        ).order_by('created_at__date')
        
        # Статистика по фильмам
        movie_stats = Booking.objects.filter(
            status='confirmed'
        ).values('screening__movie__title').annotate(
            count=Count('id'),
            revenue=Sum('price')
        ).order_by('-revenue')[:10]
        
        return Response({
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'average_price': total_revenue / total_bookings if total_bookings else 0,
            'by_status': list(status_stats),
            'daily_stats': list(daily_stats),
            'top_movies': list(movie_stats)
        })
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def verify(self, request):
        """
        Проверить бронирование по коду (для контроллера)
        POST /api/bookings/verify/
        {
            "booking_code": "BK12345678"
        }
        """
        booking_code = request.data.get('booking_code')
        
        if not booking_code:
            return Response(
                {'error': 'Необходимо указать booking_code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            booking = Booking.objects.get(booking_code=booking_code)
        except Booking.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Бронирование не найдено'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Проверка статуса
        if booking.status == 'used':
            return Response({
                'valid': False,
                'status': 'used',
                'message': 'Билет уже использован',
                'booking': BookingDetailSerializer(booking).data
            })
        
        if booking.status == 'cancelled':
            return Response({
                'valid': False,
                'status': 'cancelled',
                'message': 'Бронирование отменено',
                'booking': BookingDetailSerializer(booking).data
            })
        
        # Проверка времени сеанса
        now = timezone.now()
        screening = booking.screening
        
        if now > screening.end_time:
            return Response({
                'valid': False,
                'status': 'expired',
                'message': 'Сеанс уже закончился',
                'booking': BookingDetailSerializer(booking).data
            })
        
        # Если билет действителен и еще не использован
        if booking.status == 'confirmed' and now < screening.end_time:
            # Отмечаем как использованный (опционально)
            if request.data.get('mark_as_used', False):
                booking.status = 'used'
                booking.save()
                message = 'Билет действителен и отмечен как использованный'
            else:
                message = 'Билет действителен'
            
            return Response({
                'valid': True,
                'status': booking.status,
                'message': message,
                'booking': BookingDetailSerializer(booking).data
            })
        
        return Response({
            'valid': False,
            'status': booking.status,
            'message': 'Неизвестный статус бронирования',
            'booking': BookingDetailSerializer(booking).data
        })