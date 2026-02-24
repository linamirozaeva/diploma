# tests/debug_qr.py
import requests
import sys
import io

# Настройка кодировки
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'http://127.0.0.1:8000/api'
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

print("ДИАГНОСТИКА QR-КОДА")
print("="*60)

# Логин
r = requests.post(f"{BASE_URL}/auth/login/", json=ADMIN_CREDENTIALS)
token = r.json().get('access')
headers = {'Authorization': f'Bearer {token}'}

# Получаем список бронирований
bookings = requests.get(f"{BASE_URL}/bookings/", headers=headers)
print(f"Бронирования: {bookings.status_code}")

if bookings.status_code == 200:
    bookings_data = bookings.json()
    print(f"Всего бронирований: {len(bookings_data)}")
    
    if bookings_data:
        booking = bookings_data[0]
        booking_id = booking.get('id')
        print(f"ID бронирования: {booking_id}")
        
        # Проверяем разные форматы QR
        print("\nПроверка форматов QR:")
        
        # Формат 1: базовый URL
        r1 = requests.get(f"{BASE_URL}/bookings/{booking_id}/qr_code/", headers=headers)
        print(f"Базовый: {r1.status_code}")
        
        # Формат 2: с параметром format=url
        r2 = requests.get(f"{BASE_URL}/bookings/{booking_id}/qr_code/?format=url", headers=headers)
        print(f"URL формат: {r2.status_code}")
        if r2.status_code == 200:
            print(f"Ответ: {r2.json()}")
        
        # Формат 3: с параметром format=base64
        r3 = requests.get(f"{BASE_URL}/bookings/{booking_id}/qr_code/?format=base64", headers=headers)
        print(f"Base64 формат: {r3.status_code}")
        if r3.status_code == 200:
            data = r3.json()
            print(f"Base64 длина: {len(data.get('qr_code_base64', ''))}")