# tests/debug_post.py
import requests
from datetime import datetime, timedelta
import time
import sys
import io

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'http://127.0.0.1:8000/api'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

print("ДИАГНОСТИКА POST ЗАПРОСОВ")
print("="*60)

# 1. Логин админа
r = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
if r.status_code != 200:
    print("Не удалось войти как админ")
    exit()

token = r.json().get('access')
headers = {'Authorization': f'Bearer {token}'}
print("Успешный вход как админ")

# 2. Создаём фильм
print("\nСоздание фильма...")
movie_data = {
    'title': f'Тестовый фильм {int(time.time())}',
    'duration': 120
}
movie_resp = requests.post(f"{BASE_URL}/movies/", json=movie_data, headers=headers)
print(f"Статус: {movie_resp.status_code}")
if movie_resp.status_code == 201:
    movie_id = movie_resp.json().get('id')
    print(f"Фильм ID: {movie_id}")
else:
    print("Не удалось создать фильм")
    exit()

# 3. Создаём зал
print("\nСоздание зала...")
hall_data = {
    'name': f'Тестовый зал {int(time.time())}',
    'rows': 5,
    'seats_per_row': 8
}
hall_resp = requests.post(f"{BASE_URL}/cinemas/halls/", json=hall_data, headers=headers)
print(f"Статус: {hall_resp.status_code}")
if hall_resp.status_code == 201:
    hall_id = hall_resp.json().get('id')
    print(f"Зал ID: {hall_id}")
else:
    print("Не удалось создать зал")
    exit()

# 4. Создаём сеанс
print("\nСоздание сеанса...")
tomorrow = datetime.now() + timedelta(days=1)
start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
end_time = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0).isoformat()

screening_data = {
    'movie': movie_id,
    'hall': hall_id,
    'start_time': start_time,
    'end_time': end_time,
    'price_standard': 250,
    'price_vip': 350
}

print(f"Данные: {screening_data}")
response = requests.post(f"{BASE_URL}/screenings/", json=screening_data, headers=headers)
print(f"Статус: {response.status_code}")

if response.status_code == 201:
    screening_id = response.json().get('id')
    print(f"Сеанс ID: {screening_id}")
    
    # 5. Проверяем доступные места
    print("\nПроверка доступных мест...")
    seats_response = requests.get(f"{BASE_URL}/screenings/{screening_id}/available_seats/")
    print(f"Статус: {seats_response.status_code}")
    
    if seats_response.status_code == 200:
        seats_data = seats_response.json()
        seats = seats_data.get('seats', [])
        available = [s for s in seats if s['status'] == 'available']
        print(f"Всего мест: {len(seats)}")
        print(f"Свободно мест: {len(available)}")
        
        if available:
            # 6. Пробуем забронировать место
            print("\nСоздание бронирования...")
            booking_data = {
                'screening': screening_id,
                'seat_ids': [available[0]['id']]
            }
            
            booking_response = requests.post(
                f"{BASE_URL}/bookings/", 
                json=booking_data, 
                headers=headers
            )
            print(f"Статус: {booking_response.status_code}")
            if booking_response.status_code == 201:
                print(f"Бронирование создано: {booking_response.json()}")
            else:
                print(f"Ошибка: {booking_response.text}")
else:
    print(f"Ошибка создания сеанса: {response.text}")