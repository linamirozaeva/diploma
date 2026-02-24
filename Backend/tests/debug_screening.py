# tests/debug_screening.py
import requests
from datetime import datetime, timedelta
import time

BASE_URL = 'http://127.0.0.1:8000/api'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

print("ПРОВЕРКА СОЗДАНИЯ СЕАНСА")
print("="*60)

# 1. Логин админа
r = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
if r.status_code != 200:
    print("Не удалось войти как админ")
    exit()

token = r.json().get('access')
headers = {'Authorization': f'Bearer {token}'}
print("Успешный вход как админ")

# 2. Создаём НОВЫЙ зал для тестов
print("\nСоздание нового зала...")
hall_data = {
    'name': f'Тестовый зал {int(time.time())}',
    'rows': 5,
    'seats_per_row': 8
}
hall_response = requests.post(f"{BASE_URL}/cinemas/halls/", json=hall_data, headers=headers)

if hall_response.status_code != 201:
    print("Не удалось создать зал")
    exit()

hall_id = hall_response.json().get('id')
print(f"Создан новый зал ID: {hall_id}")

# 3. Создаём НОВЫЙ фильм для тестов
print("\nСоздание нового фильма...")
movie_data = {
    'title': f'Тестовый фильм {int(time.time())}',
    'duration': 120
}
movie_response = requests.post(f"{BASE_URL}/movies/", json=movie_data, headers=headers)

if movie_response.status_code != 201:
    print("Не удалось создать фильм")
    exit()

movie_id = movie_response.json().get('id')
print(f"Создан новый фильм ID: {movie_id}")

# 4. Создаём сеанс в НОВОМ зале
print(f"\nИспользуем фильм ID: {movie_id}, зал ID: {hall_id}")

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

print(f"\nОтправка данных: {screening_data}")
response = requests.post(f"{BASE_URL}/screenings/", json=screening_data, headers=headers)

print(f"\nСтатус: {response.status_code}")

if response.status_code == 201:
    print(f"Ответ: {response.json()}")
elif response.status_code == 400:
    print(f"Ошибка валидации: {response.json()}")
else:
    print(f"Текст ошибки: {response.text[:500]}")