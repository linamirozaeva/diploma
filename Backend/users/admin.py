from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Админ-панель для управления пользователями
    """
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 
                    'user_type', 'is_staff', 'is_active', 'get_bookings_count')
    list_display_links = ('id', 'username')
    list_filter = ('user_type', 'is_staff', 'is_active', 'is_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    list_editable = ('user_type', 'is_active')
    list_per_page = 25
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'user_type', 'is_verified'),
            'classes': ('wide',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'phone', 'user_type'),
            'classes': ('wide',)
        }),
    )
    
    actions = ['make_admin', 'make_guest', 'activate_users', 'deactivate_users']
    
    def get_bookings_count(self, obj):
        """Количество бронирований пользователя"""
        count = obj.bookings.count()
        if count > 0:
            return format_html('<b style="color: #28a745;">{}</b>', count)
        return count
    get_bookings_count.short_description = 'Бронирований'
    
    def make_admin(self, request, queryset):
        """Сделать выбранных пользователей администраторами"""
        updated = queryset.update(user_type='admin', is_staff=True)
        self.message_user(request, f'{updated} пользователей стали администраторами')
    make_admin.short_description = "Сделать администраторами"
    
    def make_guest(self, request, queryset):
        """Сделать выбранных пользователей гостями"""
        updated = queryset.update(user_type='guest', is_staff=False)
        self.message_user(request, f'{updated} пользователей стали гостями')
    make_guest.short_description = "Сделать гостями"
    
    def activate_users(self, request, queryset):
        """Активировать выбранных пользователей"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} пользователей активированы')
    activate_users.short_description = "Активировать"
    
    def deactivate_users(self, request, queryset):
        """Деактивировать выбранных пользователей"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} пользователей деактивированы')
    deactivate_users.short_description = "Деактивировать"