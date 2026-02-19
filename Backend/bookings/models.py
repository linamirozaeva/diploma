import uuid
import qrcode
import io
from datetime import datetime
from django.db import models
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from screenings.models import Screening
from cinemas.models import Seat

class Booking(models.Model):
    """
    Модель бронирования билетов
    """
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('used', 'Использовано'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings', 
        null=True, 
        blank=True,
        verbose_name='Пользователь'
    )
    screening = models.ForeignKey(
        Screening, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='Сеанс'
    )
    seat = models.ForeignKey(
        Seat, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='Место'
    )
    booking_code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='Код бронирования'
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена',
        default=0
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='confirmed', 
        verbose_name='Статус'
    )
    qr_code = models.ImageField(
        upload_to='qrcodes/', 
        blank=True, 
        null=True, 
        verbose_name='QR-код'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']
        unique_together = ('screening', 'seat')  # Запрет двойного бронирования
    
    def __str__(self):
        return f"Бронь {self.booking_code} - {self.seat}"
    
    def save(self, *args, **kwargs):
        """
        Переопределенный save для генерации кода и QR перед сохранением
        """
        # Генерируем код бронирования, если его нет
        if not self.booking_code:
            self.booking_code = self.generate_booking_code()
        
        # Генерируем QR-код, если его нет
        if not self.qr_code:
            qr_image = self.generate_qr_code()
            if qr_image:
                filename = f"booking_{self.booking_code}.png"
                self.qr_code.save(filename, qr_image, save=False)
        
        super().save(*args, **kwargs)
    
    def generate_booking_code(self):
        """
        Генерация уникального кода бронирования
        Формат: BK + дата + уникальный хеш
        """
        import hashlib
        import time
        
        # Создаем уникальную строку
        timestamp = str(int(time.time()))
        unique_string = f"{self.screening.id}_{self.seat.id}_{timestamp}_{uuid.uuid4()}"
        
        # Создаем хеш
        hash_object = hashlib.sha256(unique_string.encode())
        hash_hex = hash_object.hexdigest()[:10].upper()
        
        # Формируем код: BK + дата (6 символов) + хеш (10 символов)
        date_str = datetime.now().strftime('%y%m%d')
        booking_code = f"BK{date_str}{hash_hex}"
        
        # Проверяем уникальность
        while Booking.objects.filter(booking_code=booking_code).exists():
            # Если код уже существует, добавляем случайное число
            import random
            booking_code = f"BK{date_str}{hash_hex}{random.randint(10, 99)}"
        
        return booking_code
    
    def generate_qr_code(self):
        """
        Генерация QR-кода для билета
        """
        try:
            # Формируем данные для QR-кода
            qr_data = self.get_qr_data()
            
            # Создаем QR-код
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Создаем изображение
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Конвертируем в bytes для сохранения
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            
            return ContentFile(buffer.getvalue(), name=f'{self.booking_code}.png')
        
        except Exception as e:
            print(f"Ошибка генерации QR-кода: {e}")
            return None
    
    def get_qr_data(self):
        """
        Формирование данных для QR-кода
        Возвращает строку с информацией о бронировании
        """
        movie_title = self.screening.movie.title if self.screening.movie else "Не указан"
        hall_name = self.screening.hall.name if self.screening.hall else "Не указан"
        
        # Формируем данные в формате JSON-подобной строки
        data = {
            'booking_code': self.booking_code,
            'movie': movie_title,
            'hall': hall_name,
            'row': self.seat.row,
            'seat': self.seat.number,
            'date': self.screening.start_time.strftime('%d.%m.%Y'),
            'time': self.screening.start_time.strftime('%H:%M'),
            'price': self.price,
            'status': self.status
        }
        
        # Преобразуем в строку для QR-кода
        qr_string = '\n'.join([f"{key}: {value}" for key, value in data.items()])
        return qr_string
    
    def get_qr_base64(self):
        """
        Возвращает QR-код в формате base64 для отображения на фронтенде
        """
        if not self.qr_code:
            return None
        
        import base64
        try:
            with open(self.qr_code.path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    
    @property
    def is_active(self):
        """Проверка, активно ли бронирование"""
        return self.status in ['confirmed', 'pending']
    
    @property
    def can_cancel(self):
        """Можно ли отменить бронирование"""
        if self.status in ['cancelled', 'used']:
            return False
        
        # Нельзя отменить за 30 минут до начала
        time_until = self.screening.start_time - timezone.now()
        return time_until.total_seconds() > 30 * 60