# test_admin.py
import sys
import io

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Проверка наличия необходимых библиотек
try:
    import requests
except ImportError:
    print("Библиотека 'requests' не установлена")
    print("   Установите: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Библиотека 'beautifulsoup4' не установлена")
    print("   Установите: pip install beautifulsoup4")
    sys.exit(1)

BASE_URL = 'http://127.0.0.1:8000'
ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'admin123'

def print_result(test_name, success, message=""):
    """Вывод результата теста"""
    status = "yes" if success else "no"
    print(f"{status} {test_name}")
    if message and not success:
        print(f"   {message}")

def test_admin_login():
    """Тест входа в админ-панель"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ВХОДА В АДМИН-ПАНЕЛЬ")
    print("="*60)
    
    session = requests.Session()
    
    try:
        # 1. Получаем страницу логина и CSRF токен
        login_page = session.get(f"{BASE_URL}/admin/login/")
        
        if login_page.status_code != 200:
            print_result("Доступ к странице логина", False, f"Статус: {login_page.status_code}")
            return None
            
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_token:
            print_result("Получение CSRF токена", False, "CSRF токен не найден")
            return None
        
        csrf_token = csrf_token['value']
        
        # 2. Отправляем данные для входа
        login_data = {
            'username': ADMIN_LOGIN,
            'password': ADMIN_PASSWORD,
            'csrfmiddlewaretoken': csrf_token,
            'next': '/admin/'
        }
        
        headers = {
            'Referer': f"{BASE_URL}/admin/login/"
        }
        
        response = session.post(f"{BASE_URL}/admin/login/", data=login_data, headers=headers)
        
        if response.status_code == 200 and ('admin' in response.text.lower() or 'выйти' in response.text.lower()):
            print_result("Вход в админ-панель", True)
            return session
        else:
            print_result("Вход в админ-панель", False, "Не удалось войти. Проверьте логин/пароль")
            return None
            
    except requests.exceptions.ConnectionError:
        print_result("Подключение к серверу", False, f"Не удалось подключиться к {BASE_URL}. Убедитесь, что сервер запущен")
        return None

def test_admin_apps(session):
    """Тест доступности всех приложений в админке"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ДОСТУПНОСТИ ПРИЛОЖЕНИЙ")
    print("="*60)
    
    if not session:
        print("Нет сессии, пропускаем тесты")
        return
    
    apps = [
        ('users/user/', 'Пользователи'),
        ('cinemas/cinemahall/', 'Кинозалы'),
        ('movies/movie/', 'Фильмы'),
        ('screenings/screening/', 'Сеансы'),
        ('bookings/booking/', 'Бронирования')
    ]
    
    for app, name in apps:
        try:
            response = session.get(f"{BASE_URL}/admin/{app}")
            success = response.status_code == 200
            print_result(f"Доступ к {name}", success)
        except:
            print_result(f"Доступ к {name}", False, "Ошибка подключения")

def test_user_admin(session):
    """Тест админ-панели пользователей"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ АДМИН-ПАНЕЛИ ПОЛЬЗОВАТЕЛЕЙ")
    print("="*60)
    
    if not session:
        return
    
    try:
        # 1. Проверка списка пользователей
        response = session.get(f"{BASE_URL}/admin/users/user/")
        print_result("Список пользователей", response.status_code == 200)
        
        # 2. Проверка наличия кастомных колонок
        if response.status_code == 200:
            has_bookings = 'Бронирований' in response.text or 'bookings' in response.text.lower()
            print_result("Кастомные колонки (Бронирований)", has_bookings)
        
        # 3. Проверка фильтров
        has_filters = 'changelist-filter' in response.text
        print_result("Наличие фильтров", has_filters)
        
    except Exception as e:
        print_result("Тест пользователей", False, str(e))

def test_cinema_admin(session):
    """Тест админ-панели кинозалов"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ АДМИН-ПАНЕЛИ КИНОЗАЛОВ")
    print("="*60)
    
    if not session:
        return
    
    try:
        # 1. Проверка списка залов
        response = session.get(f"{BASE_URL}/admin/cinemas/cinemahall/")
        print_result("Список кинозалов", response.status_code == 200)
        
        # 2. Проверка наличия ссылки на места
        if response.status_code == 200:
            has_seats_link = 'Места' in response.text or 'мест' in response.text.lower()
            print_result("Ссылка на места", has_seats_link)
        
    except Exception as e:
        print_result("Тест кинозалов", False, str(e))

