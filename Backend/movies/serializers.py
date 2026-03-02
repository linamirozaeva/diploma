from rest_framework import serializers
from .models import Movie

class MovieListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка фильмов
    """
    poster_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'duration', 
            'poster_url', 'age_rating', 'is_active', 'release_date', 'country'
        ]
    
    def get_poster_url(self, obj):
        if obj.poster and hasattr(obj.poster, 'url'):
            return obj.poster.url
        return None

class MovieDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о фильме
    """
    poster_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'duration', 'release_date', 
            'poster_url', 'country', 'director', 'cast', 'age_rating', 
            'trailer_url', 'is_active', 'created_at', 'updated_at'
        ]
    
    def get_poster_url(self, obj):
        if obj.poster and hasattr(obj.poster, 'url'):
            return obj.poster.url
        return None

class MovieCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления фильмов
    """
    class Meta:
        model = Movie
        fields = [
            'title', 'description', 'duration', 'release_date', 
            'poster', 'country', 'director', 'cast', 'age_rating', 
            'trailer_url', 'is_active'
        ]
    
    def validate_duration(self, value):
        """Проверка длительности фильма"""
        if value < 1 or value > 300:
            raise serializers.ValidationError("Длительность должна быть от 1 до 300 минут")
        return value

# Алиас для обратной совместимости
MovieSerializer = MovieListSerializer