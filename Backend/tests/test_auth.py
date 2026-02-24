# tests/test_auth.py
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTest(TestCase):
    """Тестирование аутентификации"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': 'test@example.com',
            'first_name': 'Тест',
            'last_name': 'Пользователь'
        }
    
    def test_register(self):
        """Тест регистрации нового пользователя"""
        response = self.client.post('/api/auth/register/', self.user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
    
    def test_register_duplicate(self):
        """Тест регистрации с существующим username"""
        self.client.post('/api/auth/register/', self.user_data)
        response = self.client.post('/api/auth/register/', self.user_data)
        self.assertEqual(response.status_code, 400)
    
    def test_login(self):
        """Тест входа в систему"""
        self.client.post('/api/auth/register/', self.user_data)
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_wrong_password(self):
        """Тест входа с неправильным паролем"""
        self.client.post('/api/auth/register/', self.user_data)
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_profile(self):
        """Тест получения профиля"""
        self.client.post('/api/auth/register/', self.user_data)
        login = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = login.data['access']
        
        response = self.client.get('/api/auth/me/', 
            HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_profile_no_token(self):
        """Тест доступа к профилю без токена"""
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 401)