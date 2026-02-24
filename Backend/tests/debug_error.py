# tests/debug_error.py
import requests
import re

BASE_URL = 'http://127.0.0.1:8000'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

print("ПОИСК ОТСУТСТВУЮЩЕГО ИМПОРТА")
print("="*60)

# Логин админа
r = requests.post(f"{BASE_URL}/api/auth/login/", json=ADMIN_CREDENTIALS)
token = r.json().get('access')
headers = {'Authorization': f'Bearer {token}'}

# Отправка запроса для получения ошибки
data = {
    'movie': 1,
    'hall': 1,
    'start_time': '2026-02-25T10:00:00',
    'end_time': '2026-02-25T12:00:00',
    'price_standard': 250,
    'price_vip': 350
}

response = requests.post(f"{BASE_URL}/api/screenings/", json=data, headers=headers)

if response.status_code == 500:
    # Ищем имя отсутствующего класса в HTML
    match = re.search(r"name '(\w+)' is not defined", response.text)
    if match:
        missing_name = match.group(1)
        print(f"ОТСУТСТВУЕТ ИМПОРТ: {missing_name}")
    else:
        print("Не удалось найти имя в ошибке")