from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

class ScreeningValidator:
    """
    Валидатор для сеансов
    """
    
    @staticmethod
    def validate_screening_times(start_time, end_time, hall, instance=None):
        """
        Проверка корректности времени сеанса и отсутствия пересечений
        Возвращает словарь с ошибками или пустой словарь
        """
        errors = {}
        
        # Проверка 1: Время окончания должно быть позже времени начала
        if start_time >= end_time:
            errors['end_time'] = "Время окончания должно быть позже времени начала"
            return errors
        
        # Проверка 2: Минимальная длительность сеанса (30 минут)
        min_duration = timedelta(minutes=30)
        if end_time - start_time < min_duration:
            errors['duration'] = "Длительность сеанса должна быть не менее 30 минут"
        
        # Проверка 3: Максимальная длительность (4 часа)
        max_duration = timedelta(hours=4)
        if end_time - start_time > max_duration:
            errors['duration'] = "Длительность сеанса не может превышать 4 часа"
        
        # Проверка 4: Сеанс не может быть в прошлом (для новых сеансов)
        if not instance and start_time < timezone.now():
            errors['start_time'] = "Нельзя создавать сеансы в прошлом"
        
        # Проверка 5: Часы работы кинотеатра (с 9:00 до 23:00)
        if start_time.hour < 9 or start_time.hour > 23:
            errors['start_time'] = "Сеансы доступны только с 9:00 до 23:00"
        
        if end_time.hour < 9 or end_time.hour > 23:
            errors['end_time'] = "Сеансы доступны только с 9:00 до 23:00"
        
        # Проверка 6: Пересечение с другими сеансами в этом же зале
        from .models import Screening
        
        # Базовый запрос для поиска пересекающихся сеансов
        overlapping = Screening.objects.filter(
            hall=hall,
            start_time__lt=end_time,
            end_time__gt=start_time,
            is_active=True
        )
        
        # Исключаем текущий сеанс при обновлении
        if instance:
            overlapping = overlapping.exclude(pk=instance.pk)
        
        if overlapping.exists():
            # Формируем понятное сообщение о конфликтующих сеансах
            conflicts = []
            for s in overlapping[:5]:  # Ограничим количество для читаемости
                movie_title = s.movie.title if s.movie else "Неизвестный фильм"
                time_str = s.start_time.strftime("%H:%M")
                end_str = s.end_time.strftime("%H:%M")
                conflicts.append(f"'{movie_title}' ({time_str}-{end_str})")
            
            if overlapping.count() > 5:
                conflicts.append(f"и еще {overlapping.count() - 5}...")
            
            errors['overlap'] = f"Этот зал уже занят в указанное время. Конфликтующие сеансы: {', '.join(conflicts)}"
        
        return errors
    
    @staticmethod
    def validate_screening_with_movie(movie, start_time, end_time):
        """
        Проверка соответствия длительности сеанса длительности фильма
        """
        errors = {}
        
        if not movie:
            return errors
        
        # Длительность сеанса в минутах
        screening_duration = (end_time - start_time).total_seconds() / 60
        
        # Длительность сеанса должна быть не меньше длительности фильма
        if screening_duration < movie.duration:
            errors['duration'] = (
                f"Длительность сеанса ({screening_duration:.0f} мин) "
                f"меньше длительности фильма ({movie.duration} мин)"
            )
        
        # Длительность сеанса не должна превышать длительность фильма больше чем на 30 минут
        max_allowed = movie.duration + 30
        if screening_duration > max_allowed:
            errors['duration'] = (
                f"Длительность сеанса ({screening_duration:.0f} мин) "
                f"слишком велика для этого фильма (макс. {max_allowed} мин)"
            )
        
        return errors
    
    @staticmethod
    def validate_price_range(price_standard, price_vip):
        """
        Проверка корректности цен
        """
        errors = {}
        
        if price_standard < 0:
            errors['price_standard'] = "Цена не может быть отрицательной"
        
        if price_vip < 0:
            errors['price_vip'] = "Цена не может быть отрицательной"
        
        if price_vip < price_standard:
            errors['price_vip'] = "VIP места не могут стоить дешевле обычных"
        
        return errors


class BatchScreeningValidator:
    """
    Валидатор для массового создания сеансов
    """
    
    @staticmethod
    def validate_batch_screenings(screenings_data):
        """
        Проверка списка сеансов на корректность
        Возвращает список ошибок
        """
        errors = []
        
        # Проверка на дублирование времени в одном зале
        hall_schedule = {}
        
        for i, data in enumerate(screenings_data):
            hall_id = data.get('hall')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            
            if not all([hall_id, start_time, end_time]):
                errors.append({
                    'index': i,
                    'error': 'Неполные данные: необходимы hall, start_time, end_time'
                })
                continue
            
            # Получаем дату для группировки
            if hasattr(start_time, 'date'):
                date_key = start_time.date()
            else:
                # Если это строка, пытаемся извлечь дату
                try:
                    from datetime import datetime
                    if isinstance(start_time, str):
                        dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        date_key = dt.date()
                    else:
                        date_key = str(start_time).split('T')[0]
                except:
                    date_key = str(start_time)
            
            key = f"{hall_id}_{date_key}"
            
            if key not in hall_schedule:
                hall_schedule[key] = []
            
            # Проверка пересечений внутри загружаемого списка
            for existing in hall_schedule[key]:
                if (start_time < existing['end_time'] and end_time > existing['start_time']):
                    errors.append({
                        'index': i,
                        'error': f"Сеанс пересекается с сеансом {existing['index']} в этом же зале"
                    })
                    break
            
            hall_schedule[key].append({
                'index': i,
                'start_time': start_time,
                'end_time': end_time
            })
        
        return errors