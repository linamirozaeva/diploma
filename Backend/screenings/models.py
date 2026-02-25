from django.db import models
from movies.models import Movie
from cinemas.models import CinemaHall

class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='screenings')
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='screenings')
    start_time = models.DateTimeField(verbose_name='Время начала')
    end_time = models.DateTimeField(verbose_name='Время окончания')
    price_standard = models.PositiveIntegerField(verbose_name='Цена за обычное место', default=250)
    price_vip = models.PositiveIntegerField(verbose_name='Цена за VIP место', default=350)
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'
        ordering = ['start_time']
        indexes = [
            # Индекс для поиска по времени начала (часто используется)
            models.Index(fields=['start_time'], name='screening_start_time_idx'),
            
            # Составной индекс для фильтрации фильмов по дате
            models.Index(fields=['movie', 'start_time'], name='screening_movie_start_idx'),
            
            # Составной индекс для проверки пересечений в зале
            models.Index(fields=['hall', 'start_time', 'end_time'], name='screening_hall_time_idx'),
            
            # Индекс для фильтрации активных сеансов
            models.Index(fields=['is_active'], name='screening_active_idx'),
            
            # Индекс для поиска по дате окончания
            models.Index(fields=['end_time'], name='screening_end_time_idx'),
        ]
    
    def __str__(self):
        movie_title = self.movie.title if self.movie else 'Без фильма'
        return f"{movie_title} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"