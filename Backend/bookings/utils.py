import qrcode
import io
import base64
from django.core.files.base import ContentFile
from django.conf import settings
import os

class QRCodeGenerator:
    """
    Класс для генерации и обработки QR-кодов
    """
    
    @staticmethod
    def generate_qr_code(data, box_size=10, border=4):
        """
        Генерация QR-кода из данных
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    
    @staticmethod
    def image_to_bytes(img, format='PNG'):
        """
        Конвертация изображения в bytes
        """
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        return buffer.getvalue()
    
    @staticmethod
    def image_to_base64(img, format='PNG'):
        """
        Конвертация изображения в base64 строку
        """
        bytes_data = QRCodeGenerator.image_to_bytes(img, format)
        return base64.b64encode(bytes_data).decode()
    
    @staticmethod
    def bytes_to_content_file(bytes_data, filename):
        """
        Создание ContentFile из bytes
        """
        return ContentFile(bytes_data, name=filename)
    
    @staticmethod
    def generate_booking_qr(booking):
        """
        Генерация QR-кода для бронирования
        """
        from .models import Booking
        
        # Получаем данные для QR
        qr_data = booking.get_qr_data()
        
        # Генерируем QR
        img = QRCodeGenerator.generate_qr_code(qr_data)
        
        # Конвертируем в bytes
        bytes_data = QRCodeGenerator.image_to_bytes(img)
        
        # Создаем файл
        filename = f"booking_{booking.booking_code}.png"
        return QRCodeGenerator.bytes_to_content_file(bytes_data, filename)


class QRCodeValidator:
    """
    Класс для валидации QR-кодов
    """
    
    @staticmethod
    def decode_qr_data(qr_data):
        """
        Декодирование данных из QR-кода
        """
        result = {}
        lines = qr_data.strip().split('\n')
        
        for line in lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                result[key.strip()] = value.strip()
        
        return result
    
    @staticmethod
    def validate_qr_data(data, expected_booking):
        """
        Проверка данных из QR-кода
        """
        if not data:
            return {'valid': False, 'error': 'Нет данных'}
        
        # Проверяем код бронирования
        if data.get('booking_code') != expected_booking.booking_code:
            return {'valid': False, 'error': 'Неверный код бронирования'}
        
        # Проверяем фильм
        expected_movie = expected_booking.screening.movie.title if expected_booking.screening.movie else "Не указан"
        if data.get('movie') != expected_movie:
            return {'valid': False, 'error': 'Неверный фильм'}
        
        # Проверяем дату и время
        expected_date = expected_booking.screening.start_time.strftime('%d.%m.%Y')
        expected_time = expected_booking.screening.start_time.strftime('%H:%M')
        
        if data.get('date') != expected_date:
            return {'valid': False, 'error': 'Неверная дата'}
        
        if data.get('time') != expected_time:
            return {'valid': False, 'error': 'Неверное время'}
        
        return {'valid': True}