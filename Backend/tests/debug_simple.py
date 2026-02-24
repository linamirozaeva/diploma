# tests/debug_simple.py
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

print("ПРОСТАЯ ДИАГНОСТИКА")
print("="*50)

# 1. Проверка подключения
try:
    r = requests.get("http://127.0.0.1:8000/")
    print(f"Сервер отвечает: {r.status_code}")
except:
    print("Сервер не отвечает!")
    exit()

# 2. Логин админа
r = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
if r.status_code == 200:
    token = r.json().get('access')
    headers = {'Authorization': f'Bearer {token}'}
    print("Успешный вход как админ")
else:
    print(f"Ошибка входа: {r.status_code}")
    exit()

# 3. Создание фильма (упрощенно)
print("\nСоздание фильма:")
movie_data = {
    'title': 'Тестовый фильм',
    'duration': 120
}
r = requests.post(f"{BASE_URL}/movies/", json=movie_data, headers=headers)
print(f"Статус: {r.status_code}")
if r.status_code == 201:
    print(f"Ответ: {json.dumps(r.json(), indent=2, ensure_ascii=False)}")
else:
    print(f"Текст ошибки: {r.text[:200]}")