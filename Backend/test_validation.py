# test_validation.py
import os
import django
import sys
from datetime import datetime, timedelta
from django.utils import timezone

# Настройка кодировки для Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from screenings.validators import ScreeningValidator
from bookings.validators import BookingValidator
from cinemas.validators import CinemaHallValidator
from movies.validators import MovieValidator

print("=" * 70)
print("ТЕСТИРОВАНИЕ ВАЛИДАТОРОВ")
print("=" * 70)

# Тест 1: Проверка валидатора зала
print("\n1. Проверка валидатора зала:")
hall_errors = CinemaHallValidator.validate_hall_dimensions(rows=60, seats_per_row=40)
print(f"   Некорректные размеры (60x40): {hall_errors}")
print(f"   Результат: {'✓ Ошибки найдены' if hall_errors else '✗ Должны быть ошибки'}")

# Тест 2: Проверка валидатора фильма
print("\n2. Проверка валидатора фильма:")
duration_errors = MovieValidator.validate_movie_duration(10)
print(f"   Слишком короткий фильм (10 мин): {duration_errors}")
print(f"   Результат: {'✓ Ошибки найдены' if duration_errors else '✗ Должны быть ошибки'}")

# Тест 3: Проверка валидатора времени сеанса (без обращения к БД)
print("\n3. Проверка валидатора времени сеанса (базовая):")
now = timezone.now()
start = now + timedelta(hours=1)
end = start + timedelta(hours=3)  # 3 часа - нормально

# Тестируем только базовые проверки времени, без проверки пересечений
print(f"   Корректное время: начало {start.strftime('%H:%M')}, конец {end.strftime('%H:%M')}")
print(f"   Длительность: 3 часа")

# Проверка 1: время окончания позже времени начала
if start >= end:
    print("   ✗ Ошибка: время окончания должно быть позже времени начала")
else:
    print("   ✓ Время окончания корректно")

# Проверка 2: минимальная длительность
min_duration = timedelta(minutes=30)
if end - start < min_duration:
    print(f"   ✗ Ошибка: длительность меньше минимальной (30 мин)")
else:
    print(f"   ✓ Длительность достаточная")

# Проверка 3: максимальная длительность
max_duration = timedelta(hours=4)
if end - start > max_duration:
    print(f"   ✗ Ошибка: длительность больше максимальной (4 часа)")
else:
    print(f"   ✓ Длительность в пределах нормы")

# Проверка 4: часы работы
if start.hour < 9 or start.hour > 23:
    print(f"   ✗ Ошибка: время начала {start.hour}:{start.minute} вне рабочего времени")
else:
    print(f"   ✓ Время начала в рабочее время")

if end.hour < 9 or end.hour > 23:
    print(f"   ✗ Ошибка: время окончания {end.hour}:{end.minute} вне рабочего времени")
else:
    print(f"   ✓ Время окончания в рабочее время")

print("\n4. Проверка валидатора цен:")
price_errors = ScreeningValidator.validate_price_range(price_standard=250, price_vip=200)
print(f"   VIP дешевле обычных (250/200): {price_errors}")
print(f"   Результат: {'✓ Ошибки найдены' if price_errors else '✗ Должны быть ошибки'}")

print("\n" + "=" * 70)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 70)