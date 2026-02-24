# tests/test_cinemas.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cinemas.models import CinemaHall, Seat

User = get_user_model()

class CinemasTest(TestCase):
    """Тестирование кинозалов"""
    
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
        
        # Создаем тестовый зал с автоматическим созданием мест
        self.hall = CinemaHall.objects.create(
            name='Тестовый зал',
            rows=5,
            seats_per_row=8
        )
        
        # ВАЖНО: Вручную создаем места, так как авто-создание может не работать в тестах
        for row in range(1, 6):
            for num in range(1, 9):
                Seat.objects.create(
                    hall=self.hall,
                    row=row,
                    number=num,
                    seat_type='standard'
                )
    
    def test_list_halls_public(self):
        """Тест публичного доступа к списку залов"""
        response = self.client.get('/api/cinemas/halls/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_hall_admin(self):
        """Тест создания зала админом"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/cinemas/halls/', {
            'name': 'Новый зал',
            'rows': 10,
            'seats_per_row': 12,
            'description': 'Описание зала'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CinemaHall.objects.count(), 2)
        
        # Проверяем, что места создались
        new_hall = CinemaHall.objects.get(name='Новый зал')
        seats_count = Seat.objects.filter(hall=new_hall).count()
        self.assertEqual(seats_count, 120)  # 10*12
    
    def test_create_hall_user(self):
        """Тест создания зала обычным пользователем (должен быть запрет)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cinemas/halls/', {
            'name': 'Новый зал',
            'rows': 10,
            'seats_per_row': 12
        })
        self.assertEqual(response.status_code, 403)
    
    def test_create_hall_invalid_size(self):
        """Тест создания зала с некорректными размерами"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/cinemas/halls/', {
            'name': 'Новый зал',
            'rows': 100,  # слишком много
            'seats_per_row': 50  # слишком много
        })
        self.assertEqual(response.status_code, 400)
    
    def test_hall_seats(self):
        """Тест получения мест в зале"""
        response = self.client.get(f'/api/cinemas/halls/{self.hall.id}/seats/')
        self.assertEqual(response.status_code, 200)
        # Проверяем структуру ответа
        self.assertIn('seats', response.data)
        # В ответе может быть 'seats' или 'seats_by_row'
        if 'seats' in response.data:
            self.assertEqual(len(response.data['seats']), 40)  # 5*8
        elif 'seats_by_row' in response.data:
            total_seats = sum(len(seats) for seats in response.data['seats_by_row'].values())
            self.assertEqual(total_seats, 40)
    
    def test_update_seat_type_admin(self):
        """Тест изменения типа места админом"""
        self.client.force_authenticate(user=self.admin)
        
        # Получаем первое место
        seat = Seat.objects.filter(hall=self.hall).first()
        self.assertIsNotNone(seat, "Места должны существовать")
        
        response = self.client.post(
            f'/api/cinemas/halls/{self.hall.id}/update_seat_type/',
            {'seat_id': seat.id, 'seat_type': 'vip'}
        )
        self.assertEqual(response.status_code, 200)
        
        seat.refresh_from_db()
        self.assertEqual(seat.seat_type, 'vip')
    
    def test_update_seat_type_user(self):
        """Тест изменения типа места обычным пользователем (должен быть запрет)"""
        self.client.force_authenticate(user=self.user)
        
        seat = Seat.objects.filter(hall=self.hall).first()
        self.assertIsNotNone(seat)
        
        response = self.client.post(
            f'/api/cinemas/halls/{self.hall.id}/update_seat_type/',
            {'seat_id': seat.id, 'seat_type': 'vip'}
        )
        self.assertEqual(response.status_code, 403)