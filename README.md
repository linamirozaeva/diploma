# Cinema Booking System

Полноценная система онлайн-бронирования билетов в кинотеатр. Проект состоит из Django REST API (бэкенд) и React-приложения (фронтенд).

## Содержание
- [Технологии](#технологии)
- [Архитектура проекта](#архитектура-проекта)
- [Функциональность](#функциональность)
- [Установка и запуск](#установка-и-запуск)
  - [Бэкенд](#бэкенд)
  - [Фронтенд](#фронтенд)
- [API Эндпоинты](#api-эндпоинты)
- [Структура проекта](#структура-проекта)
- [Модели данных](#модели-данных)
- [Тестирование](#тестирование)
- [Деплой](#деплой)
- [Команда](#команда)

## Технологии

### Бэкенд
- Django 4.2
- Django REST Framework
- PostgreSQL / SQLite
- JWT (djangorestframework-simplejwt)
- qrcode[pil]
- Pillow

### Фронтенд
- React 18
- Vite
- React Router 6
- Axios
- Tailwind CSS
- qrcode.react
- Vitest + Testing Library

## Архитектура проекта

```
cinema-booking/
├── Backend/              # Django приложение
│   ├── config/          # Настройки проекта
│   ├── users/           # Управление пользователями
│   ├── cinemas/         # Кинозалы и места
│   ├── movies/          # Фильмы
│   ├── screenings/      # Сеансы
│   ├── bookings/        # Бронирования
│   └── tests/           # Тесты бэкенда
│
└── frontend/            # React приложение
    ├── src/
    │   ├── pages/       # Страницы
    │   │   ├── public/  # Публичные страницы
    │   │   └── admin/   # Админ-панель
    │   ├── components/  # UI компоненты
    │   ├── context/     # Контексты (Auth)
    │   ├── services/    # API сервисы
    │   └── tests/       # Тесты фронтенда
    └── public/          # Статические файлы
```

## Функциональность

### Для гостей (без авторизации)
- Просмотр списка фильмов с постерами
- Просмотр кинозалов и схемы мест
- Просмотр расписания сеансов
- Фильтрация сеансов по дате
- Проверка доступности мест

### Для авторизованных пользователей
- Все возможности гостей
- Бронирование билетов (выбор нескольких мест)
- Просмотр истории бронирований
- Отмена бронирований
- Получение QR-кода билета

### Для администраторов
- Полный CRUD для фильмов (с загрузкой постеров)
- Полный CRUD для кинозалов (с визуальной схемой мест)
- Полный CRUD для сеансов (с проверкой пересечений)
- Просмотр всех бронирований
- Поиск и фильтрация бронирований
- Управление типами мест (обычные/VIP/заблокированные)
- Статистика по продажам

## Установка и запуск

### Предварительные требования
- Python 3.10+
- Node.js 18+
- npm или yarn
- Git
- PostgreSQL (опционально, для продакшена)

### Бэкенд

```bash
# 1. Клонировать репозиторий
git clone <url-репозитория>
cd cinema-booking

# 2. Перейти в папку бэкенда
cd Backend

# 3. Создать и активировать виртуальное окружение
python -m venv venv

# для Windows (Git Bash)
source venv/Scripts/activate

# для Windows (CMD)
venv\Scripts\activate

# для Linux/Mac
source venv/bin/activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser
# Введите: admin, admin@example.com, admin123

# 7. Запустить сервер
python manage.py runserver
```

### Фронтенд

```bash
# 1. В новом терминале перейти в папку фронтенда
cd frontend

# 2. Установить зависимости
npm install

# 3. Создать файл .env (при необходимости)
echo "VITE_API_URL=http://127.0.0.1:8000/api" > .env

# 4. Запустить сервер разработки
npm run dev

# 5. Открыть браузер по адресу http://localhost:5173
```

## API Эндпоинты

### Аутентификация
POST /api/auth/register/ - Регистрация пользователя
POST /api/auth/login/ - Получение JWT токена
POST /api/auth/refresh/ - Обновление токена
GET /api/auth/me/ - Информация о текущем пользователе

### Фильмы
GET /api/movies/ - Список всех фильмов (все пользователи)
GET /api/movies/{id}/ - Детали фильма (все пользователи)
POST /api/movies/ - Создать фильм (только администратор)
PUT /api/movies/{id}/ - Обновить фильм (только администратор)
DELETE /api/movies/{id}/ - Удалить фильм (только администратор)

### Кинозалы
GET /api/cinemas/halls/ - Список залов (все пользователи)
GET /api/cinemas/halls/{id}/ - Детали зала (все пользователи)
GET /api/cinemas/halls/{id}/seats/ - Места в зале (все пользователи)
POST /api/cinemas/halls/ - Создать зал (только администратор)
POST /api/cinemas/halls/{id}/update_seat_type/ - Изменить тип места (только администратор)
POST /api/cinemas/halls/{id}/configure/ - Перенастроить зал (только администратор)

### Сеансы
GET /api/screenings/ - Список сеансов с фильтрацией (все пользователи)
GET /api/screenings/{id}/ - Детали сеанса (все пользователи)
GET /api/screenings/{id}/available_seats/ - Доступные места (все пользователи)
POST /api/screenings/{id}/book_seats/ - Забронировать места (только авторизованные)
POST /api/screenings/ - Создать сеанс (только администратор)
PUT /api/screenings/{id}/ - Обновить сеанс (только администратор)
DELETE /api/screenings/{id}/ - Удалить сеанс (только администратор)

### Бронирования
GET /api/bookings/ - Все бронирования (только администратор)
GET /api/bookings/my_bookings/ - Мои бронирования (только авторизованные)
GET /api/bookings/{id}/ - Детали бронирования (владелец или администратор)
POST /api/bookings/{id}/cancel/ - Отменить бронирование (владелец или администратор)
GET /api/bookings/{id}/qr_code/ - Получить QR-код (владелец или администратор)
POST /api/bookings/verify/ - Проверить билет по коду (только администратор)
GET /api/bookings/stats/ - Статистика (только администратор)

## Структура проекта

```
cinema-booking/
├── Backend/
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── permissions.py
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── cinemas/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── movies/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── screenings/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── bookings/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── media/
│   └── manage.py
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── public/
    │   │   │   ├── HomePage.jsx
    │   │   │   ├── MoviePage.jsx
    │   │   │   ├── HallPage.jsx
    │   │   │   ├── PaymentPage.jsx
    │   │   │   ├── TicketPage.jsx
    │   │   │   ├── MyTicketsPage.jsx
    │   │   │   ├── LoginPage.jsx
    │   │   │   └── RegisterPage.jsx
    │   │   └── admin/
    │   │       ├── AdminLayout.jsx
    │   │       ├── AdminDashboard.jsx
    │   │       ├── AdminHalls.jsx
    │   │       ├── AdminMovies.jsx
    │   │       ├── AdminScreenings.jsx
    │   │       └── AdminBookings.jsx
    │   ├── components/
    │   │   ├── layout/
    │   │   │   └── Header.jsx
    │   │   └── ui/
    │   │       └── Notification.jsx
    │   ├── context/
    │   │   └── AuthContext.jsx
    │   ├── services/
    │   │   └── api.js
    │   ├── styles/
    │   │   ├── public/
    │   │   │   └── main.css
    │   │   └── admin/
    │   │       └── admin.css
    │   └── assets/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

## Модели данных

### User
- username (уникальное)
- email (уникальное)
- password (хэшированный)
- first_name
- last_name
- phone
- user_type (guest/admin)
- is_verified
- date_joined

### CinemaHall
- name
- rows
- seats_per_row
- description
- is_active
- created_at

### Seat
- hall (ForeignKey)
- row
- number
- seat_type (standard/vip/disabled)
- is_active

### Movie
- title
- description
- duration
- poster
- release_date
- country
- director
- cast
- age_rating
- is_active
- created_at

### Screening
- movie (ForeignKey)
- hall (ForeignKey)
- start_time
- end_time
- price_standard
- price_vip
- is_active

### Booking
- user (ForeignKey)
- screening (ForeignKey)
- seat (ForeignKey)
- booking_code (уникальный)
- price
- status (confirmed/cancelled/used)
- qr_code
- created_at

## Тестирование

### Запуск тестов бэкенда
```bash
cd Backend
python manage.py test
```

### Запуск тестов фронтенда
```bash
cd frontend
npm test
npm run test:coverage
npm run test:ui
```

### Результаты тестирования
- Бэкенд: 26 тестов
- Фронтенд: 12 тестов
- Покрытие кода: высокое

## Деплой

### Бэкенд на PythonAnywhere
1. Загрузить код на PythonAnywhere
2. Создать виртуальное окружение
3. Установить зависимости из requirements.txt
4. Настроить базу данных PostgreSQL
5. Настроить статические файлы
6. Настроить WSGI конфигурацию

### Фронтенд на Netlify/Vercel
```bash
cd frontend
npm run build
```
Загрузить папку dist на Netlify или Vercel

### Переменные окружения для продакшена

Бэкенд (.env):
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost/dbname
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

Фронтенд (.env):
```
VITE_API_URL=https://your-backend-domain.com/api
```

## Команда

- Разработчик: Васько Каролина Алексеевна
- Курс: Дипломный проект
- Год: 2026

## Итоги

Бэкенд: 26/26 тестов проходят
Фронтенд: 12/12 тестов проходят
Функционал: 100% реализован
Дизайн: Соответствует макетам

Проект полностью готов к демонстрации и деплою.