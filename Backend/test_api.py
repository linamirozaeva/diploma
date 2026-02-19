# test_api.py
import requests
import json
from pprint import pprint
import time
# test_api.py
import sys
import io

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'http://127.0.0.1:8000/api'
headers = {}

def print_response(response, test_name):
    """Красивый вывод ответа"""
    print(f"\n{'='*60}")
    print(f"ТЕСТ: {test_name}")
    print(f"URL: {response.url}")
    print(f"STATUS: {response.status_code}")
    print(f"{'='*60}")
    
    try:
        if response.text:
            data = response.json()
            pprint(data)
        else:
            print("(пустой ответ)")
    except:
        print("Ответ не в JSON формате:")
        print(response.text[:500])
    
    print(f"{'='*60}\n")
    return response

def save_token(token):
    """Сохранить токен для следующих запросов"""
    global headers
    headers = {'Authorization': f'Bearer {token}'}
    print(f"Токен сохранен")

# Тест 1: Регистрация
def test_register():
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": f"testuser_{int(time.time())}",
        "password": "testpass123",
        "password2": "testpass123",
        "email": f"test_{int(time.time())}@example.com",
        "first_name": "Тест",
        "last_name": "Пользователь"
    }
    response = requests.post(url, json=data)
    return print_response(response, "1. Регистрация пользователя")

# Тест 2: Авторизация
def test_login(username="testuser"):
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": username,
        "password": "testpass123"
    }
    response = requests.post(url, json=data)
    result = print_response(response, "2. Авторизация")
    
    if response.status_code == 200:
        token = response.json().get('access')
        if token:
            save_token(token)
    return response

# Тест 3: Профиль
def test_user_profile():
    url = f"{BASE_URL}/auth/me/"
    response = requests.get(url, headers=headers)
    return print_response(response, "3. Профиль пользователя")

# Тест 4: Фильмы
def test_movies():
    url = f"{BASE_URL}/movies/"
    response = requests.get(url)
    return print_response(response, "4. Список фильмов")

# Тест 5: Кинозалы
def test_cinemas():
    url = f"{BASE_URL}/cinemas/halls/"
    response = requests.get(url)
    return print_response(response, "5. Список кинозалов")

# Тест 6: Сеансы
def test_screenings():
    url = f"{BASE_URL}/screenings/"
    response = requests.get(url)
    return print_response(response, "6. Список сеансов")

# Тест 7: Проверка мест
def test_check_seats():
    url = f"{BASE_URL}/screenings/1/check_seats/"
    data = {"seat_ids": [1, 2, 3]}
    response = requests.post(url, json=data)
    return print_response(response, "7. Проверка мест")

# Тест 8: Создание бронирования
def test_create_booking():
    url = f"{BASE_URL}/bookings/"
    data = {
        "screening": 1,
        "seat_ids": [4, 5]
    }
    response = requests.post(url, json=data, headers=headers)
    return print_response(response, "8. Создание бронирования")

# Тест 9: Мои бронирования
def test_my_bookings():
    url = f"{BASE_URL}/bookings/my_bookings/"
    response = requests.get(url, headers=headers)
    return print_response(response, "9. Мои бронирования")

# Запуск всех тестов
def run_all_tests():
    print("НАЧИНАЕМ ТЕСТИРОВАНИЕ API")
    print("="*60)
    
    # 1. Регистрация
    reg_response = test_register()
    if reg_response.status_code != 201:
        print("Регистрация не удалась, пробуем войти существующим пользователем")
        test_login("testuser")
    else:
        # 2. Авторизация новым пользователем
        username = reg_response.json().get('username')
        test_login(username)
    
    time.sleep(1)
    
    # 3. Профиль
    test_user_profile()
    
    # 4. Фильмы
    test_movies()
    
    # 5. Кинозалы
    test_cinemas()
    
    # 6. Сеансы
    test_screenings()
    
    # 7. Проверка мест
    test_check_seats()
    
    # 8. Создание бронирования
    booking_response = test_create_booking()
    
    time.sleep(1)
    
    # 9. Мои бронирования
    test_my_bookings()
    
    print("\nТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

if __name__ == "__main__":
    run_all_tests()