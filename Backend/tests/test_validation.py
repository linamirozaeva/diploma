# tests/test_validation.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, datetime
from cinemas.validators import CinemaHallValidator, SeatValidator
from movies.validators import MovieValidator
from screenings.validators import ScreeningValidator, BatchScreeningValidator
from bookings.validators import BookingValidator, BookingCancellationValidator
from movies.models import Movie
from cinemas.models import CinemaHall, Seat
from screenings.models import Screening
from bookings.models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()

class CinemaHallValidatorTest(TestCase):
    """Тестирование валидаторов кинозалов"""
    
    def test_validate_hall_dimensions(self):
        """Тест проверки размеров зала"""
        # Некорректные размеры
        errors = CinemaHallValidator.validate_hall_dimensions(rows=100, seats_per_row=50)
        self.assertIn('rows', errors)
        self.assertIn('seats_per_row', errors)
        
        # Корректные размеры
        errors = CinemaHallValidator.validate_hall_dimensions(rows=10, seats_per_row=15)
        self.assertEqual(errors, {})
        
        # Граничные значения
        errors = CinemaHallValidator.validate_hall_dimensions(rows=1, seats_per_row=1)
        self.assertEqual(errors, {})
        
        errors = CinemaHallValidator.validate_hall_dimensions(rows=50, seats_per_row=30)
        self.assertEqual(errors, {})
    
    def test_validate_seat_number(self):
        """Тест проверки номера места"""
        hall = CinemaHall(rows=10, seats_per_row=15)
        
        # Корректный номер
        result = SeatValidator.validate_seat_number(row=5, number=8, hall=hall)
        self.assertTrue(result['valid'])
        
        # Некорректный ряд
        result = SeatValidator.validate_seat_number(row=20, number=8, hall=hall)
        self.assertFalse(result['valid'])
        
        # Некорректное место
        result = SeatValidator.validate_seat_number(row=5, number=30, hall=hall)
        self.assertFalse(result['valid'])

class MovieValidatorTest(TestCase):
    """Тестирование валидаторов фильмов"""
    
    def test_validate_movie_duration(self):
        """Тест проверки длительности фильма"""
        # Слишком короткий
        errors = MovieValidator.validate_movie_duration(10)
        self.assertIn('duration', errors)
        
        # Слишком длинный
        errors = MovieValidator.validate_movie_duration(400)
        self.assertIn('duration', errors)
        
        # Корректная длительность
        errors = MovieValidator.validate_movie_duration(120)
        self.assertEqual(errors, {})
    
    def test_validate_title(self):
        """Тест проверки названия фильма"""
        # Пустое название
        errors = MovieValidator.validate_title('')
        self.assertIn('title', errors)
        
        # Слишком короткое
        errors = MovieValidator.validate_title('A')
        self.assertIn('title', errors)
        
        # Слишком длинное
        errors = MovieValidator.validate_title('A' * 300)
        self.assertIn('title', errors)
        
        # Корректное название
        errors = MovieValidator.validate_title('Тестовый фильм')
        self.assertEqual(errors, {})
    
    def test_validate_release_date(self):
        """Тест проверки даты выхода"""
        from datetime import date
        # Слишком старая дата
        errors = MovieValidator.validate_release_date(date(1800, 1, 1))
        self.assertIn('release_date', errors)
        
        # Корректная дата
        errors = MovieValidator.validate_release_date(date(2023, 1, 1))
        self.assertEqual(errors, {})

class ScreeningValidatorTest(TestCase):
    """Тестирование валидаторов сеансов"""
    
    def setUp(self):
        self.hall = CinemaHall.objects.create(
            name='Тестовый зал',
            rows=5,
            seats_per_row=8
        )
        self.movie = Movie.objects.create(
            title='Тестовый фильм',
            duration=120
        )
    
    def test_validate_screening_times(self):
        """Тест проверки времени сеанса"""
        now = timezone.now()
        
        # Корректное время (в рабочее время)
        start = datetime(now.year, now.month, now.day, 10, 0) + timedelta(days=1)
        end = start + timedelta(hours=2)
        start = timezone.make_aware(start)
        end = timezone.make_aware(end)
        
        errors = ScreeningValidator.validate_screening_times(start, end, self.hall)
        self.assertEqual(errors, {})
        
        # end_time раньше start_time
        errors = ScreeningValidator.validate_screening_times(end, start, self.hall)
        self.assertIn('end_time', errors)
        
        # Слишком короткий сеанс
        short_end = start + timedelta(minutes=15)
        errors = ScreeningValidator.validate_screening_times(start, short_end, self.hall)
        self.assertIn('duration', errors)
        
        # Слишком длинный сеанс
        long_end = start + timedelta(hours=5)
        errors = ScreeningValidator.validate_screening_times(start, long_end, self.hall)
        self.assertIn('duration', errors)
    
    def test_validate_screening_with_movie(self):
        """Тест соответствия длительности сеанса фильму"""
        now = timezone.now()
        
        # Корректная длительность (ровно под фильм)
        start = now + timedelta(days=1)
        end = start + timedelta(minutes=self.movie.duration)
        
        errors = ScreeningValidator.validate_screening_with_movie(self.movie, start, end)
        self.assertEqual(errors, {})
        
        # Слишком короткий сеанс
        short_end = start + timedelta(minutes=self.movie.duration - 30)
        errors = ScreeningValidator.validate_screening_with_movie(self.movie, start, short_end)
        self.assertIn('duration', errors)
        
        # Слишком длинный сеанс
        long_end = start + timedelta(minutes=self.movie.duration + 60)
        errors = ScreeningValidator.validate_screening_with_movie(self.movie, start, long_end)
        self.assertIn('duration', errors)
    
    def test_validate_price_range(self):
        """Тест проверки цен"""
        # Корректные цены
        errors = ScreeningValidator.validate_price_range(250, 350)
        self.assertEqual(errors, {})
        
        # VIP дешевле обычных
        errors = ScreeningValidator.validate_price_range(350, 250)
        self.assertIn('price_vip', errors)
        
        # Отрицательные цены
        errors = ScreeningValidator.validate_price_range(-100, 350)
        self.assertIn('price_standard', errors)

