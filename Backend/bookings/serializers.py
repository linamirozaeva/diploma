import uuid
from rest_framework import serializers
from django.utils import timezone
from .models import Booking
from .validators import BookingValidator, BookingCancellationValidator
from screenings.models import Screening
from cinemas.models import Seat


class BookingListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка бронирований (краткая информация)
    Доступен всем авторизованным пользователям (видят только свои)
    """
    movie_title = serializers.CharField(source='screening.movie.title', read_only=True, default='')
    hall_name = serializers.CharField(source='screening.hall.name', read_only=True, default='')
    seat_info = serializers.SerializerMethodField()
    screening_time = serializers.DateTimeField(source='screening.start_time', read_only=True)
    
    class Meta:
        model = Booking
        fields = (
            'id', 'booking_code', 'movie_title', 'hall_name', 
            'seat_info', 'screening_time', 'price', 'status', 'created_at'
        )
        read_only_fields = ('id', 'booking_code', 'created_at')
    
    def get_seat_info(self, obj):
        """Форматированная информация о месте"""
        if obj.seat:
            seat_type = "VIP" if obj.seat.seat_type == 'vip' else "обычное"
            return f"Ряд {obj.seat.row}, Место {obj.seat.number} ({seat_type})"
        return "Место не указано"


class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о бронировании
    Доступен владельцу или админу
    """
    movie_details = serializers.SerializerMethodField()
    hall_details = serializers.SerializerMethodField()
    seat_details = serializers.SerializerMethodField()
    screening_details = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    qr_code_base64 = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = (
            'id', 'booking_code', 'user_details', 'movie_details', 'hall_details',
            'seat_details', 'screening_details', 'price', 'status',
            'qr_code', 'qr_code_base64', 'can_cancel', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'booking_code', 'created_at', 'updated_at')
    
    def get_movie_details(self, obj):
        """Детальная информация о фильме"""
        if obj.screening and obj.screening.movie:
            movie = obj.screening.movie
            # Убираем age_rating, так как его нет в модели
            return {
                'id': movie.id,
                'title': movie.title,
                'duration': movie.duration,
                'poster': movie.poster.url if movie.poster and hasattr(movie.poster, 'url') else None,
            }
        return None
    
    def get_hall_details(self, obj):
        """Детальная информация о зале"""
        if obj.screening and obj.screening.hall:
            hall = obj.screening.hall
            return {
                'id': hall.id,
                'name': hall.name,
                'total_seats': hall.total_seats
            }
        return None
    
    def get_seat_details(self, obj):
        """Детальная информация о месте"""
        if obj.seat:
            return {
                'id': obj.seat.id,
                'row': obj.seat.row,
                'number': obj.seat.number,
                'type': obj.seat.seat_type,
                'type_display': 'VIP' if obj.seat.seat_type == 'vip' else 'Обычное'
            }
        return None
    
    def get_screening_details(self, obj):
        """Детальная информация о сеансе"""
        if obj.screening:
            return {
                'id': obj.screening.id,
                'start_time': obj.screening.start_time,
                'end_time': obj.screening.end_time,
                'price_standard': obj.screening.price_standard,
                'price_vip': obj.screening.price_vip
            }
        return None
    
    def get_user_details(self, obj):
        """Информация о пользователе (только для админов)"""
        request = self.context.get('request')
        if request and request.user.is_admin_user and obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name
            }
        return None
    
    def get_qr_code_base64(self, obj):
        """Возвращает QR-код в формате base64"""
        return obj.get_qr_base64()
    
    def get_can_cancel(self, obj):
        """Проверка возможности отмены бронирования"""
        return obj.can_cancel  


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания бронирования
    Доступен авторизованным пользователям
    """
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        min_length=1,
        max_length=10,
        help_text="Список ID мест для бронирования"
    )
    
    class Meta:
        model = Booking
        fields = ('id', 'screening', 'seat_ids')
        read_only_fields = ('id',)
    
    def validate(self, data):
        """
        Комплексная валидация перед созданием бронирования
        """
        screening = data.get('screening')
        seat_ids = data.get('seat_ids', [])
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        # 1. Проверка времени бронирования
        time_check = BookingValidator.validate_booking_time(screening)
        if not time_check['valid']:
            raise serializers.ValidationError({
                'booking_time': time_check['error']
            })
        
        # 2. Проверка лимита пользователя
        if user:
            limit_check = BookingValidator.validate_user_booking_limit(
                user, screening, requested_seats_count=len(seat_ids)
            )
            if not limit_check['valid']:
                raise serializers.ValidationError({
                    'user_limit': limit_check['error']
                })
        
        # 3. Проверка доступности мест
        availability = BookingValidator.validate_seats_availability(screening, seat_ids)
        if not availability['available']:
            raise serializers.ValidationError({
                'seats': availability['message'],
                'details': availability.get('details', {})
            })
        
        # 4. Проверка выбранных мест (логика)
        seats = Seat.objects.filter(id__in=availability['available_seats'])
        
        selection_check = BookingValidator.validate_seat_selection(seats)
        if not selection_check['valid']:
            raise serializers.ValidationError({
                'seat_selection': selection_check['error']
            })
        
        # Сохраняем проверенные данные
        data['validated_seats'] = seats
        data['user'] = user
        
        return data
    
    def create(self, validated_data):
        """
        Создание одного или нескольких бронирований
        Возвращает список созданных бронирований
        """
        screening = validated_data['screening']
        seats = validated_data['validated_seats']
        user = validated_data.get('user')
        
        bookings = []
        
        for seat in seats:
            # Определение цены
            price = screening.price_vip if seat.seat_type == 'vip' else screening.price_standard
            
            # Создаем бронирование
            booking = Booking(
                user=user,
                screening=screening,
                seat=seat,
                price=price,
                status='confirmed'
            )
            
            booking.save()  # Здесь сработает переопределенный save() с генерацией QR-кода
            bookings.append(booking)
        
        # Возвращаем список созданных бронирований
        return bookings


class BookingCancelSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отмены бронирования
    Доступен владельцу или админу
    """
    reason = serializers.CharField(required=False, allow_blank=True, help_text="Причина отмены")
    
    class Meta:
        model = Booking
        fields = ('id', 'status', 'reason')
        read_only_fields = ('id',)
    
    def validate(self, data):
        """
        Проверка возможности отмены
        """
        if not self.instance:
            raise serializers.ValidationError("Бронирование не найдено")
        
        # Проверка возможности отмены
        cancellation_check = BookingCancellationValidator.validate_cancellation(self.instance)
        if not cancellation_check['valid']:
            raise serializers.ValidationError({
                'cancellation': cancellation_check['error']
            })
        
        return data
    
    def update(self, instance, validated_data):
        """
        Отмена бронирования
        """
        instance.status = 'cancelled'
        instance.save()
        return instance