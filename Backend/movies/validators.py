from datetime import date
from django.utils import timezone

class MovieValidator:
    """
    Валидатор для фильмов
    """
    
    @staticmethod
    def validate_movie_duration(duration):
        """
        Проверка длительности фильма
        """
        errors = {}
        
        if duration < 1:
            errors['duration'] = "Длительность фильма должна быть больше 0 минут"
        elif duration < 30:
            errors['duration'] = "Минимальная длительность фильма - 30 минут"
        elif duration > 300:
            errors['duration'] = "Максимальная длительность фильма - 5 часов (300 минут)"
        
        return errors
    
    @staticmethod
    def validate_release_date(release_date):
        """
        Проверка даты выхода фильма
        """
        errors = {}
        
        if not release_date:
            return errors
        
        if release_date.year < 1900:
            errors['release_date'] = "Некорректная дата выхода (год меньше 1900)"
        
        # Можно разрешить даты в будущем для "скоро в прокате"
        
        return errors
    
    @staticmethod
    def validate_title(title):
        """
        Проверка названия фильма
        """
        errors = {}
        
        if not title:
            errors['title'] = "Название не может быть пустым"
        elif len(title) < 2:
            errors['title'] = "Название должно содержать хотя бы 2 символа"
        elif len(title) > 200:
            errors['title'] = "Название слишком длинное (максимум 200 символов)"
        
        return errors
    
    @staticmethod
    def validate_movie_deletion(movie):
        """
        Проверка возможности удаления фильма
        """
        from screenings.models import Screening
        
        # Есть ли будущие сеансы с этим фильмом
        future_screenings = Screening.objects.filter(
            movie=movie,
            start_time__gt=timezone.now(),
            is_active=True
        ).exists()
        
        if future_screenings:
            return {
                'valid': False,
                'error': "Нельзя удалить фильм, на который запланированы будущие сеансы"
            }
        
        return {'valid': True}
    
    @staticmethod
    def validate_movie_update(movie, data):
        """
        Проверка обновления фильма
        """
        errors = {}
        
        # Если меняется длительность, проверяем существующие сеансы
        if 'duration' in data and data['duration'] != movie.duration:
            from screenings.models import Screening
            
            # Проверка на будущие сеансы
            future_screenings = Screening.objects.filter(
                movie=movie,
                start_time__gt=timezone.now(),
                is_active=True
            )
            
            if future_screenings.exists():
                errors['duration'] = (
                    "Нельзя изменить длительность фильма, "
                    "на который запланированы будущие сеансы"
                )
        
        return errors