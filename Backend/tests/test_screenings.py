# tests/test_screenings.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from movies.models import Movie
from cinemas.models import CinemaHall, Seat
from screenings.models import Screening
from bookings.models import Booking

User = get_user_model()

class ScreeningsTest(TestCase):
    """Тестирование сеансов"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаем админа
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='user123'
        )
        
        # Создаем тестовые данные
        self.movie = Movie.objects.create(
            title='Тестовый фильм',
            duration=120
        )
        
        self.hall = CinemaHall.objects.create(
            name='Тестовый зал',
            rows=5,
            seats_per_row=8
        )
        
        # Создаем места
        for row in range(1, 6):
            for num in range(1, 9):
                Seat.objects.create(
                    hall=self.hall,
                    row=row,
                    number=num,
                    seat_type='standard'
                )
        
        # Создаем сеанс на будущее
        self.screening = Screening.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            price_standard=250,
            price_vip=350
        )
    
    def test_list_screenings_public(self):
        """Тест публичного доступа к списку сеансов"""
        response = self.client.get('/api/screenings/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_screening_admin(self):
        """Тест создания сеанса админом"""
        self.client.force_authenticate(user=self.admin)
        start = timezone.now() + timedelta(days=2)
        end = start + timedelta(hours=2)
        
        response = self.client.post('/api/screenings/', {
            'movie': self.movie.id,
            'hall': self.hall.id,
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'price_standard': 300,
            'price_vip': 400
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Screening.objects.count(), 2)
    
    def test_create_screening_user(self):
        """Тест создания сеанса обычным пользователем (должен быть запрет)"""
        self.client.force_authenticate(user=self.user)
        start = timezone.now() + timedelta(days=2)
        end = start + timedelta(hours=2)
        
        response = self.client.post('/api/screenings/', {
            'movie': self.movie.id,
            'hall': self.hall.id,
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'price_standard': 300,
            'price_vip': 400
        }, format='json')
        self.assertEqual(response.status_code, 403)
    
    def test_screening_overlap(self):
        """Тест пересечения сеансов"""
        self.client.force_authenticate(user=self.admin)
        start = self.screening.start_time + timedelta(minutes=30)
        end = self.screening.end_time - timedelta(minutes=30)
        
        response = self.client.post('/api/screenings/', {
            'movie': self.movie.id,
            'hall': self.hall.id,
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'price_standard': 300,
            'price_vip': 400
        }, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_available_seats_public(self):
        """Тест получения доступных мест (публичный доступ)"""
        response = self.client.get(f'/api/screenings/{self.screening.id}/available_seats/')
        self.assertEqual(response.status_code, 200)
        # Проверяем структуру ответа
        self.assertIn('seats_by_row', response.data)
        # Подсчитываем общее количество мест
        total_seats = sum(len(seats) for seats in response.data['seats_by_row'].values())
        self.assertEqual(total_seats, 40)
    
    def test_check_seats_public(self):
        """Тест проверки мест (публичный доступ)"""
        response = self.client.post(
            f'/api/screenings/{self.screening.id}/check_seats/',
            {'seat_ids': [1, 2, 3]},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['available'])
    
    def test_check_seats_with_booked(self):
        """Тест проверки уже занятых мест"""
        # Создаем пользователя и бронирование
        booker = User.objects.create_user(username='booker', password='book123')
        self.client.force_authenticate(user=booker)
        
        # Получаем ID реального места
        seat = Seat.objects.filter(hall=self.hall).first()
        
        booking_response = self.client.post('/api/bookings/', {
            'screening': self.screening.id,
            'seat_ids': [seat.id]
        }, format='json')
        self.assertEqual(booking_response.status_code, 201)
        
        # Проверяем места без авторизации
        self.client.force_authenticate(user=None)
        response = self.client.post(
            f'/api/screenings/{self.screening.id}/check_seats/',
            {'seat_ids': [seat.id, seat.id + 1]},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['available'])
        self.assertIn(seat.id, response.data['booked_seats'])
    
    def test_screenings_by_date(self):
        """Тест получения сеансов по датам"""
        response = self.client.get('/api/screenings/by_date/?days=7')
        self.assertEqual(response.status_code, 200)