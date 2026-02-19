from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USER_TYPE_CHOICES = (
        ('guest', 'Гость'),
        ('admin', 'Администратор'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='guest')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin_user(self):
        return self.is_staff or self.user_type == 'admin'