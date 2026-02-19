from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Разрешение только для администраторов
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin_user
    
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user.is_admin_user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение: админы могут всё, остальные только чтение
    """
    def has_permission(self, request, view):
        # Разрешить чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Изменение только для админов
        return request.user and request.user.is_authenticated and request.user.is_admin_user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешение: владелец объекта или админ
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
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        
        return False


class IsOwnerOrAdminForBooking(permissions.BasePermission):
    """
    Разрешение для бронирований: владелец брони или админ
    """
    def has_object_permission(self, request, view, obj):
        # Админы могут всё
        if request.user and request.user.is_authenticated and request.user.is_admin_user:
            return True
        
        # Для обычных пользователей - только свои брони
        return obj.user == request.user


class IsAuthenticatedAndNotBanned(permissions.BasePermission):
    """
    Разрешение для авторизованных пользователей (не забаненных)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Проверка, не забанен ли пользователь
        if hasattr(request.user, 'is_banned') and request.user.is_banned:
            return False
        
        # Проверка, активен ли пользователь
        return request.user.is_active


class CanCreateBooking(permissions.BasePermission):
    """
    Разрешение на создание бронирования
    """
    def has_permission(self, request, view):
        # Анонимные пользователи могут создавать бронирования?
        # Если да, то раскомментируйте следующую строку:
        # return True
        
        # Иначе только авторизованные
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Для создания объекта эта проверка не используется
        return True


class CanCancelBooking(permissions.BasePermission):
    """
    Разрешение на отмену бронирования (своё или админ)
    """
    def has_object_permission(self, request, view, obj):
        # Админы могут отменять любые брони
        if request.user and request.user.is_authenticated and request.user.is_admin_user:
            return True
        
        # Обычные пользователи могут отменять только свои брони
        if obj.user == request.user:
            # Дополнительная проверка: можно ли отменить по времени
            from django.utils import timezone
            from datetime import timedelta
            
            # Нельзя отменить за 30 минут до начала
            time_until = obj.screening.start_time - timezone.now()
            if time_until.total_seconds() < 30 * 60:
                return False
            
            return True
        
        return False


class CanViewBookings(permissions.BasePermission):
    """
    Разрешение на просмотр бронирований
    """
    def has_permission(self, request, view):
        # Админы видят все
        if request.user and request.user.is_authenticated and request.user.is_admin_user:
            return True
        
        # Обычные пользователи видят только свои (фильтрация в queryset)
        return request.user and request.user.is_authenticated