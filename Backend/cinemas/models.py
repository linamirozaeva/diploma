from django.db import models

class CinemaHall(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_per_row = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Кинозал'
        verbose_name_plural = 'Кинозалы'
    
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
    
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='seats')
    row = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPE_CHOICES, default='standard')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'
        unique_together = ('hall', 'row', 'number')
    
    def __str__(self):
        return f"Ряд {self.row}, Место {self.number}"