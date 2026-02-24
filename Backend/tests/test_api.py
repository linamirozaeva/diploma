# test_api.py
import requests
import json
import time
import sys
import io

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'http://127.0.0.1:8000/api'
TEST_USER = {
    "username": f"testuser_{int(time.time())}",
    "password": "testpass123",
    "password2": "testpass123",
    "email": f"test_{int(time.time())}@example.com",
    "first_name": "Тест",
    "last_name": "Пользователь"
}

def print_response(response, test_name):
    """Красивый вывод ответа"""
    print(f"\n{'='*60}")
    print(f"ТЕСТ: {test_name}")
    print(f"URL: {response.url}")
    print(f"СТАТУС: {response.status_code}")
    print(f"{'='*60}")
    
    try:
        if response.text:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("(пустой ответ)")
    except:
        print("Ответ не в JSON формате:")
        print(response.text[:500])
    
    print(f"{'='*60}\n")
    return response

# Тест 1: Регистрация
def test_register():
    url = f"{BASE_URL}/auth/register/"
    response = requests.post(url, json=TEST_USER)
    return print_response(response, "1. Регистрация пользователя")

# Тест 2: Авторизация
def test_login():
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    response = requests.post(url, json=data)
    return print_response(response, "2. Авторизация")

# Тест 3: Профиль
def test_user_profile(token):
    url = f"{BASE_URL}/auth/me/"
    headers = {'Authorization': f'Bearer {token}'}
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

def run_all_tests():
    print("ЗАПУСК ТЕСТИРОВАНИЯ API")
    print("="*60)
    
    # 1. Регистрация
    test_register()
    
    # 2. Авторизация
    login_response = test_login()
    
    if login_response.status_code == 200:
        token = login_response.json().get('access')
        
        # 3. Профиль
        test_user_profile(token)
    
    # 4. Фильмы
    test_movies()
    
    # 5. Кинозалы
    test_cinemas()
    
    # 6. Сеансы
    test_screenings()
    
    print("\nТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

if __name__ == "__main__":
    run_all_tests()