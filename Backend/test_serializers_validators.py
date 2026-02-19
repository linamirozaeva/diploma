# test_serializers_validators.py
import os
import django
import sys
from datetime import datetime, timedelta

# Настройка кодировки для Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Для старых версий Python
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cinemas.validators import CinemaHallValidator
from movies.validators import MovieValidator
from screenings.validators import ScreeningValidator
from bookings.validators import BookingValidator

print("=" * 60)
print("ТЕСТИРОВАНИЕ СЕРИАЛИЗАТОРОВ И ВАЛИДАТОРОВ")
print("=" * 60)

# Тест 1: Проверка валидатора зала
print("\n1. Проверка валидатора зала:")
hall_errors = CinemaHallValidator.validate_hall_dimensions(rows=60, seats_per_row=40)
print(f"   Некорректные размеры (60x40): {hall_errors}")

# Тест 2: Проверка валидатора фильма
print("\n2. Проверка валидатора фильма:")
duration_errors = MovieValidator.validate_movie_duration(10)
print(f"   Слишком короткий фильм (10 мин): {duration_errors}")

# Тест 3: Проверка импортов сериализаторов
print("\n3. Проверка импортов сериализаторов:")

try:
    from cinemas.serializers import (
        SeatSerializer, CinemaHallListSerializer, 
        CinemaHallDetailSerializer, CinemaHallCreateSerializer
    )
    print("  cinemas.serializers - OK")
except Exception as e:
    print(f"  Ошибка в cinemas.serializers: {e}")

try:
    from movies.serializers import (
        MovieListSerializer, MovieDetailSerializer, MovieCreateUpdateSerializer
    )
    print("  movies.serializers - OK")
except Exception as e:
    print(f"  Ошибка в movies.serializers: {e}")

try:
    from screenings.serializers import (
        ScreeningListSerializer, ScreeningDetailSerializer, 
        ScreeningCreateUpdateSerializer
    )
    print("  screenings.serializers - OK")
except Exception as e:
    print(f"  Ошибка в screenings.serializers: {e}")

try:
    from bookings.serializers import (
        BookingListSerializer, BookingDetailSerializer, 
        BookingCreateSerializer, BookingCancelSerializer
    )
    print("  bookings.serializers - OK")
except Exception as e:
    print(f"  Ошибка в bookings.serializers: {e}")

print("\n" + "=" * 60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 60)