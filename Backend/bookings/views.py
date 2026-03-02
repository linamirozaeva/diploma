from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import timedelta
import base64
import uuid

from bookings.models import Booking
from .serializers import (
    BookingListSerializer, BookingDetailSerializer,
    BookingCreateSerializer, BookingCancelSerializer
)


class IsAdminOrOwner(permissions.BasePermission):
    """
    Разрешение: админы могут всё, владельцы только свои брони
    """
    def has_object_permission(self, request, view, obj):
        # Админы могут всё
        if request.user and request.user.is_staff:
            return True
        # Владельцы могут просматривать и отменять свои брони
        return obj.user == request.user


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления бронированиями
    """
    queryset = Booking.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['booking_code', 'screening__movie__title', 'user__username']
    ordering_fields = ['created_at', 'screening__start_time', 'price']

    def get_queryset(self):
        """Фильтрация бронирований в зависимости от роли"""
        user = self.request.user
        
        # Анонимные пользователи ничего не видят
        if not user or not user.is_authenticated:
            return Booking.objects.none()
        
        # Админы видят все
        if user.is_staff or user.is_superuser:
            return Booking.objects.all()
        
        # Обычные пользователи видят только свои
        return Booking.objects.filter(user=user)

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
        """Динамическое определение прав доступа"""
        if self.action == 'create':
            # Создание бронирования - авторизованные пользователи
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            # Просмотр списка - авторизованные пользователи (фильтрация в get_queryset)
            permission_classes = [permissions.IsAdminUser]  # Только админы могут видеть весь список
        elif self.action == 'my_bookings':
            # Свои бронирования - авторизованные пользователи
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'retrieve':
            # Просмотр конкретного бронирования - авторизованные пользователи
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'cancel':
            # Отмена - владелец или админ
            permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
        elif self.action == 'destroy':
            # Удаление - только админы
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['stats', 'verify']:
            # Статистика и проверка - только админы
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAdminUser]
        
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Создание бронирования
        POST /api/bookings/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.context['request'] = request
        
        try:
            bookings = serializer.save()
            
            if isinstance(bookings, list):
                response_serializer = BookingDetailSerializer(bookings, many=True)
                return Response({
                    'status': 'success',
                    'message': f'Создано {len(bookings)} бронирований',
                    'bookings': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                response_serializer = BookingDetailSerializer(bookings)
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
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Требуется авторизация'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        
        # Фильтрация по статусу
        status_param = request.query_params.get('status')
        if status_param:
            bookings = bookings.filter(status=status_param)
        
        serializer = BookingDetailSerializer(bookings, many=True)
        
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
        
        # Проверка прав через permission classes
        self.check_object_permissions(request, booking)
        
        serializer = BookingCancelSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Бронирование успешно отменено',
                'booking': BookingDetailSerializer(booking).data
            })
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """
        Получить QR-код для бронирования
        GET /api/bookings/{id}/qr_code/
        """
        booking = self.get_object()
        
        # Проверка прав
        self.check_object_permissions(request, booking)
        
        if not booking.qr_code:
            return Response(
                {'error': 'QR-код не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.query_params.get('format') == 'base64':
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
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'qr_code_url': booking.qr_code.url if booking.qr_code else None,
            'booking_id': booking.id,
            'booking_code': booking.booking_code
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request):
        """
        Статистика по бронированиям (только для админов)
        GET /api/bookings/stats/
        """
        total_bookings = Booking.objects.count()
        total_revenue = Booking.objects.filter(status='confirmed').aggregate(
            total=Sum('price')
        )['total'] or 0
        
        status_stats = Booking.objects.values('status').annotate(
            count=Count('id'),
            revenue=Sum('price')
        )
        
        last_week = timezone.now().date() - timedelta(days=7)
        daily_stats = Booking.objects.filter(
            created_at__date__gte=last_week
        ).values('created_at__date').annotate(
            count=Count('id'),
            revenue=Sum('price')
        ).order_by('created_at__date')
        
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
        
        now = timezone.now()
        screening = booking.screening
        
        if now > screening.end_time:
            return Response({
                'valid': False,
                'status': 'expired',
                'message': 'Сеанс уже закончился',
                'booking': BookingDetailSerializer(booking).data
            })
        
        if booking.status == 'confirmed' and now < screening.end_time:
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