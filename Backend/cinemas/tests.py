from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import CinemaHall, Seat

User = get_user_model()

class CinemaHallTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', 
            email='admin@test.com', 
            password='admin123'
        )
        
        self.hall_data = {
            'name': 'Тестовый зал',
            'rows': 10,
            'seats_per_row': 12,
            'description': 'Описание тестового зала'
        }

    def test_create_hall(self):
        """Тест создания зала"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/cinemas/halls/', self.hall_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CinemaHall.objects.count(), 1)
        
        # Проверяем, что места создались автоматически
        hall = CinemaHall.objects.first()
        self.assertEqual(hall.seats.count(), 10 * 12)

    def test_list_halls(self):
        """Тест получения списка залов"""
        CinemaHall.objects.create(**self.hall_data)
        response = self.client.get('/api/cinemas/halls/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_get_hall_seats(self):
        """Тест получения мест зала"""
        hall = CinemaHall.objects.create(**self.hall_data)
        
        # Создаем места вручную для теста
        for row in range(1, hall.rows + 1):
            for num in range(1, hall.seats_per_row + 1):
                Seat.objects.create(
                    hall=hall,
                    row=row,
                    number=num,
                    seat_type='standard'
                )
        
        response = self.client.get(f'/api/cinemas/halls/{hall.id}/seats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), hall.rows * hall.seats_per_row)

    def test_update_seat_type(self):
        """Тест обновления типа места"""
        self.client.force_authenticate(user=self.admin)
        hall = CinemaHall.objects.create(**self.hall_data)
        
        # Создаем место
        seat = Seat.objects.create(
            hall=hall,
            row=1,
            number=1,
            seat_type='standard'
        )
        
        response = self.client.post(
            f'/api/cinemas/halls/{hall.id}/update_seat_type/',
            {'seat_id': seat.id, 'seat_type': 'vip'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        seat.refresh_from_db()
        self.assertEqual(seat.seat_type, 'vip')