def test_movie_admin(session):
    """Тест админ-панели фильмов"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ АДМИН-ПАНЕЛИ ФИЛЬМОВ")
    print("="*60)
    
    if not session:
        return
    
    try:
        # 1. Проверка списка фильмов
        response = session.get(f"{BASE_URL}/admin/movies/movie/")
        print_result("Список фильмов", response.status_code == 200)
        
        # 2. Проверка наличия превью постера
        if response.status_code == 200:
            has_poster = 'Превью' in response.text or 'poster' in response.text.lower()
            print_result("Колонка с превью постера", has_poster)
        
    except Exception as e:
        print_result("Тест фильмов", False, str(e))

def test_screening_admin(session):
    """Тест админ-панели сеансов"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ АДМИН-ПАНЕЛИ СЕАНСОВ")
    print("="*60)
    
    if not session:
        return
    
    try:
        # 1. Проверка списка сеансов
        response = session.get(f"{BASE_URL}/admin/screenings/screening/")
        print_result("Список сеансов", response.status_code == 200)
        
        # 2. Проверка наличия отображения длительности
        if response.status_code == 200:
            has_duration = 'Длительность' in response.text or 'duration' in response.text.lower()
            print_result("Отображение длительности", has_duration)
        
    except Exception as e:
        print_result("Тест сеансов", False, str(e))

def test_booking_admin(session):
    """Тест админ-панели бронирований"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ АДМИН-ПАНЕЛИ БРОНИРОВАНИЙ")
    print("="*60)
    
    if not session:
        return
    
    try:
        # 1. Проверка списка бронирований
        response = session.get(f"{BASE_URL}/admin/bookings/booking/")
        print_result("Список бронирований", response.status_code == 200)
        
        # 2. Проверка цветного статуса
        if response.status_code == 200:
            has_colored_status = 'status' in response.text.lower() and ('color' in response.text.lower() or 'style' in response.text.lower())
            print_result("Цветной статус", has_colored_status)
        
    except Exception as e:
        print_result("Тест бронирований", False, str(e))

def run_admin_tests():
    """Запуск всех тестов админ-панели"""
    print("ЗАПУСК ТЕСТИРОВАНИЯ АДМИН-ПАНЕЛИ")
    print("="*60)
    print(f"Сервер: {BASE_URL}")
    print(f"Логин: {ADMIN_LOGIN}")
    print("="*60)
    
    # Проверка подключения к серверу
    try:
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print(f"Сервер не отвечает по адресу {BASE_URL}")
            print("   Убедитесь, что сервер запущен: python manage.py runserver")
            return
        else:
            print("Сервер доступен")
    except:
        print(f"Не удалось подключиться к {BASE_URL}")
        print("   Убедитесь, что сервер запущен: python manage.py runserver")
        return
    
    # Вход в админку
    session = test_admin_login()
    
    if session:
        # Тест доступности приложений
        test_admin_apps(session)
        
        # Тест пользователей
        test_user_admin(session)
        
        # Тест кинозалов
        test_cinema_admin(session)
        
        # Тест фильмов
        test_movie_admin(session)
        
        # Тест сеансов
        test_screening_admin(session)
        
        # Тест бронирований
        test_booking_admin(session)
    else:
        print("\nНе удалось войти в админ-панель, тесты прерваны")
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ АДМИН-ПАНЕЛИ ЗАВЕРШЕНО")
    print("="*60)

if __name__ == "__main__":
    run_admin_tests()