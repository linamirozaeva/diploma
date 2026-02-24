from rest_framework import serializers
from django.utils import timezone
from .models import Screening
from .validators import ScreeningValidator

class ScreeningListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка сеансов
    """
    movie_title = serializers.CharField(source='movie.title', read_only=True, default='')
    hall_name = serializers.CharField(source='hall.name', read_only=True, default='')
    
    class Meta:
        model = Screening
        fields = ['id', 'movie', 'movie_title', 'hall', 'hall_name', 
                  'start_time', 'end_time', 'price_standard', 'price_vip', 'is_active']

class ScreeningDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о сеансе
    """
    movie_details = serializers.SerializerMethodField()
    hall_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Screening
        fields = ['id', 'movie', 'movie_details', 'hall', 'hall_details', 
                  'start_time', 'end_time', 'price_standard', 'price_vip', 
                  'is_active', 'created_at', 'updated_at']
    
    def get_movie_details(self, obj):
        if obj.movie:
            return {
                'id': obj.movie.id,
                'title': obj.movie.title,
                'duration': obj.movie.duration,
                'poster': obj.movie.poster.url if obj.movie.poster else None
            }
        return None
    
    def get_hall_details(self, obj):
        if obj.hall:
            return {
                'id': obj.hall.id,
                'name': obj.hall.name,
                'total_seats': obj.hall.total_seats
            }
        return None

class ScreeningCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор ТОЛЬКО для создания сеансов
    """
    class Meta:
        model = Screening
        fields = ['id', 'movie', 'hall', 'start_time', 'end_time', 'price_standard', 'price_vip', 'is_active']
        read_only_fields = ['id']  # ID только для чтения, но будет возвращаться
    
    def validate(self, data):
        # Проверка времени и пересечений
        time_errors = ScreeningValidator.validate_screening_times(
            start_time=data['start_time'],
            end_time=data['end_time'],
            hall=data['hall'],
            instance=self.instance
        )
        
        if time_errors:
            raise serializers.ValidationError(time_errors)
        
        # Проверка соответствия длительности фильма
        if data.get('movie'):
            movie_errors = ScreeningValidator.validate_screening_with_movie(
                movie=data['movie'],
                start_time=data['start_time'],
                end_time=data['end_time']
            )
            
            if movie_errors:
                raise serializers.ValidationError(movie_errors)
        
        # Проверка цен
        if data['price_standard'] < 0:
            raise serializers.ValidationError({
                "price_standard": "Цена не может быть отрицательной"
            })
        
        if data['price_vip'] < 0:
            raise serializers.ValidationError({
                "price_vip": "Цена не может быть отрицательной"
            })
        
        return data

class ScreeningUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор ТОЛЬКО для обновления сеансов
    """
    class Meta:
        model = Screening
        fields = ['id', 'movie', 'hall', 'start_time', 'end_time', 'price_standard', 'price_vip', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        # Та же валидация, что и выше
        time_errors = ScreeningValidator.validate_screening_times(
            start_time=data['start_time'],
            end_time=data['end_time'],
            hall=data['hall'],
            instance=self.instance
        )
        
        if time_errors:
            raise serializers.ValidationError(time_errors)
        
        return data

class ScreeningCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления сеансов
    """
    class Meta:
        model = Screening
        fields = ['id', 'movie', 'hall', 'start_time', 'end_time', 'price_standard', 'price_vip', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        # Проверка времени и пересечений
        time_errors = ScreeningValidator.validate_screening_times(
            start_time=data['start_time'],
            end_time=data['end_time'],
            hall=data['hall'],
            instance=self.instance
        )
        
        if time_errors:
            raise serializers.ValidationError(time_errors)
        
        # Проверка соответствия длительности фильма
        if data.get('movie'):
            movie_errors = ScreeningValidator.validate_screening_with_movie(
                movie=data['movie'],
                start_time=data['start_time'],
                end_time=data['end_time']
            )
            
            if movie_errors:
                raise serializers.ValidationError(movie_errors)
        
        # Проверка цен
        if data['price_standard'] < 0:
            raise serializers.ValidationError({
                "price_standard": "Цена не может быть отрицательной"
            })
        
        if data['price_vip'] < 0:
            raise serializers.ValidationError({
                "price_vip": "Цена не может быть отрицательной"
            })
        
        return data
    """
    Сериализатор для создания и обновления сеансов с валидацией
    """
    
    class Meta:
        model = Screening
        fields = ('movie', 'hall', 'start_time', 'end_time', 'price_standard', 'price_vip', 'is_active')
    
    def validate(self, data):
        """
        Комплексная валидация сеанса
        """
        errors = {}
        
        # 1. Проверка времени и пересечений
        time_errors = ScreeningValidator.validate_screening_times(
            start_time=data['start_time'],
            end_time=data['end_time'],
            hall=data['hall'],
            instance=self.instance
        )
        
        if time_errors:
            raise serializers.ValidationError(time_errors)
        
        # 2. Проверка соответствия длительности фильма
        if data.get('movie'):
            movie_errors = ScreeningValidator.validate_screening_with_movie(
                movie=data['movie'],
                start_time=data['start_time'],
                end_time=data['end_time']
            )
            
            if movie_errors:
                raise serializers.ValidationError(movie_errors)
        
        # 3. Проверка цен
        price_errors = ScreeningValidator.validate_price_range(
            price_standard=data['price_standard'],
            price_vip=data['price_vip']
        )
        
        if price_errors:
            raise serializers.ValidationError(price_errors)
        
        return data

class ScreeningDateFilterSerializer(serializers.Serializer):
    """
    Сериализатор для фильтрации сеансов по дате
    """
    date = serializers.DateField(required=False)
    movie_id = serializers.IntegerField(required=False)
    hall_id = serializers.IntegerField(required=False)