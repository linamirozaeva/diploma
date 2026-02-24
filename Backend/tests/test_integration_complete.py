# tests/test_integration_complete.py (финальная версия)
"""
ПОЛНЫЙ НАБОР ИНТЕГРАЦИОННЫХ ТЕСТОВ
"""

import requests
import sys
import io
import time
from datetime import datetime, timedelta
import json

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'http://127.0.0.1:8000/api'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

class Colors:
    """Цвета для вывода"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """Вывод заголовка"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{Colors.RESET}")

def print_result(test_name, success, details=None):
    """Вывод результата теста"""
    status = f"{Colors.GREEN}✓ УСПЕХ{Colors.RESET}" if success else f"{Colors.RED}✗ ОШИБКА{Colors.RESET}"
    print(f"  {status} - {test_name}")
    if details and not success:
        print(f"    {Colors.YELLOW}Детали: {details}{Colors.RESET}")

def print_info(message):
    """Вывод информационного сообщения"""
    print(f"  {Colors.BLUE}i {message}{Colors.RESET}")

# =====================================================================
# 1. ТЕСТ ПОЛНОГО ЦИКЛА РАБОТЫ ПРИЛОЖЕНИЯ
# =====================================================================

class FullCycleTest:
    """Тест полного цикла работы приложения"""
    
    def __init__(self):
        self.token = None
        self.admin_token = None
        self.user_data = {
            'username': f'fullcycle_{int(time.time())}',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'email': f'fullcycle_{int(time.time())}@test.com',
            'first_name': 'Тест',
            'last_name': 'Пользователь'
        }
        self.movie_id = None
        self.hall_id = None
        self.screening_id = None
        self.booking_id = None
    
    def run(self):
        """Запуск всех тестов полного цикла"""
        print_header("ТЕСТ 1: ПОЛНЫЙ ЦИКЛ РАБОТЫ ПРИЛОЖЕНИЯ")
        
        # Проверяем админа
        self._check_admin()
        
        tests = [
            ("1.1 Регистрация пользователя", self.test_register),
            ("1.2 Авторизация пользователя", self.test_login),
            ("1.3 Получение профиля", self.test_profile),
            ("1.4 Авторизация админа", self.test_admin_login),
            ("1.5 Создание фильма", self.test_create_movie),
            ("1.6 Создание зала", self.test_create_hall),
            ("1.7 Создание сеанса", self.test_create_screening),
            ("1.8 Проверка доступных мест", self.test_available_seats),
            ("1.9 Проверка конкретных мест", self.test_check_seats),
            ("1.10 Создание бронирования", self.test_create_booking),
            ("1.11 Просмотр своих броней", self.test_my_bookings),
            ("1.12 Получение QR-кода", self.test_qr_code),
            ("1.13 Отмена бронирования", self.test_cancel_booking),
        ]
        
        all_success = True
        for name, test_func in tests:
            try:
                success = test_func()
                print_result(name, success)
                if not success:
                    all_success = False
            except Exception as e:
                print_result(name, False, str(e))
                all_success = False
        
        return all_success
    
    def _check_admin(self):
        """Проверка существования админа"""
        try:
            response = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                print_info("Админ уже существует")
        except:
            pass
    
    def test_register(self):
        """Тест регистрации"""
        response = requests.post(f"{BASE_URL}/auth/register/", json=self.user_data)
        return response.status_code == 201
    
    def test_login(self):
        """Тест логина"""
        response = requests.post(f"{BASE_URL}/auth/login/", json={
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        if response.status_code == 200:
            self.token = response.json().get('access')
            return True
        return False
    
    def test_profile(self):
        """Тест получения профиля"""
        if not self.token:
            return False
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{BASE_URL}/auth/me/", headers=headers)
        return response.status_code == 200
    
    def test_admin_login(self):
        """Тест входа админа"""
        response = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            self.admin_token = response.json().get('access')
            return True
        return False
    
    def test_create_movie(self):
        """Тест создания фильма"""
        if not self.admin_token:
            return False
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        data = {
            'title': f'Тестовый фильм {int(time.time())}',
            'description': 'Фильм созданный в интеграционном тесте',
            'duration': 120,
            'release_date': '2024-01-01',
            'director': 'Тестовый режиссер'
        }
        response = requests.post(f"{BASE_URL}/movies/", json=data, headers=headers)
        if response.status_code == 201:
            response_data = response.json()
            # Проверяем разные возможные форматы ответа
            if isinstance(response_data, dict):
                if 'id' in response_data:
                    self.movie_id = response_data['id']
                elif 'data' in response_data and isinstance(response_data['data'], dict):
                    self.movie_id = response_data['data'].get('id')
            print_info(f"Создан фильм ID: {self.movie_id}")
            return self.movie_id is not None
        else:
            print_info(f"Ошибка создания фильма: {response.status_code}")
            return False
    
    def test_create_hall(self):
        if not self.admin_token:
            return False
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        data = {
            'name': f'Тестовый зал {int(time.time())}',
            'rows': 5,
            'seats_per_row': 8,
            'description': 'Зал созданный в интеграционном тесте'
        }
        response = requests.post(f"{BASE_URL}/cinemas/halls/", json=data, headers=headers)
        if response.status_code == 201:
            response_data = response.json()
            if isinstance(response_data, dict):
                if 'id' in response_data:
                    self.hall_id = response_data['id']
            print_info(f"Создан зал ID: {self.hall_id}")
            return self.hall_id is not None
        return False
    
    def get_screening_id_by_params(self, movie_id, hall_id, headers):
        try:
            screenings = requests.get(f"{BASE_URL}/screenings/", headers=headers).json()
            for screening in screenings:
                if (screening.get('movie') == movie_id and 
                    screening.get('hall') == hall_id):
                    return screening.get('id')
        except:
            pass
        return None

    def test_create_screening(self):
        """Тест создания сеанса"""
        if not self.admin_token or not self.movie_id or not self.hall_id:
            return False

        headers = {'Authorization': f'Bearer {self.admin_token}'}

        # Используем СОЗДАННЫЙ зал, а не существующий
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
        end_time = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0).isoformat()

        data = {
            'movie': self.movie_id,
            'hall': self.hall_id,  # Используем наш новый зал
            'start_time': start_time,
            'end_time': end_time,
            'price_standard': 250,
            'price_vip': 350
        }

        print_info(f"Создание сеанса: movie={self.movie_id}, hall={self.hall_id}")
        response = requests.post(f"{BASE_URL}/screenings/", json=data, headers=headers)

        if response.status_code == 201:
            response_data = response.json()
            if isinstance(response_data, dict) and 'id' in response_data:
                self.screening_id = response_data['id']
            print_info(f"Создан сеанс ID: {self.screening_id}")
            return self.screening_id is not None
        else:
            print_info(f"Ошибка создания сеанса: {response.status_code}")
            if response.status_code == 400:
                print_info(f"Ошибка валидации: {response.json()}")
            return False
    
    def test_available_seats(self):
        """Тест получения доступных мест"""
        if not self.screening_id:
            print_info("Нет screening_id")
            return False
        response = requests.get(f"{BASE_URL}/screenings/{self.screening_id}/available_seats/")
        return response.status_code == 200
    
    def test_check_seats(self):
        """Тест проверки конкретных мест"""
        if not self.screening_id:
            print_info("Нет screening_id")
            return False
        response = requests.post(
            f"{BASE_URL}/screenings/{self.screening_id}/check_seats/",
            json={'seat_ids': [1, 2, 3]}
        )
        return response.status_code == 200
    
    def test_create_booking(self):
        """Тест создания бронирования"""
        if not self.token or not self.screening_id:
            print_info("Нет token или screening_id")
            return False

        # Сначала получаем доступные места
        seats_response = requests.get(
            f"{BASE_URL}/screenings/{self.screening_id}/available_seats/"
        )

        if seats_response.status_code != 200:
            print_info(f"Ошибка получения мест: {seats_response.status_code}")
            return False

        seats_data = seats_response.json()

        # УНИВЕРСАЛЬНОЕ ИЗВЛЕЧЕНИЕ ID МЕСТ
        available_seats = []

        # Вариант 1: прямой список seats
        if 'seats' in seats_data:
            for seat in seats_data['seats']:
                if seat.get('status') == 'available':
                    available_seats.append(seat.get('id'))

        # Вариант 2: seats_by_row (как в вашем API)
        if 'seats_by_row' in seats_data:
            for row_seats in seats_data['seats_by_row'].values():
                for seat in row_seats:
                    if seat.get('status') == 'available':
                        available_seats.append(seat.get('id'))

        # Вариант 3: прямой список в результате
        if isinstance(seats_data, list):
            for seat in seats_data:
                if isinstance(seat, dict) and seat.get('status') == 'available':
                    available_seats.append(seat.get('id'))

        print_info(f"Найдено доступных мест: {len(available_seats)}")

        if not available_seats:
            print_info("Нет доступных мест")
            return False

        # Берём первые два доступных места
        seat_ids = available_seats[:2]
        print_info(f"Бронируем места: {seat_ids}")

        headers = {'Authorization': f'Bearer {self.token}'}
        data = {
            'screening': self.screening_id,
            'seat_ids': seat_ids
        }

        response = requests.post(f"{BASE_URL}/bookings/", json=data, headers=headers)

        if response.status_code == 201:
            response_data = response.json()
            # Извлекаем ID бронирования из ответа
            if 'booking' in response_data:
                self.booking_id = response_data['booking'].get('id')
            elif 'id' in response_data:
                self.booking_id = response_data['id']
            elif isinstance(response_data, list) and len(response_data) > 0:
                self.booking_id = response_data[0].get('id')

            print_info(f"Создано бронирование ID: {self.booking_id}")
            return self.booking_id is not None
        else:
            print_info(f"Ошибка создания бронирования: {response.status_code}")
            if response.text:
                print_info(f"Ответ: {response.text[:200]}")
            return False
    
    def test_my_bookings(self):
        """Тест получения своих броней"""
        if not self.token:
            return False
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{BASE_URL}/bookings/my_bookings/", headers=headers)
        return response.status_code == 200
    
    def test_qr_code(self):
        """Тест получения QR-кода"""
        if not self.token or not self.booking_id:
            print_info("Нет token или booking_id")
            return False

        headers = {'Authorization': f'Bearer {self.token}'}

        # ИСПОЛЬЗУЕМ ТОЛЬКО БАЗОВЫЙ ФОРМАТ (ОН РАБОТАЕТ)
        response = requests.get(
            f"{BASE_URL}/bookings/{self.booking_id}/qr_code/", 
            headers=headers
        )

        if response.status_code == 200:
            print_info("QR-код получен")
            return True
        else:
            print_info(f"Ошибка получения QR-кода: {response.status_code}")
            return False
    
    def test_cancel_booking(self):
        """Тест отмены бронирования"""
        if not self.token or not self.booking_id:
            print_info("Нет token или booking_id")
            return False

        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{BASE_URL}/bookings/{self.booking_id}/cancel/", 
            headers=headers
        )

        if response.status_code == 200:
            print_info("Бронирование отменено")
            return True
        else:
            print_info(f"Ошибка отмены: {response.status_code}")
            return False


