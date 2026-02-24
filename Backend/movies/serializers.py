from rest_framework import serializers
from .models import Movie
from .validators import MovieValidator

class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'duration', 'poster', 'release_date', 'director']

class MovieDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'duration', 'poster', 'release_date', 
                  'director', 'cast', 'is_active', 'created_at', 'updated_at']

class MovieCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'duration', 'poster', 'release_date', 
                  'director', 'cast', 'is_active']
        read_only_fields = ['id']
    
    def validate_title(self, value):
        """
        Валидация названия
        """
        title_errors = MovieValidator.validate_title(value)
        if title_errors:
            raise serializers.ValidationError(title_errors['title'])
        return value
    
    def validate_duration(self, value):
        """
        Валидация длительности
        """
        duration_errors = MovieValidator.validate_movie_duration(value)
        if duration_errors:
            raise serializers.ValidationError(duration_errors['duration'])
        return value
    
    def validate_release_date(self, value):
        """
        Валидация даты выхода
        """
        if value:
            date_errors = MovieValidator.validate_release_date(value)
            if date_errors:
                raise serializers.ValidationError(date_errors['release_date'])
        return value