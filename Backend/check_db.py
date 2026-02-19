
import sqlite3
import os

db_path = 'db.sqlite3'

if not os.path.exists(db_path):
    print(f" База данных {db_path} не найдена")
    exit(1)

print(f" База данных найдена: {db_path}")
print("=" * 50)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("\n ТАБЛИЦЫ В БАЗЕ ДАННЫХ:")
for table in tables:
    print(f"   - {table[0]}")

print("\n СТРУКТУРА ТАБЛИЦЫ movies_movie:")
try:
    cursor.execute("PRAGMA table_info(movies_movie);")
    columns = cursor.fetchall()
    if columns:
        print("   Колонка | Тип | Null | Default")
        print("   " + "-" * 40)
        for col in columns:
            print(f"   {col[1]} | {col[2]} | {'YES' if col[3] else 'NO'} | {col[4]}")
    else:
        print("   Таблица movies_movie не существует")
except sqlite3.OperationalError as e:
    print(f"   Ошибка: {e}")

print("\n СТРУКТУРА ТАБЛИЦЫ screenings_screening:")
try:
    cursor.execute("PRAGMA table_info(screenings_screening);")
    columns = cursor.fetchall()
    if columns:
        print("   Колонка | Тип | Null | Default")
        print("   " + "-" * 40)
        for col in columns:
            print(f"   {col[1]} | {col[2]} | {'YES' if col[3] else 'NO'} | {col[4]}")
    else:
        print("   Таблица screenings_screening не существует")
except sqlite3.OperationalError as e:
    print(f"   Ошибка: {e}")

print("\n СТРУКТУРА ТАБЛИЦЫ bookings_booking:")
try:
    cursor.execute("PRAGMA table_info(bookings_booking);")
    columns = cursor.fetchall()
    if columns:
        print("   Колонка | Тип | Null | Default")
        print("   " + "-" * 40)
        for col in columns:
            print(f"   {col[1]} | {col[2]} | {'YES' if col[3] else 'NO'} | {col[4]}")
    else:
        print("   Таблица bookings_booking не существует")
except sqlite3.OperationalError as e:
    print(f"   Ошибка: {e}")

conn.close()
print("\n" + "=" * 50)