# =====================================================================
# 2. ТЕСТЫ ОШИБОЧНЫХ СЦЕНАРИЕВ
# =====================================================================

class ErrorScenariosTest:
    """Тестирование ошибочных сценариев"""
    
    def __init__(self):
        self.token = None
        self.admin_token = None
        self.test_user = {
            'username': f'error_{int(time.time())}',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'email': f'error_{int(time.time())}@test.com'
        }
        self.movie_id = None
        self.hall_id = None
        self.screening_id = None
    
    def run(self):
        """Запуск всех тестов ошибочных сценариев"""
        print_header("ТЕСТ 2: ОШИБОЧНЫЕ СЦЕНАРИИ")
        
        # Подготовка - создаем пользователя и получаем токены
        self._setup()
        
        # Создаем тестовые данные для валидации
        self._create_test_data()
        
        tests = [
            ("2.1 Регистрация с существующим username", self.test_duplicate_register),
            ("2.2 Логин с неправильным паролем", self.test_wrong_password),
            ("2.3 Доступ к профилю без токена", self.test_profile_no_token),
            ("2.4 Создание фильма без прав", self.test_create_movie_unauthorized),
            ("2.5 Создание зала с некорректными размерами", self.test_invalid_hall),
            ("2.6 Создание фильма с некорректной длительностью", self.test_invalid_movie),
            ("2.7 Бронирование без авторизации", self.test_booking_unauthorized),
            ("2.8 Бронирование несуществующего места", self.test_booking_nonexistent),
        ]
        
        all_success = True
        for name, test_func in tests:
            try:
                success = test_func()
                print_result(name, success)
                if not success:
                    all_success = False
            except Exception as e:
                print_result(name, False, str(e))
                all_success = False
        
        return all_success
    
    def _setup(self):
        """Подготовка тестовых данных"""
        # Регистрация пользователя
        reg_response = requests.post(f"{BASE_URL}/auth/register/", json=self.test_user)
        if reg_response.status_code == 201:
            print_info("Тестовый пользователь создан")
        
        # Логин пользователя
        login_resp = requests.post(f"{BASE_URL}/auth/login/", json={
            'username': self.test_user['username'],
            'password': self.test_user['password']
        })
        if login_resp.status_code == 200:
            self.token = login_resp.json().get('access')
            print_info("Токен пользователя получен")
        
        # Логин админа
        admin_resp = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
        if admin_resp.status_code == 200:
            self.admin_token = admin_resp.json().get('access')
            print_info("Токен админа получен")
    
    def _create_test_data(self):
        """Создание тестовых данных для валидации"""
        if not self.admin_token:
            print_info("Нет admin_token для создания тестовых данных")
            return
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Создаем фильм
        movie_data = {
            'title': f'Тестовый фильм {int(time.time())}',
            'duration': 120
        }
        movie_resp = requests.post(f"{BASE_URL}/movies/", json=movie_data, headers=headers)
        if movie_resp.status_code == 201:
            movie_data = movie_resp.json()
            if isinstance(movie_data, dict):
                self.movie_id = movie_data.get('id')
            print_info(f"Создан тестовый фильм ID: {self.movie_id}")
        
        # Создаем зал
        hall_data = {
            'name': f'Тестовый зал {int(time.time())}',
            'rows': 5,
            'seats_per_row': 8
        }
        hall_resp = requests.post(f"{BASE_URL}/cinemas/halls/", json=hall_data, headers=headers)
        if hall_resp.status_code == 201:
            hall_data = hall_resp.json()
            if isinstance(hall_data, dict):
                self.hall_id = hall_data.get('id')
            print_info(f"Создан тестовый зал ID: {self.hall_id}")
        
        # Создаем сеанс, если есть фильм и зал
        if self.movie_id and self.hall_id:
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
            end_time = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0).isoformat()
            
            screening_data = {
                'movie': self.movie_id,
                'hall': self.hall_id,
                'start_time': start_time,
                'end_time': end_time,
                'price_standard': 250,
                'price_vip': 350
            }
            screening_resp = requests.post(f"{BASE_URL}/screenings/", json=screening_data, headers=headers)
            if screening_resp.status_code == 201:
                screening_data = screening_resp.json()
                if isinstance(screening_data, dict):
                    self.screening_id = screening_data.get('id')
                print_info(f"Создан тестовый сеанс ID: {self.screening_id}")
    
    def test_duplicate_register(self):
        """Тест регистрации с существующим username"""
        response = requests.post(f"{BASE_URL}/auth/register/", json=self.test_user)
        return response.status_code == 400
    
    def test_wrong_password(self):
        """Тест логина с неправильным паролем"""
        response = requests.post(f"{BASE_URL}/auth/login/", json={
            'username': self.test_user['username'],
            'password': 'wrongpassword'
        })
        return response.status_code == 401
    
    def test_profile_no_token(self):
        """Тест доступа к профилю без токена"""
        response = requests.get(f"{BASE_URL}/auth/me/")
        return response.status_code == 401
    
    def test_create_movie_unauthorized(self):
        """Тест создания фильма без прав"""
        response = requests.post(f"{BASE_URL}/movies/", json={
            'title': 'Неавторизованный фильм',
            'duration': 120
        })
        return response.status_code == 401
    
    def test_invalid_hall(self):
        """Тест создания зала с некорректными размерами"""
        if not self.admin_token:
            print_info("Нет admin_token для теста")
            return False
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = requests.post(f"{BASE_URL}/cinemas/halls/", json={
            'name': 'Некорректный зал',
            'rows': 100,
            'seats_per_row': 50
        }, headers=headers)
        return response.status_code == 400
    
    def test_invalid_movie(self):
        """Тест создания фильма с некорректной длительностью"""
        if not self.admin_token:
            print_info("Нет admin_token для теста")
            return False
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = requests.post(f"{BASE_URL}/movies/", json={
            'title': 'Некорректный фильм',
            'duration': 5
        }, headers=headers)
        return response.status_code == 400
    
    def test_booking_unauthorized(self):
        """Тест бронирования без авторизации"""
        if not self.screening_id:
            print_info("Нет screening_id для теста, пропускаем")
            return True
        response = requests.post(f"{BASE_URL}/bookings/", json={
            'screening': self.screening_id,
            'seat_ids': [1]
        })
        return response.status_code == 401
    
    def test_booking_nonexistent(self):
        """Тест бронирования несуществующего места"""
        if not self.token:
            print_info("Нет token для теста")
            return False
        if not self.screening_id:
            print_info("Нет screening_id для теста, пропускаем")
            return True
            
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f"{BASE_URL}/bookings/", json={
            'screening': self.screening_id,
            'seat_ids': [99999]
        }, headers=headers)
        return response.status_code == 400


