from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Разрешение только для администраторов.
    Проверяет, является ли пользователь администратором.
    Используется для эндпоинтов, доступных исключительно админам.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin_user
    
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user.is_admin_user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение: админы могут всё, остальные только чтение.
    GET, HEAD, OPTIONS - доступны всем
    POST, PUT, PATCH, DELETE - только админам
    """
    def has_permission(self, request, view):
        # Разрешить чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Изменение только для админов
        return request.user and request.user.is_authenticated and request.user.is_admin_user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешение: владелец объекта или админ.
    Используется для объектов, у которых есть поле 'user' или 'owner'.
    """
    def has_object_permission(self, request, view, obj):
        # Админы могут всё
        if request.user and request.user.is_authenticated and request.user.is_admin_user:
            return True
        
        # Для остальных проверяем, являются ли они владельцами
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsOwnerOrAdminForBooking(permissions.BasePermission):
    """
    Разрешение для бронирований: владелец брони или админ.
    Специализированный класс для модели Booking.
    """
    def has_object_permission(self, request, view, obj):
        # Админы могут всё
        if request.user and request.user.is_authenticated and request.user.is_admin_user:
            return True
        
        # Для обычных пользователей - только свои брони
        return obj.user == request.user


class IsAuthenticatedAndNotBanned(permissions.BasePermission):
    """
    Разрешение для авторизованных пользователей (не забаненных).
    Проверяет, что пользователь авторизован и активен.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Проверка, активен ли пользователь
        return request.user.is_active


class CanCreateBooking(permissions.BasePermission):
    """
    Разрешение на создание бронирования.
    По умолчанию только авторизованные пользователи.
    """
    def has_permission(self, request, view):
        # Только авторизованные пользователи могут создавать бронирования
        return request.user and request.user.is_authenticated


class CanCancelBooking(permissions.BasePermission):
    """
    Разрешение на отмену бронирования (своё или админ).
    Также проверяет временные ограничения (нельзя отменить за 30 минут до начала).
    """
    def has_object_permission(self, request, view, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        # Админы могут отменять любые брони
        if request.user and request.user.is_authenticated and request.user.is_admin_user:
            return True
        
        # Обычные пользователи могут отменять только свои брони
        if obj.user == request.user:
            # Проверка времени: нельзя отменить за 30 минут до начала
            time_until = obj.screening.start_time - timezone.now()
            if time_until.total_seconds() < 30 * 60:  # 30 минут в секундах
                return False
            return True
        
        return False


class CanViewBookings(permissions.BasePermission):
    """
    Разрешение на просмотр бронирований.
    Админы видят все, пользователи только свои (фильтрация в queryset).
    """
    def has_permission(self, request, view):
        # Анонимные пользователи ничего не видят
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Админы видят все
        if request.user.is_admin_user:
            return True
        
        # Обычные пользователи видят только свои (фильтрация будет в queryset)
        return True


class PublicAccess(permissions.BasePermission):
    """
    Полностью публичный доступ (для эндпоинтов типа check_seats).
    Не требует никакой авторизации.
    """
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        return True


class IsAdminOrOwnerForUser(permissions.BasePermission):
    """
    Разрешение для работы с пользователями:
    - Админ может работать с любым пользователем
    - Обычный пользователь может работать только со своим профилем
    """
    def has_object_permission(self, request, view, obj):
        # Админы могут всё
        if request.user and request.user.is_authenticated and request.user.is_admin_user:
            return True
        
        # Пользователи могут работать только с собой
        return obj == request.user


class IsAdminForStats(permissions.BasePermission):
    """
    Разрешение для доступа к статистике (только админы).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin_user


class IsAdminForVerification(permissions.BasePermission):
    """
    Разрешение для верификации билетов (только админы/контроллеры).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin_user