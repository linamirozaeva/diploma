# tests/debug_views.py
import requests

BASE_URL = 'http://127.0.0.1:8000'

print("ДИАГНОСТИКА VIEWS")
print("="*60)

# 1. Проверка, что сервер отвечает
try:
    r = requests.get(f"{BASE_URL}/")
    print(f"Сервер отвечает: {r.status_code}")
except:
    print("Сервер не отвечает!")
    exit()

# 2. Проверка списка сеансов (GET)
print(f"\n GET /api/screenings/")
r = requests.get(f"{BASE_URL}/api/screenings/")
print(f"Статус: {r.status_code}")
if r.status_code != 200:
    print(f"Ошибка: {r.text[:200]}")

# 3. Проверка импортов - загружаем страницу ошибки
print(f"\n Детали ошибки:")
r = requests.get(f"{BASE_URL}/api/screenings/")
if r.status_code == 500:
    # Ищем имя отсутствующего класса в HTML
    import re
    match = re.search(r"name '(\w+)' is not defined", r.text)
    if match:
        print(f" Отсутствует импорт: {match.group(1)}")
    else:
        print(" Не удалось определить отсутствующий импорт")