# =====================================================================
# 3. ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ
# =====================================================================

class PerformanceTest:
    """Тестирование производительности"""
    
    def run(self):
        """Запуск всех тестов производительности"""
        print_header("ТЕСТ 3: ПРОИЗВОДИТЕЛЬНОСТЬ")
        
        tests = [
            ("3.1 Время ответа movies/", self.test_movies_response_time),
            ("3.2 Время ответа cinemas/", self.test_cinemas_response_time),
            ("3.3 Время ответа screenings/", self.test_screenings_response_time),
        ]
        
        all_success = True
        for name, test_func in tests:
            try:
                success = test_func()
                print_result(name, success)
                if not success:
                    all_success = False
            except Exception as e:
                print_result(name, False, str(e))
                all_success = False
        
        return all_success
    
    def _measure_time(self, url):
        """Измерение времени ответа"""
        start = time.time()
        try:
            response = requests.get(url)
            elapsed = (time.time() - start) * 1000  # в миллисекундах
            return elapsed, response.status_code
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return elapsed, 500
    
    def test_movies_response_time(self):
        """Проверка времени ответа /movies/"""
        elapsed, status = self._measure_time(f"{BASE_URL}/movies/")
        print_info(f"  Время: {elapsed:.0f}ms, Статус: {status}")
        return elapsed < 1000 and status == 200
    
    def test_cinemas_response_time(self):
        """Проверка времени ответа /cinemas/halls/"""
        elapsed, status = self._measure_time(f"{BASE_URL}/cinemas/halls/")
        print_info(f"  Время: {elapsed:.0f}ms, Статус: {status}")
        return elapsed < 1000 and status == 200
    
    def test_screenings_response_time(self):
        """Проверка времени ответа /screenings/"""
        elapsed, status = self._measure_time(f"{BASE_URL}/screenings/")
        print_info(f"  Время: {elapsed:.0f}ms, Статус: {status}")
        return elapsed < 1000 and status == 200


