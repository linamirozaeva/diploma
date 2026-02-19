from django.utils import timezone
from datetime import timedelta

class BookingValidator:
    """
    Валидатор для бронирований
    """
    
    @staticmethod
    def validate_seats_availability(screening, seat_ids, exclude_booking_id=None):
        """
        Проверка доступности мест на сеанс
        Возвращает словарь с информацией о доступности
        """
        from .models import Booking
        from cinemas.models import Seat
        
        result = {
            'available': True,
            'available_seats': [],
            'unavailable_seats': [],
            'message': '',
            'details': {}
        }
        
        # Проверка 1: Существуют ли места в этом зале
        seats = Seat.objects.filter(id__in=seat_ids, hall=screening.hall)
        found_ids = set(seats.values_list('id', flat=True))
        requested_ids = set(seat_ids)
        
        missing_ids = requested_ids - found_ids
        if missing_ids:
            result['available'] = False
            result['unavailable_seats'].extend(list(missing_ids))
            result['message'] += f"Места {missing_ids} не найдены в этом зале. "
            result['details']['missing'] = list(missing_ids)
        
        # Проверка 2: Неактивные места
        inactive_seats = seats.filter(is_active=False).values_list('id', flat=True)
        if inactive_seats:
            inactive_list = list(inactive_seats)
            result['available'] = False
            result['unavailable_seats'].extend(inactive_list)
            result['message'] += f"Места {inactive_list} неактивны. "
            result['details']['inactive'] = inactive_list
        
        # Проверка 3: Уже забронированные места
        booked_query = Booking.objects.filter(
            screening=screening,
            seat_id__in=seat_ids,
            status__in=['confirmed', 'pending']
        )
        
        if exclude_booking_id:
            booked_query = booked_query.exclude(pk=exclude_booking_id)
        
        booked_seats = set(booked_query.values_list('seat_id', flat=True))
        
        if booked_seats:
            booked_list = list(booked_seats)
            result['available'] = False
            result['unavailable_seats'].extend(booked_list)
            result['message'] += f"Места {booked_list} уже заняты. "
            result['details']['booked'] = booked_list
        
        # Определяем доступные места
        all_unavailable = set(result['unavailable_seats'])
        available_ids = requested_ids - all_unavailable
        result['available_seats'] = list(available_ids)
        
        if result['available']:
            result['message'] = "Все места доступны"
        
        return result
    
    @staticmethod
    def validate_booking_time(screening):
        """
        Проверка времени бронирования
        Возвращает словарь с результатом проверки
        """
        now = timezone.now()
        
        # Проверка 1: Нельзя бронировать на прошедшие сеансы
        if screening.start_time < now:
            return {
                'valid': False,
                'error': "Нельзя бронировать билеты на прошедшие сеансы",
                'code': 'past_screening'
            }
        
        # Проверка 2: Минимальное время до сеанса (15 минут)
        min_time_before = timedelta(minutes=15)
        time_until = screening.start_time - now
        if time_until < min_time_before:
            return {
                'valid': False,
                'error': "Слишком поздно для бронирования (менее 15 минут до начала)",
                'code': 'too_late',
                'minutes_left': int(time_until.total_seconds() / 60)
            }
        
        # Проверка 3: Максимальное время до сеанса (7 дней)
        max_time_before = timedelta(days=7)
        if screening.start_time - now > max_time_before:
            return {
                'valid': False,
                'error': "Бронирование открыто только за 7 дней до сеанса",
                'code': 'too_early'
            }
        
        return {
            'valid': True,
            'minutes_left': int((screening.start_time - now).total_seconds() / 60)
        }
    
    @staticmethod
    def validate_user_booking_limit(user, screening, requested_seats_count=1):
        """
        Проверка лимита бронирований для пользователя на один сеанс
        """
        from .models import Booking
        
        if not user or user.is_anonymous:
            return {'valid': True, 'message': 'Анонимный пользователь'}
        
        # Максимальное количество мест на одного пользователя на один сеанс
        MAX_SEATS_PER_USER = 5
        
        # Сколько уже забронировал пользователь на этот сеанс
        existing_bookings = Booking.objects.filter(
            user=user,
            screening=screening,
            status__in=['confirmed', 'pending']
        ).count()
        
        total_after_booking = existing_bookings + requested_seats_count
        
        if total_after_booking > MAX_SEATS_PER_USER:
            return {
                'valid': False,
                'error': (
                    f"Вы можете забронировать не более {MAX_SEATS_PER_USER} мест на один сеанс. "
                    f"Уже забронировано: {existing_bookings}"
                ),
                'code': 'limit_exceeded',
                'existing': existing_bookings,
                'max_allowed': MAX_SEATS_PER_USER,
                'requested': requested_seats_count
            }
        
        return {
            'valid': True,
            'existing': existing_bookings,
            'remaining': MAX_SEATS_PER_USER - existing_bookings
        }
    
    @staticmethod
    def validate_seat_selection(seats):
        """
        Проверка выбранных мест (например, чтобы они были в одном ряду)
        """
        if len(seats) <= 1:
            return {'valid': True}
        
        # Проверка, что все места в одном ряду (опционально)
        rows = set(seat.row for seat in seats)
        if len(rows) > 2:
            return {
                'valid': False,
                'error': "Места должны быть не более чем в 2 рядах",
                'code': 'too_many_rows'
            }
        
        # Проверка, что места идут подряд (опционально)
        if len(seats) > 1:
            # Группируем по рядам
            from collections import defaultdict
            seats_by_row = defaultdict(list)
            for seat in seats:
                seats_by_row[seat.row].append(seat.number)
            
            # Проверяем, что в каждом ряду места идут подряд
            for row, numbers in seats_by_row.items():
                numbers.sort()
                expected = list(range(numbers[0], numbers[-1] + 1))
                if numbers != expected:
                    return {
                        'valid': False,
                        'error': f"В ряду {row} места должны быть подряд",
                        'code': 'non_consecutive'
                    }
        
        return {'valid': True}


class BookingCancellationValidator:
    """
    Валидатор для отмены бронирований
    """
    
    @staticmethod
    def validate_cancellation(booking):
        """
        Проверка возможности отмены бронирования
        """
        # Проверка 1: Нельзя отменить уже отмененное
        if booking.status == 'cancelled':
            return {
                'valid': False,
                'error': "Бронирование уже отменено",
                'code': 'already_cancelled'
            }
        
        # Проверка 2: Нельзя отменить использованное
        if booking.status == 'used':
            return {
                'valid': False,
                'error': "Нельзя отменить использованный билет",
                'code': 'already_used'
            }
        
        # Проверка 3: Время до сеанса (минимум 30 минут для отмены)
        time_until = booking.screening.start_time - timezone.now()
        min_cancellation_time = timedelta(minutes=30)
        
        if time_until < min_cancellation_time:
            minutes_left = int(time_until.total_seconds() / 60)
            return {
                'valid': False,
                'error': f"Нельзя отменить бронирование менее чем за 30 минут до начала (осталось {minutes_left} мин)",
                'code': 'too_late_to_cancel',
                'minutes_left': minutes_left
            }
        
        return {
            'valid': True,
            'minutes_left': int(time_until.total_seconds() / 60)
        }