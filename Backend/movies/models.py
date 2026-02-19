from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True)
    duration = models.PositiveIntegerField(verbose_name='Длительность (минут)', default=120)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True, verbose_name='Постер')
    release_date = models.DateField(verbose_name='Дата выхода', null=True, blank=True)
    director = models.CharField(max_length=100, verbose_name='Режиссер', blank=True)
    cast = models.TextField(verbose_name='В ролях', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title