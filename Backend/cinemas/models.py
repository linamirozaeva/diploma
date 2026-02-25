from django.db import models

class CinemaHall(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название зала')
    rows = models.PositiveIntegerField(verbose_name='Количество рядов')
    seats_per_row = models.PositiveIntegerField(verbose_name='Мест в ряду')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Кинозал'
        verbose_name_plural = 'Кинозалы'
        ordering = ['name']
        indexes = [
            # Индекс для поиска по названию
            models.Index(fields=['name'], name='hall_name_idx'),
            
            # Индекс для фильтрации активных залов
            models.Index(fields=['is_active'], name='hall_active_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.rows}x{self.seats_per_row})"
    
    @property
    def total_seats(self):
        return self.rows * self.seats_per_row

class Seat(models.Model):
    SEAT_TYPE_CHOICES = (
        ('standard', 'Обычное'),
        ('vip', 'VIP'),
    )
    
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='seats', verbose_name='Зал')
    row = models.PositiveIntegerField(verbose_name='Ряд')
    number = models.PositiveIntegerField(verbose_name='Место')
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPE_CHOICES, default='standard', verbose_name='Тип места')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    
    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'
        unique_together = ('hall', 'row', 'number')
        ordering = ['row', 'number']
        indexes = [
            # Индекс для поиска по залу
            models.Index(fields=['hall'], name='seat_hall_idx'),
            
            # Индекс для поиска по типу места
            models.Index(fields=['seat_type'], name='seat_type_idx'),
            
            # Составной индекс для сортировки по ряду и месту
            models.Index(fields=['row', 'number'], name='seat_row_number_idx'),
        ]
    
    def __str__(self):
        return f"Ряд {self.row}, Место {self.number}"