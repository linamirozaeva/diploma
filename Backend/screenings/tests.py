from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from movies.models import Movie
from cinemas.models import CinemaHall, Seat
from screenings.models import Screening

User = get_user_model()

class ScreeningTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', 
            email='admin@test.com', 
            password='admin123'
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
        
        # Создаем места
        for row in range(1, 11):
            for num in range(1, 13):
                Seat.objects.create(
                    hall=self.hall,
                    row=row,
                    number=num,
                    seat_type='standard'
                )
        
        self.start_time = timezone.now() + timedelta(days=1)
        
        self.screening_data = {
            'movie': self.movie.id,
            'hall': self.hall.id,
            'start_time': self.start_time.isoformat(),
            'price_standard': 250,
            'price_vip': 350
        }

    def test_create_screening(self):
        """Тест создания сеанса"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/screenings/', self.screening_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Screening.objects.count(), 1)

    def test_available_seats(self):
        """Тест получения доступных мест"""
        self.client.force_authenticate(user=self.admin)
        
        # Создаем сеанс
        screening = Screening.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=self.start_time,
            end_time=self.start_time + timedelta(minutes=self.movie.duration),
            price_standard=250,
            price_vip=350
        )
        
        response = self.client.get(f'/api/screenings/{screening.id}/available_seats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.hall.total_seats)

    def test_prevent_overlapping_screenings(self):
        """Тест предотвращения пересечения сеансов"""
        self.client.force_authenticate(user=self.admin)
        
        # Создаем первый сеанс
        screening1 = Screening.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=self.start_time,
            end_time=self.start_time + timedelta(minutes=self.movie.duration),
            price_standard=250,
            price_vip=350
        )
        
        # Пытаемся создать второй сеанс через API
        response2 = self.client.post('/api/screenings/', self.screening_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)