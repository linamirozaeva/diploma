# tests/test_integration_simple.py
"""
Упрощенная версия интеграционных тестов
"""

import requests
import sys
import io
import time
from datetime import datetime, timedelta

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'http://127.0.0.1:8000/api'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

def print_result(name, status, expected):
    icon = "yes" if status == expected else "no"
    print(f"{icon} {name}: {status} (ожидалось {expected})")

def run_simple_tests():
    print("ЗАПУСК УПРОЩЕННЫХ ТЕСТОВ")
    print("="*60)
    
    # 1. Проверка сервера
    try:
        r = requests.get(f"{BASE_URL}/movies/", timeout=2)
        print_result("Сервер доступен", r.status_code, 200)
    except:
        print("Сервер не отвечает!")
        return
    
    # 2. Регистрация
    user_data = {
        'username': f'test_{int(time.time())}',
        'password': 'Test123!',
        'password2': 'Test123!',
        'email': f'test_{int(time.time())}@test.com'
    }
    r = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    print_result("Регистрация", r.status_code, 201)
    
    # 3. Логин
    r = requests.post(f"{BASE_URL}/auth/login/", json={
        'username': user_data['username'],
        'password': user_data['password']
    })
    print_result("Логин", r.status_code, 200)
    token = r.json().get('access') if r.status_code == 200 else None
    
    # 4. Профиль
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        r = requests.get(f"{BASE_URL}/auth/me/", headers=headers)
        print_result("Профиль", r.status_code, 200)
    
    # 5. Админ логин
    r = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
    print_result("Админ логин", r.status_code, 200)
    admin_token = r.json().get('access') if r.status_code == 200 else None
    
    # 6. Создание фильма (админ)
    if admin_token:
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        movie_data = {
            'title': f'Фильм {int(time.time())}',
            'duration': 120
        }
        r = requests.post(f"{BASE_URL}/movies/", json=movie_data, headers=admin_headers)
        print_result("Создание фильма", r.status_code, 201)
    
    # 7. Создание зала (админ)
    if admin_token:
        hall_data = {
            'name': f'Зал {int(time.time())}',
            'rows': 5,
            'seats_per_row': 8
        }
        r = requests.post(f"{BASE_URL}/cinemas/halls/", json=hall_data, headers=admin_headers)
        print_result("Создание зала", r.status_code, 201)
    
    print("\n" + "="*60)
    print("ТЕСТЫ ЗАВЕРШЕНЫ")

if __name__ == "__main__":
    run_simple_tests()