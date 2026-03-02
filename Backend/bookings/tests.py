from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from movies.models import Movie
from cinemas.models import CinemaHall, Seat
from screenings.models import Screening
from bookings.models import Booking

User = get_user_model()

class BookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Создаем администратора (для проверки прав)
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        
        self.movie = Movie.objects.create(
            title='Тестовый фильм',
            description='Описание',
            duration=120
        )
        
        self.hall = CinemaHall.objects.create(
            name='Тестовый зал',
            rows=10,
            seats_per_row=12
        )
        
        # Создаем места в зале
        for row in range(1, 11):
            for num in range(1, 13):
                Seat.objects.create(
                    hall=self.hall,
                    row=row,
                    number=num,
                    seat_type='standard'
                )
        
        self.start_time = timezone.now() + timedelta(days=1)
        self.end_time = self.start_time + timedelta(minutes=self.movie.duration)
        
        self.screening = Screening.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=self.start_time,
            end_time=self.end_time,
            price_standard=250,
            price_vip=350
        )
        
        self.seat = Seat.objects.first()

    def test_create_booking(self):
        """Тест создания бронирования обычным пользователем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/screenings/{self.screening.id}/book_seats/',
            {'seat_ids': [self.seat.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_booking_unauthorized(self):
        """Тест создания бронирования без авторизации"""
        response = self.client.post(
            f'/api/screenings/{self.screening.id}/book_seats/',
            {'seat_ids': [self.seat.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_booking_for_past_screening(self):
        """Тест создания бронирования на прошедший сеанс"""
        self.client.force_authenticate(user=self.user)
        
        past_screening = Screening.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=timezone.now() - timedelta(days=1),
            end_time=timezone.now() - timedelta(days=1, minutes=120),
            price_standard=250,
            price_vip=350
        )
        
        response = self.client.post(
            f'/api/screenings/{past_screening.id}/book_seats/',
            {'seat_ids': [self.seat.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_booking_for_already_booked_seat(self):
        """Тест создания бронирования на уже занятое место"""
        self.client.force_authenticate(user=self.user)
        
        # Первое бронирование
        response1 = self.client.post(
            f'/api/screenings/{self.screening.id}/book_seats/',
            {'seat_ids': [self.seat.id]},
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Второе бронирование того же места
        response2 = self.client.post(
            f'/api/screenings/{self.screening.id}/book_seats/',
            {'seat_ids': [self.seat.id]},
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_my_bookings(self):
        """Тест получения своих бронирований"""
        self.client.force_authenticate(user=self.user)
        
        # Создаем бронирование
        self.client.post(
            f'/api/screenings/{self.screening.id}/book_seats/',
            {'seat_ids': [self.seat.id]},
            format='json'
        )
        
        response = self.client.get('/api/bookings/my_bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_cancel_booking(self):
        """Тест отмены бронирования"""
        self.client.force_authenticate(user=self.user)
        
        # Создаем бронирование
        booking = Booking.objects.create(
            user=self.user,
            screening=self.screening,
            seat=self.seat,
            price=self.screening.price_standard,
            booking_code='TEST123',
            status='confirmed'
        )
        
        # Отменяем бронирование
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
    
    def test_admin_can_view_all_bookings(self):
        """Тест: администратор может видеть все бронирования"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_view_all_bookings(self):
        """Тест: обычный пользователь не может видеть все бронирования"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)