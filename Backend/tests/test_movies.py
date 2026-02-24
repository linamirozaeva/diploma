# tests/test_movies.py
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from movies.models import Movie

User = get_user_model()

class MoviesTest(TestCase):
    """Тестирование фильмов"""
    
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
        
        # Создаем тестовый фильм
        self.movie = Movie.objects.create(
            title='Тестовый фильм',
            description='Описание',
            duration=120,
            director='Тестовый режиссер'
        )
    
    def test_list_movies_public(self):
        """Тест публичного доступа к списку фильмов"""
        response = self.client.get('/api/movies/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
    
    def test_create_movie_admin(self):
        """Тест создания фильма админом"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/movies/', {
            'title': 'Новый фильм',
            'description': 'Описание',
            'duration': 90,
            'director': 'Новый режиссер'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Movie.objects.count(), 2)
    
    def test_create_movie_user(self):
        """Тест создания фильма обычным пользователем (должен быть запрет)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/movies/', {
            'title': 'Новый фильм',
            'description': 'Описание',
            'duration': 90
        })
        self.assertEqual(response.status_code, 403)
    
    def test_create_movie_invalid_duration(self):
        """Тест создания фильма с некорректной длительностью"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/movies/', {
            'title': 'Новый фильм',
            'duration': 5  # слишком короткий
        })
        self.assertEqual(response.status_code, 400)
    
    def test_movie_detail(self):
        """Тест получения деталей фильма"""
        response = self.client.get(f'/api/movies/{self.movie.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Тестовый фильм')
    
    def test_update_movie_admin(self):
        """Тест обновления фильма админом"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f'/api/movies/{self.movie.id}/',
            {'title': 'Обновленный фильм'}
        )
        self.assertEqual(response.status_code, 200)
        
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, 'Обновленный фильм')
    
    def test_delete_movie_admin(self):
        """Тест удаления фильма админом"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/movies/{self.movie.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Movie.objects.count(), 0)