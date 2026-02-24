# tests/debug_api.py
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

def debug_api():
    print("ДИАГНОСТИКА API ОТВЕТОВ")
    print("="*60)
    
    # Логинимся как админ
    login_resp = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
    if login_resp.status_code != 200:
        print("Не удалось войти как админ")
        return
    
    token = login_resp.json().get('access')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Создаем фильм и смотрим ответ
    print("\n1. СОЗДАНИЕ ФИЛЬМА:")
    movie_data = {
        'title': 'Диагностический фильм',
        'description': 'Тестовое описание',
        'duration': 120,
        'release_date': '2024-01-01',
        'director': 'Тестовый режиссер'
    }
    movie_resp = requests.post(f"{BASE_URL}/movies/", json=movie_data, headers=headers)
    print(f"Статус: {movie_resp.status_code}")
    print(f"Ответ: {json.dumps(movie_resp.json(), indent=2, ensure_ascii=False)}")
    
    # 2. Создаем зал и смотрим ответ
    print("\n2. СОЗДАНИЕ ЗАЛА:")
    hall_data = {
        'name': 'Диагностический зал',
        'rows': 5,
        'seats_per_row': 8,
        'description': 'Тестовый зал'
    }
    hall_resp = requests.post(f"{BASE_URL}/cinemas/halls/", json=hall_data, headers=headers)
    print(f"Статус: {hall_resp.status_code}")
    print(f"Ответ: {json.dumps(hall_resp.json(), indent=2, ensure_ascii=False)}")
    
    # 3. Если есть ID фильма и зала, создаем сеанс
    print("\n3. СОЗДАНИЕ СЕАНСА:")
    movie_id = movie_resp.json().get('id') if movie_resp.status_code == 201 else None
    hall_id = hall_resp.json().get('id') if hall_resp.status_code == 201 else None
    
    if movie_id and hall_id:
        from datetime import datetime, timedelta
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
        screening_resp = requests.post(f"{BASE_URL}/screenings/", json=screening_data, headers=headers)
        print(f"Статус: {screening_resp.status_code}")
        print(f"Ответ: {json.dumps(screening_resp.json(), indent=2, ensure_ascii=False)}")
    else:
        print("Нет movie_id или hall_id для создания сеанса")

if __name__ == "__main__":
    debug_api()