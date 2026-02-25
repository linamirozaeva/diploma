# delete_migrations.py
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Удаляем записи о миграциях
cursor.execute("DELETE FROM django_migrations WHERE app='bookings' AND name LIKE '0002%'")
cursor.execute("DELETE FROM django_migrations WHERE app='screenings' AND name LIKE '0002%'")
cursor.execute("DELETE FROM django_migrations WHERE app='movies' AND name LIKE '0002%'")
cursor.execute("DELETE FROM django_migrations WHERE app='cinemas' AND name LIKE '0002%'")

conn.commit()
conn.close()
print("Записи о миграциях удалены")