# tests/test_admin.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

User = get_user_model()

class AdminSiteTest(TestCase):
    """Тестирование доступности админ-панели"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем суперпользователя для входа в админку
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Создаем обычного пользователя
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        
        # Создаем клиент для запросов
        self.client = Client()
    
    def test_admin_login_required(self):
        """Тест: вход в админку требует авторизации"""
        response = self.client.get('/admin/')
        # Должно перенаправлять на страницу логина
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)
    
    def test_admin_login_success(self):
        """Тест: успешный вход в админку"""
        # Логинимся как админ
        login = self.client.login(username='admin', password='admin123')
        self.assertTrue(login)
        
        # Проверяем доступ к админке
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Администрирование')
    
    def test_admin_login_fail(self):
        """Тест: неудачный вход в админку"""
        # Пытаемся залогиниться с неправильным паролем
        login = self.client.login(username='admin', password='wrongpass')
        self.assertFalse(login)
    
    def test_regular_user_cannot_access_admin(self):
        """Тест: обычный пользователь не может войти в админку"""
        login = self.client.login(username='user', password='user123')
        self.assertTrue(login)  # Логин успешен для сайта
        
        # Но не должен иметь доступ к админке
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Перенаправление на логин
    
    def test_user_model_admin(self):
        """Тест: модель User доступна в админке"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/users/user/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователи')
    
    def test_cinema_model_admin(self):
        """Тест: модель CinemaHall доступна в админке"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/cinemas/cinemahall/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Кинозалы')
    
    def test_movie_model_admin(self):
        """Тест: модель Movie доступна в админке"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/movies/movie/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Фильмы')
    
    def test_screening_model_admin(self):
        """Тест: модель Screening доступна в админке"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/screenings/screening/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сеансы')
    
    def test_booking_model_admin(self):
        """Тест: модель Booking доступна в админке"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/bookings/booking/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Бронирования')