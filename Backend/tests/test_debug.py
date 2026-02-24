# tests/test_debug.py
import requests
import sys

BASE_URL = 'http://127.0.0.1:8000'

def debug_connection():
    """Диагностика подключения к серверу"""
    print("ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ")
    print("="*50)
    
    # 1. Проверка localhost
    try:
        r = requests.get('http://localhost:8000/', timeout=2)
        print(f" http://localhost:8000/ - {r.status_code}")
    except Exception as e:
        print(f" http://localhost:8000/ - {e}")
    
    # 2. Проверка 127.0.0.1
    try:
        r = requests.get('http://127.0.0.1:8000/', timeout=2)
        print(f" http://127.0.0.1:8000/ - {r.status_code}")
    except Exception as e:
        print(f" http://127.0.0.1:8000/ - {e}")
    
    # 3. Проверка API
    try:
        r = requests.get('http://127.0.0.1:8000/api/movies/', timeout=2)
        print(f" API /movies/ - {r.status_code}")
    except Exception as e:
        print(f" API /movies/ - {e}")
    
    # 4. Информация о системе
    import socket
    print(f"\n Информация:")
    print(f"   Hostname: {socket.gethostname()}")
    print(f"   IP: {socket.gethostbyname(socket.gethostname())}")
    print(f"   Python: {sys.version}")

if __name__ == "__main__":
    debug_connection()