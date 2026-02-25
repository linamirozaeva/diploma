from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Телефон')
    is_verified = models.BooleanField(default=False, verbose_name='Подтвержден')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    USER_TYPE_CHOICES = (
        ('guest', 'Гость'),
        ('admin', 'Администратор'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='guest', verbose_name='Тип пользователя')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
        indexes = [
            # Индекс для поиска по email
            models.Index(fields=['email'], name='user_email_idx'),
            
            # Индекс для поиска по типу пользователя
            models.Index(fields=['user_type'], name='user_type_idx'),
            
            # Индекс для фильтрации верифицированных
            models.Index(fields=['is_verified'], name='user_verified_idx'),
            
            # Составной индекс для статуса и типа
            models.Index(fields=['is_active', 'user_type'], name='user_active_type_idx'),
        ]
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin_user(self):
        return self.is_staff or self.user_type == 'admin'