class BookingValidatorTest(TestCase):
    """Тестирование валидаторов бронирований"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
        
        self.hall = CinemaHall.objects.create(
            name='Тестовый зал',
            rows=5,
            seats_per_row=8
        )
        
        self.seat1 = Seat.objects.create(
            hall=self.hall,
            row=1,
            number=1,
            seat_type='standard'
        )
        self.seat2 = Seat.objects.create(
            hall=self.hall,
            row=1,
            number=2,
            seat_type='standard'
        )
        
        self.movie = Movie.objects.create(
            title='Тестовый фильм',
            duration=120
        )
        
        self.screening = Screening.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            price_standard=250,
            price_vip=350
        )
    
    def test_validate_booking_time(self):
        """Тест проверки времени бронирования"""
        # Будущий сеанс (корректно)
        result = BookingValidator.validate_booking_time(self.screening)
        self.assertTrue(result['valid'])
        
        # Прошедший сеанс
        self.screening.start_time = timezone.now() - timedelta(hours=1)
        result = BookingValidator.validate_booking_time(self.screening)
        self.assertFalse(result['valid'])
    
    def test_validate_seats_availability(self):
        """Тест проверки доступности мест"""
        # Все места свободны
        result = BookingValidator.validate_seats_availability(
            self.screening, [self.seat1.id, self.seat2.id]
        )
        self.assertTrue(result['available'])
        
        # Бронируем одно место
        Booking.objects.create(
            user=self.user,
            screening=self.screening,
            seat=self.seat1,
            booking_code='TEST123',
            price=250,
            status='confirmed'
        )
        
        # Проверяем с учетом занятого места
        result = BookingValidator.validate_seats_availability(
            self.screening, [self.seat1.id, self.seat2.id]
        )
        self.assertFalse(result['available'])
        self.assertIn(self.seat1.id, result['unavailable_seats'])
    
    def test_validate_user_booking_limit(self):
        """Тест проверки лимита пользователя"""
        # Лимит не превышен
        result = BookingValidator.validate_user_booking_limit(
            self.user, self.screening, requested_seats_count=2
        )
        self.assertTrue(result['valid'])
        
        # Бронируем 4 места
        for i in range(4):
            seat = Seat.objects.create(
                hall=self.hall,
                row=1,
                number=10 + i,
                seat_type='standard'
            )
            Booking.objects.create(
                user=self.user,
                screening=self.screening,
                seat=seat,
                booking_code=f'TEST{i}',
                price=250,
                status='confirmed'
            )
        
        # Пытаемся забронировать еще 2 (всего будет 6 > лимита 5)
        result = BookingValidator.validate_user_booking_limit(
            self.user, self.screening, requested_seats_count=2
        )
        self.assertFalse(result['valid'])
    
    def test_cancellation_validator(self):
        """Тест проверки отмены бронирования"""
        booking = Booking.objects.create(
            user=self.user,
            screening=self.screening,
            seat=self.seat1,
            booking_code='TEST123',
            price=250,
            status='confirmed'
        )
        
        # Можно отменить
        result = BookingCancellationValidator.validate_cancellation(booking)
        self.assertTrue(result['valid'])
        
        # Уже отменено
        booking.status = 'cancelled'
        result = BookingCancellationValidator.validate_cancellation(booking)
        self.assertFalse(result['valid'])
        
        # Уже использовано
        booking.status = 'used'
        result = BookingCancellationValidator.validate_cancellation(booking)
        self.assertFalse(result['valid'])