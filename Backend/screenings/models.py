from django.db import models
from movies.models import Movie
from cinemas.models import CinemaHall

class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='screenings', null=True, blank=True)
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='screenings', null=True, blank=True)
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
    
    def __str__(self):
        movie_title = self.movie.title if self.movie else 'Без фильма'
        return f"{movie_title} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"