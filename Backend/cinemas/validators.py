from django.utils import timezone
from django.db.models import Q

class CinemaHallValidator:
    """
    Валидатор для кинозалов
    """
    
    @staticmethod
    def validate_hall_dimensions(rows, seats_per_row):
        """
        Проверка размеров зала
        """
        errors = {}
        
        # Минимальные размеры
        if rows < 1:
            errors['rows'] = "Количество рядов должно быть не менее 1"
        if rows > 50:
            errors['rows'] = "Количество рядов не может превышать 50"
        
        if seats_per_row < 1:
            errors['seats_per_row'] = "Количество мест в ряду должно быть не менее 1"
        if seats_per_row > 30:
            errors['seats_per_row'] = "Количество мест в ряду не может превышать 30"
        
        return errors
    
    @staticmethod
    def validate_hall_name(name, exclude_id=None):
        """
        Проверка уникальности названия зала
        """
        from .models import CinemaHall
        
        queryset = CinemaHall.objects.filter(name=name)
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        
        if queryset.exists():
            return {
                'valid': False,
                'error': "Зал с таким названием уже существует"
            }
        
        return {'valid': True}
    
    @staticmethod
    def validate_hall_deletion(hall):
        """
        Проверка возможности удаления зала
        """
        from screenings.models import Screening
        from bookings.models import Booking
        
        # Проверка на будущие сеансы
        future_screenings = Screening.objects.filter(
            hall=hall,
            start_time__gt=timezone.now(),
            is_active=True
        ).exists()
        
        if future_screenings:
            return {
                'valid': False,
                'error': "Нельзя удалить зал, на который запланированы будущие сеансы"
            }
        
        # Проверка на активные бронирования
        active_bookings = Booking.objects.filter(
            screening__hall=hall,
            status__in=['confirmed', 'pending']
        ).exists()
        
        if active_bookings:
            return {
                'valid': False,
                'error': "Нельзя удалить зал, на который есть активные бронирования"
            }
        
        return {'valid': True}


class SeatValidator:
    """
    Валидатор для мест
    """
    
    @staticmethod
    def validate_seat_number(row, number, hall):
        """
        Проверка корректности номера места
        """
        if number < 1 or number > hall.seats_per_row:
            return {
                'valid': False,
                'error': f"Номер места {number} недопустим для зала с {hall.seats_per_row} местами в ряду"
            }
        
        if row < 1 or row > hall.rows:
            return {
                'valid': False,
                'error': f"Номер ряда {row} недопустим для зала с {hall.rows} рядами"
            }
        
        return {'valid': True}
    
    @staticmethod
    def validate_seat_type_change(seat, new_type):
        """
        Проверка возможности изменения типа места
        """
        from bookings.models import Booking
        
        # Если место уже забронировано на будущие сеансы, нельзя менять его тип
        has_future_bookings = Booking.objects.filter(
            seat=seat,
            screening__start_time__gt=timezone.now(),
            status__in=['confirmed', 'pending']
        ).exists()
        
        if has_future_bookings:
            return {
                'valid': False,
                'error': "Нельзя изменить тип места, на которое есть будущие бронирования"
            }
        
        return {'valid': True}
    
    @staticmethod
    def validate_bulk_seat_update(hall, seat_ids, new_type):
        """
        Проверка массового обновления мест
        """
        from bookings.models import Booking
        
        # Проверка, что места существуют в этом зале
        from .models import Seat
        seats = Seat.objects.filter(id__in=seat_ids, hall=hall)
        if seats.count() != len(seat_ids):
            return {
                'valid': False,
                'error': "Некоторые места не найдены в этом зале"
            }
        
        # Проверка на будущие бронирования
        has_future_bookings = Booking.objects.filter(
            seat_id__in=seat_ids,
            screening__start_time__gt=timezone.now(),
            status__in=['confirmed', 'pending']
        ).exists()
        
        if has_future_bookings:
            return {
                'valid': False,
                'error': "Некоторые места имеют будущие бронирования"
            }
        
        return {'valid': True}