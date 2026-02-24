# tests/test_permissions.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from movies.models import Movie
from cinemas.models import CinemaHall

User = get_user_model()

class PermissionsTest(TestCase):
    """Тестирование прав доступа для разных ролей"""
    
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
        
        # Создаем тестовые данные для сеансов
        self.movie = Movie.objects.create(
            title='Тестовый фильм',
            duration=120
        )
        
        self.hall = CinemaHall.objects.create(
            name='Тестовый зал',
            rows=5,
            seats_per_row=8
        )
    
    def test_public_access(self):
        """Тест публичных эндпоинтов (доступны всем)"""
        endpoints = [
            ('GET', '/api/movies/'),
            ('GET', '/api/cinemas/halls/'),
            ('GET', '/api/screenings/'),
        ]
        
        for method, url in endpoints:
            if method == 'GET':
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"{method} {url}")
    
    def test_user_only_endpoints(self):
        """Тест эндпоинтов только для авторизованных пользователей"""
        self.client.force_authenticate(user=self.user)
        
        endpoints = [
            ('GET', '/api/auth/me/'),
            ('GET', '/api/bookings/my_bookings/'),
        ]
        
        for method, url in endpoints:
            if method == 'GET':
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"{method} {url}")
        
        # Проверяем без авторизации
        self.client.force_authenticate(user=None)
        for method, url in endpoints:
            if method == 'GET':
                response = self.client.get(url)
            self.assertEqual(response.status_code, 401, f"{method} {url}")
    
    def test_admin_only_endpoints(self):
        """Тест эндпоинтов только для админов"""
        # Сначала создаем тестовые данные
        movie = Movie.objects.create(title='Test', duration=120)
        hall = CinemaHall.objects.create(name='Test Hall', rows=5, seats_per_row=8)
        
        # Как админ
        self.client.force_authenticate(user=self.admin)
        
        # Тест создания фильма
        response = self.client.post('/api/movies/', {
            'title': 'Admin Movie',
            'duration': 120
        }, format='json')
        self.assertEqual(response.status_code, 201, "POST /api/movies/")
        
        # Тест создания зала
        response = self.client.post('/api/cinemas/halls/', {
            'name': 'Admin Hall',
            'rows': 5,
            'seats_per_row': 8
        }, format='json')
        self.assertEqual(response.status_code, 201, "POST /api/cinemas/halls/")
        
        # Тест создания сеанса с правильными данными
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        response = self.client.post('/api/screenings/', {
            'movie': movie.id,
            'hall': hall.id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'price_standard': 250,
            'price_vip': 350
        }, format='json')
        self.assertEqual(response.status_code, 201, "POST /api/screenings/")
        
        # Как обычный пользователь
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/movies/', {
            'title': 'User Movie',
            'duration': 120
        }, format='json')
        self.assertEqual(response.status_code, 403, "POST /api/movies/ (user)")
        
        response = self.client.post('/api/cinemas/halls/', {
            'name': 'User Hall',
            'rows': 5,
            'seats_per_row': 8
        }, format='json')
        self.assertEqual(response.status_code, 403, "POST /api/cinemas/halls/ (user)")
        
        # Без авторизации
        self.client.force_authenticate(user=None)
        
        response = self.client.post('/api/movies/', {
            'title': 'Anon Movie',
            'duration': 120
        }, format='json')
        self.assertEqual(response.status_code, 401, "POST /api/movies/ (anon)")