# test_complete.py
import requests
import json
import base64
import time
from PIL import Image
from io import BytesIO

BASE_URL = 'http://127.0.0.1:8000/api'
TEST_USER = {
    "username": f"testuser_{int(time.time())}",
    "password": "TestPass123!",
    "password2": "TestPass123!",
    "email": f"test_{int(time.time())}@example.com",
    "first_name": "Тест",
    "last_name": "Пользователь"
}
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def print_result(test_name, status_code, expected, data=None):
    """Вывод результата теста"""
    icon = "yes" if status_code == expected else "no"
    print(f"{icon} {test_name}: {status_code} (ожидалось {expected})")
    if data and status_code != expected:
        print(f"   Ответ: {data}")

def test_authentication():
    """Тестирование аутентификации"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ АУТЕНТИФИКАЦИИ")
    print("="*60)
    
    # 1. Регистрация нового пользователя
    response = requests.post(f"{BASE_URL}/auth/register/", json=TEST_USER)
    print_result("Регистрация", response.status_code, 201)
    
    # 2. Логин с правильным паролем
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print_result("Логин (правильный пароль)", response.status_code, 200)
    
    token = None
    if response.status_code == 200:
        token = response.json().get('access')
        print(f"   Токен получен")
    
    # 3. Логин с неправильным паролем
    wrong_login = {
        "username": TEST_USER["username"],
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=wrong_login)
    print_result("Логин (неправильный пароль)", response.status_code, 401)
    
    # 4. Регистрация с существующим username
    response = requests.post(f"{BASE_URL}/auth/register/", json=TEST_USER)
    print_result("Регистрация (дубликат)", response.status_code, 400)
    
    # 5. Доступ к защищенному эндпоинту с токеном
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{BASE_URL}/auth/me/", headers=headers)
        print_result("Профиль с токеном", response.status_code, 200)
    
    # 6. Доступ к защищенному эндпоинту без токена
    response = requests.get(f"{BASE_URL}/auth/me/")
    print_result("Профиль без токена", response.status_code, 401)
    
    return token

def test_movies(token):
    """Тестирование фильмов"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ФИЛЬМОВ")
    print("="*60)
    
    # 1. GET /movies/ (публичный)
    response = requests.get(f"{BASE_URL}/movies/")
    print_result("GET /movies/", response.status_code, 200)

def test_cinemas(token):
    """Тестирование кинозалов"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ КИНОЗАЛОВ")
    print("="*60)
    
    # 1. GET /cinemas/halls/ (публичный)
    response = requests.get(f"{BASE_URL}/cinemas/halls/")
    print_result("GET /cinemas/halls/", response.status_code, 200)

def test_screenings(token):
    """Тестирование сеансов"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ СЕАНСОВ")
    print("="*60)
    
    # 1. GET /screenings/ (публичный)
    response = requests.get(f"{BASE_URL}/screenings/")
    print_result("GET /screenings/", response.status_code, 200)

def run_all_tests():
    """Запуск всех тестов"""
    print("ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ API")
    print("="*60)
    
    token = test_authentication()
    test_movies(token)
    test_cinemas(token)
    test_screenings(token)
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()