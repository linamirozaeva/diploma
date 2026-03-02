from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import CinemaHall, Seat
from .serializers import (
    CinemaHallSerializer,
    CinemaHallCreateSerializer,
    CinemaHallDetailSerializer,
    SeatSerializer
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
    
    list: Все пользователи (включая гостей) - получают список залов
    retrieve: Все пользователи - получают детальную информацию о зале
    create: Только админы - создают новый зал
    update: Только админы - обновляют информацию о зале
    partial_update: Только админы - частично обновляют зал
    destroy: Только админы - удаляют зал
    
    Дополнительные действия:
    seats: Получить все места зала (доступно всем)
    update_seat_type: Обновить тип места (только админы)
    configure: Перенастроить зал (только админы)
    """
    queryset = CinemaHall.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """
        Фильтрация залов
        - Все видят только активные залы
        - Админы могут видеть все залы с параметром include_inactive=true
        """
        queryset = CinemaHall.objects.all()
        
        # Фильтр по активности
        include_inactive = self.request.query_params.get('include_inactive', False)
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('name')
    
    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия
        """
        if self.action == 'create':
            return CinemaHallCreateSerializer
        elif self.action == 'retrieve':
            return CinemaHallDetailSerializer
        return CinemaHallSerializer  # Для list и других действий
    
    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        """
        Получить все места конкретного зала
        GET /api/cinemas/halls/{id}/seats/
        Доступно всем пользователям
        """
        hall = self.get_object()
        seats = Seat.objects.filter(hall=hall, is_active=True).order_by('row', 'number')
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_seat_type(self, request, pk=None):
        """
        Обновить тип места
        POST /api/cinemas/halls/{id}/update_seat_type/
        Только для администраторов
        
        Тело запроса:
        {
            "seat_id": 123,
            "seat_type": "vip"  // standard, vip, disabled
        }
        """
        hall = self.get_object()
        seat_id = request.data.get('seat_id')
        seat_type = request.data.get('seat_type')
        
        if not seat_id or not seat_type:
            return Response(
                {'error': 'Необходимо указать seat_id и seat_type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_types = ['standard', 'vip', 'disabled']
        if seat_type not in valid_types:
            return Response(
                {'error': f'Недопустимый тип места. Допустимые значения: {valid_types}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seat = get_object_or_404(Seat, id=seat_id, hall=hall)
        seat.seat_type = seat_type
        seat.save()
        
        serializer = SeatSerializer(seat)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def configure(self, request, pk=None):
        """
        Перенастроить зал (изменить количество рядов и мест)
        POST /api/cinemas/halls/{id}/configure/
        Только для администраторов
        
        Тело запроса:
        {
            "rows": 10,
            "seats_per_row": 12
        }
        """
        hall = self.get_object()
        rows = request.data.get('rows')
        seats_per_row = request.data.get('seats_per_row')
        
        if not rows or not seats_per_row:
            return Response(
                {'error': 'Необходимо указать rows и seats_per_row'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Обновляем зал
            hall.rows = rows
            hall.seats_per_row = seats_per_row
            hall.save()
            
            # Удаляем старые места
            Seat.objects.filter(hall=hall).delete()
            
            # Создаем новые места
            seats = []
            for row in range(1, rows + 1):
                for number in range(1, seats_per_row + 1):
                    seats.append(
                        Seat(
                            hall=hall,
                            row=row,
                            number=number,
                            seat_type='standard'
                        )
                    )
            Seat.objects.bulk_create(seats)
            
            return Response({
                'success': True,
                'message': 'Конфигурация зала обновлена',
                'hall': {
                    'id': hall.id,
                    'name': hall.name,
                    'rows': hall.rows,
                    'seats_per_row': hall.seats_per_row,
                    'total_seats': hall.total_seats
                }
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Включить/выключить зал
        POST /api/cinemas/halls/{id}/toggle_active/
        Только для администраторов
        """
        hall = self.get_object()
        hall.is_active = not hall.is_active
        hall.save()
        
        return Response({
            'success': True,
            'is_active': hall.is_active,
            'message': f'Зал {"активирован" if hall.is_active else "деактивирован"}'
        })
    
    def create(self, request, *args, **kwargs):
        """
        Создание нового зала с автоматическим созданием мест
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        hall = serializer.save()
        
        # Возвращаем полную информацию о созданном зале
        response_serializer = CinemaHallDetailSerializer(hall)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Обновление информации о зале
        """
        partial = kwargs.pop('partial', False)
        hall = self.get_object()
        serializer = self.get_serializer(hall, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_hall = serializer.save()
        
        # Возвращаем обновленную информацию
        response_serializer = CinemaHallDetailSerializer(updated_hall)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Удаление зала (мягкое удаление - деактивация)
        """
        hall = self.get_object()
        hall.is_active = False
        hall.save()
        
        return Response(
            {'message': 'Зал успешно деактивирован'},
            status=status.HTTP_200_OK
        )