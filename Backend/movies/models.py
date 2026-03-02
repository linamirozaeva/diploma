from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название фильма')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    duration = models.PositiveIntegerField(verbose_name='Длительность (минут)')
    release_date = models.DateField(verbose_name='Дата выхода', null=True, blank=True)
    poster = models.ImageField(upload_to='posters/', verbose_name='Постер', blank=True, null=True)
    country = models.CharField(max_length=100, verbose_name='Страна производства', blank=True)
    director = models.CharField(max_length=200, verbose_name='Режиссер', blank=True)
    cast = models.TextField(verbose_name='В главных ролях', blank=True)
    age_rating = models.CharField(max_length=10, verbose_name='Возрастной рейтинг', default='12+')
    trailer_url = models.URLField(verbose_name='Ссылка на трейлер', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']
        indexes = [
            # Индекс для поиска по названию (часто используется)
            models.Index(fields=['title'], name='movie_title_idx'),
            
            # Индекс для сортировки по дате выхода
            models.Index(fields=['release_date'], name='movie_release_date_idx'),
            
            # Индекс для фильтрации активных фильмов
            models.Index(fields=['is_active'], name='movie_active_idx'),
            
            # Составной индекс для now_showing/coming_soon
            models.Index(fields=['release_date', 'is_active'], name='movie_release_active_idx'),
            
            # Индекс для поиска по режиссеру
            models.Index(fields=['director'], name='movie_director_idx'),
        ]
    
    def __str__(self):
        return self.title