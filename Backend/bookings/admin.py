from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления бронированиями
    """
    list_display = ('id', 'booking_code', 'user_info', 'movie_title', 'seat_info', 
                    'screening_time', 'price', 'status_colored', 'qr_code_link')
    list_display_links = ('id', 'booking_code')
    list_filter = ('status', 'created_at', 'screening__movie', 'screening__hall')
    search_fields = ('booking_code', 'user__username', 'user__email', 'screening__movie__title')
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('booking_code', 'user', 'status', 'price')
        }),
        ('Сеанс и место', {
            'fields': ('screening', 'seat'),
        }),
        ('QR-код', {
            'fields': ('qr_code',),
            'description': 'QR-код для контроллера'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('booking_code', 'created_at', 'updated_at', 'qr_code_preview')
    
    actions = ['confirm_bookings', 'cancel_bookings', 'mark_as_used']
    
    def user_info(self, obj):
        """Информация о пользователе"""
        if obj.user:
            return format_html('{}<br><small>{}</small>', 
                             obj.user.username, obj.user.email)
        return "Аноним"
    user_info.short_description = 'Пользователь'
    
    def movie_title(self, obj):
        """Название фильма"""
        return obj.screening.movie.title if obj.screening and obj.screening.movie else "-"
    movie_title.short_description = 'Фильм'
    
    def seat_info(self, obj):
        """Информация о месте"""
        if obj.seat:
            return f"Ряд {obj.seat.row}, Место {obj.seat.number} ({obj.seat.seat_type})"
        return "-"
    seat_info.short_description = 'Место'
    
    def screening_time(self, obj):
        """Время сеанса"""
        if obj.screening:
            return obj.screening.start_time
        return "-"
    screening_time.short_description = 'Время сеанса'
    screening_time.admin_order_field = 'screening__start_time'
    
    def status_colored(self, obj):
        """Статус с цветом"""
        colors = {
            'confirmed': '#28a745',
            'pending': '#ffc107',
            'cancelled': '#dc3545',
            'used': '#17a2b8'
        }
        status_names = {
            'confirmed': 'Подтверждено',
            'pending': 'Ожидает',
            'cancelled': 'Отменено',
            'used': 'Использовано'
        }
        color = colors.get(obj.status, '#6c757d')
        name = status_names.get(obj.status, obj.status)
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                         color, name)
    status_colored.short_description = 'Статус'
    
    def qr_code_preview(self, obj):
        """Превью QR-кода"""
        if obj.qr_code:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', 
                             obj.qr_code.url)
        return "Нет QR-кода"
    qr_code_preview.short_description = 'Превью QR'
    
    def qr_code_link(self, obj):
        """Ссылка на QR-код"""
        if obj.qr_code:
            return format_html('<a href="{}" target="_blank">QR</a>', obj.qr_code.url)
        return "-"
    qr_code_link.short_description = 'QR'
    
    def confirm_bookings(self, request, queryset):
        """Подтвердить бронирования"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} бронирований подтверждены')
    confirm_bookings.short_description = "Подтвердить"
    
    def cancel_bookings(self, request, queryset):
        """Отменить бронирования"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} бронирований отменены')
    cancel_bookings.short_description = "Отменить"
    
    def mark_as_used(self, request, queryset):
        """Отметить как использованные"""
        updated = queryset.update(status='used')
        self.message_user(request, f'{updated} бронирований отмечены как использованные')
    mark_as_used.short_description = "Отметить использованными"