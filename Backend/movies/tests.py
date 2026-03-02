from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Movie

User = get_user_model()

class MovieTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user', password='pass123')
        self.admin = User.objects.create_superuser(
            username='admin', 
            email='admin@test.com', 
            password='admin123'
        )
        
        self.movie_data = {
            'title': 'Тестовый фильм',
            'description': 'Описание тестового фильма',
            'duration': 120,
            'release_date': '2025-01-01',
            'country': 'Россия',
            'director': 'Тестовый режиссер',
            'cast': 'Актер 1, Актер 2',
            'age_rating': '12+'
        }

    def test_list_movies_unauthorized(self):
        """Тест получения списка фильмов без авторизации"""
        response = self.client.get('/api/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_movie_as_admin(self):
        """Тест создания фильма администратором"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/movies/', self.movie_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 1)

    def test_create_movie_as_user(self):
        """Тест создания фильма обычным пользователем (должен быть запрещен)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/movies/', self.movie_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_movie_detail(self):
        """Тест получения детальной информации о фильме"""
        movie = Movie.objects.create(**self.movie_data)
        response = self.client.get(f'/api/movies/{movie.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.movie_data['title'])

    def test_search_movies(self):
        """Тест поиска фильмов"""
        Movie.objects.create(**self.movie_data)
        response = self.client.get('/api/movies/?search=Тестовый')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_filter_by_duration(self):
        """Тест фильтрации по длительности"""
        Movie.objects.create(**self.movie_data)
        response = self.client.get('/api/movies/?min_duration=100&max_duration=140')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)