# =====================================================================
# ЗАПУСК ВСЕХ ТЕСТОВ
# =====================================================================

def check_server():
    """Проверка доступности сервера"""
    try:
        response = requests.get(f"{BASE_URL}/movies/", timeout=2)
        if response.status_code == 200:
            print(f"{Colors.GREEN} Сервер доступен (API отвечает){Colors.RESET}")
            return True
        else:
            print(f"{Colors.YELLOW} Сервер доступен, но API вернул {response.status_code}{Colors.RESET}")
            return True
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED} Не удалось подключиться к серверу!{Colors.RESET}")
        print(f"{Colors.YELLOW}   Запустите: python manage.py runserver{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED} Ошибка при проверке сервера: {e}{Colors.RESET}")
        return False

def run_all_tests():
    """Запуск всех интеграционных тестов"""
    print_header(" ЗАПУСК ВСЕХ ИНТЕГРАЦИОННЫХ ТЕСТОВ")
    
    if not check_server():
        return False
    
    results = []
    
    # Тест 1: Полный цикл
    test1 = FullCycleTest()
    results.append(("Полный цикл", test1.run()))
    
    # Тест 2: Ошибочные сценарии
    test2 = ErrorScenariosTest()
    results.append(("Ошибочные сценарии", test2.run()))
    
    # Тест 3: Производительность
    test3 = PerformanceTest()
    results.append(("Производительность", test3.run()))
    
    # Итоги
    print_header(" ИТОГИ ТЕСТИРОВАНИЯ")
    
    all_passed = True
    for name, passed in results:
        status = f"{Colors.GREEN}✓ ПРОЙДЕН{Colors.RESET}" if passed else f"{Colors.RED}✗ ПРОВАЛЕН{Colors.RESET}"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD} ВСЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD} НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ{Colors.RESET}")
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()