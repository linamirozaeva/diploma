from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Screening
from movies.serializers import MovieListSerializer
from cinemas.serializers import CinemaHallSerializer

class ScreeningListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка сеансов
    """
    movie_details = MovieListSerializer(source='movie', read_only=True)
    hall_details = CinemaHallSerializer(source='hall', read_only=True)
    
    class Meta:
        model = Screening
        fields = [
            'id', 'movie', 'movie_details', 'hall', 'hall_details',
            'start_time', 'end_time', 'price_standard', 'price_vip',
            'is_active', 'created_at'
        ]

class ScreeningDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о сеансе
    """
    movie_details = MovieListSerializer(source='movie', read_only=True)
    hall_details = CinemaHallSerializer(source='hall', read_only=True)
    available_seats = serializers.IntegerField(source='available_seats_count', read_only=True)
    is_future = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Screening
        fields = [
            'id', 'movie', 'movie_details', 'hall', 'hall_details',
            'start_time', 'end_time', 'price_standard', 'price_vip',
            'is_active', 'available_seats', 'is_future', 'is_ongoing', 'is_past',
            'created_at', 'updated_at'
        ]

class ScreeningCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления сеансов
    """
    class Meta:
        model = Screening
        fields = ['movie', 'hall', 'start_time', 'price_standard', 'price_vip']
    
    def validate_start_time(self, value):
        """Проверка времени начала"""
        if value < timezone.now():
            raise serializers.ValidationError("Время начала сеанса не может быть в прошлом")
        return value
    
    def validate(self, data):
        """
        Валидация сеанса
        """
        start_time = data.get('start_time')
        hall = data.get('hall')
        movie = data.get('movie')
        
        if not start_time or not hall or not movie:
            return data
        
        # Рассчитываем время окончания для проверки пересечений
        end_time = start_time + timedelta(minutes=movie.duration)
        
        # Проверяем пересечение с другими сеансами
        conflicting = Screening.objects.filter(
            hall=hall,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        if self.instance:
            conflicting = conflicting.exclude(pk=self.instance.pk)
        
        if conflicting.exists():
            raise serializers.ValidationError(
                "Это время уже занято другим сеансом в выбранном зале"
            )
        
        return data
    
    def create(self, validated_data):
        """Создание сеанса с автоматическим расчетом end_time"""
        movie = validated_data['movie']
        start_time = validated_data['start_time']
        end_time = start_time + timedelta(minutes=movie.duration)
        
        screening = Screening.objects.create(
            **validated_data,
            end_time=end_time
        )
        return screening
    
    def update(self, instance, validated_data):
        """Обновление сеанса с пересчетом end_time"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Пересчитываем end_time если изменился фильм или время начала
        if 'movie' in validated_data or 'start_time' in validated_data:
            instance.end_time = instance.start_time + timedelta(
                minutes=instance.movie.duration
            )
        
        instance.save()
        return instance