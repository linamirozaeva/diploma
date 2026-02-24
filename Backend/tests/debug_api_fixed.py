# tests/debug_api_fixed.py
import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000/api'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

def print_json(data):
    """Красивый вывод JSON"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def debug_api_fixed():
    print("РАСШИРЕННАЯ ДИАГНОСТИКА API")
    print("="*70)
    
    # Логинимся как админ
    login_resp = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
    if login_resp.status_code != 200:
        print("Не удалось войти как админ")
        return
    
    token = login_resp.json().get('access')
    headers = {'Authorization': f'Bearer {token}'}
    print("Успешный вход как админ")
    
    # 1. СОЗДАНИЕ ФИЛЬМА
    print("\n" + "="*70)
    print("1. СОЗДАНИЕ ФИЛЬМА")
    print("="*70)
    
    movie_data = {
        'title': f'Диагностический фильм {int(time.time())}',
        'description': 'Тестовое описание',
        'duration': 120,
        'release_date': '2024-01-01',
        'director': 'Тестовый режиссер'
    }
    
    print(f"Отправка: {movie_data}")
    movie_resp = requests.post(f"{BASE_URL}/movies/", json=movie_data, headers=headers)
    print(f"Статус: {movie_resp.status_code}")
    print(f"Ответ при создании:")
    print_json(movie_resp.json())
    
    # Получаем список всех фильмов, чтобы найти ID
    print("\nСписок всех фильмов:")
    movies_list = requests.get(f"{BASE_URL}/movies/", headers=headers)
    if movies_list.status_code == 200:
        movies = movies_list.json()
        print_json(movies)
        
        # Находим наш фильм по названию
        movie_title = movie_data['title']
        found_movie = None
        for movie in movies:
            if movie.get('title') == movie_title:
                found_movie = movie
                break
        
        if found_movie:
            print(f"\nНайден созданный фильм с ID: {found_movie.get('id')}")
            print_json(found_movie)
        else:
            print("\nФильм не найден в списке!")
    
    # 2. СОЗДАНИЕ ЗАЛА
    print("\n" + "="*70)
    print("2. СОЗДАНИЕ ЗАЛА")
    print("="*70)
    
    hall_data = {
        'name': f'Диагностический зал {int(time.time())}',
        'rows': 5,
        'seats_per_row': 8,
        'description': 'Тестовый зал'
    }
    
    print(f"Отправка: {hall_data}")
    hall_resp = requests.post(f"{BASE_URL}/cinemas/halls/", json=hall_data, headers=headers)
    print(f"Статус: {hall_resp.status_code}")
    print(f"Ответ при создании:")
    print_json(hall_resp.json())
    
    # Получаем список всех залов, чтобы найти ID
    print("\nСписок всех залов:")
    halls_list = requests.get(f"{BASE_URL}/cinemas/halls/", headers=headers)
    if halls_list.status_code == 200:
        halls = halls_list.json()
        print_json(halls)
        
        # Находим наш зал по названию
        hall_name = hall_data['name']
        found_hall = None
        for hall in halls:
            if hall.get('name') == hall_name:
                found_hall = hall
                break
        
        if found_hall:
            print(f"\nНайден созданный зал с ID: {found_hall.get('id')}")
            print_json(found_hall)
        else:
            print("\nЗал не найден в списке!")

if __name__ == "__main__":
    debug_api_fixed()