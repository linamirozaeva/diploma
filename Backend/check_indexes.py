# check_indexes.py
import sqlite3
import os

db_path = 'db.sqlite3'

if not os.path.exists(db_path):
    print(f"База данных {db_path} не найдена")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Проверка индексов для movies_movie
print("ИНДЕКСЫ ТАБЛИЦЫ movies_movie:")
print("-" * 40)
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='movies_movie'")
indexes = cursor.fetchall()
for idx in indexes:
    print(f"  {idx[0]}")

print()

# Проверка индексов для screenings_screening
print("ИНДЕКСЫ ТАБЛИЦЫ screenings_screening:")
print("-" * 40)
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='screenings_screening'")
indexes = cursor.fetchall()
for idx in indexes:
    print(f"  {idx[0]}")

print()

# Проверка индексов для cinemas_cinemahall
print("ИНДЕКСЫ ТАБЛИЦЫ cinemas_cinemahall:")
print("-" * 40)
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='cinemas_cinemahall'")
indexes = cursor.fetchall()
for idx in indexes:
    print(f"  {idx[0]}")

print()

# Проверка индексов для bookings_booking
print("ИНДЕКСЫ ТАБЛИЦЫ bookings_booking:")
print("-" * 40)
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='bookings_booking'")
indexes = cursor.fetchall()
for idx in indexes:
    print(f"  {idx[0]}")

conn.close()