from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Screening

@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления сеансами
    """
    list_display = ('id', 'movie_title', 'hall_name', 'start_time', 'end_time', 
                    'duration_display', 'price_range', 'is_active', 'get_bookings_link')
    list_display_links = ('id', 'movie_title')
    list_filter = ('is_active', 'hall', 'start_time', 'movie')
    search_fields = ('movie__title', 'hall__name')
    list_editable = ('is_active',)
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('movie', 'hall', 'is_active')
        }),
        ('Время', {
            'fields': ('start_time', 'end_time'),
            'description': 'Время начала и окончания сеанса'
        }),
        ('Цены', {
            'fields': ('price_standard', 'price_vip'),
            'description': 'Цены на обычные и VIP места'
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['activate_screenings', 'deactivate_screenings', 'duplicate_screening']
    
    def movie_title(self, obj):
        """Название фильма"""
        return obj.movie.title if obj.movie else "-"
    movie_title.short_description = 'Фильм'
    movie_title.admin_order_field = 'movie__title'
    
    def hall_name(self, obj):
        """Название зала"""
        return obj.hall.name if obj.hall else "-"
    hall_name.short_description = 'Зал'
    hall_name.admin_order_field = 'hall__name'
    
    def duration_display(self, obj):
        """Длительность сеанса"""
        duration = obj.end_time - obj.start_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}ч {minutes}мин"
    duration_display.short_description = 'Длительность'
    
    def price_range(self, obj):
        """Диапазон цен"""
        if obj.price_vip > obj.price_standard:
            return format_html('{} / {}', obj.price_standard, obj.price_vip)
        return obj.price_standard
    price_range.short_description = 'Цены'
    
    def get_bookings_link(self, obj):
        """Ссылка на бронирования этого сеанса"""
        from bookings.models import Booking
        count = Booking.objects.filter(screening=obj).count()
        url = reverse('admin:bookings_booking_changelist') + f'?screening__id__exact={obj.id}'
        return format_html('<a href="{}">{} броней</a>', url, count)
    get_bookings_link.short_description = 'Бронирования'
    
    def activate_screenings(self, request, queryset):
        """Активировать сеансы"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} сеансов активированы')
    activate_screenings.short_description = "Активировать"
    
    def deactivate_screenings(self, request, queryset):
        """Деактивировать сеансы"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} сеансов деактивированы')
    deactivate_screenings.short_description = "Деактивировать"
    
    def duplicate_screening(self, request, queryset):
        """Копировать сеанс"""
        for screening in queryset:
            screening.pk = None
            screening.save()
        self.message_user(request, f'Скопировано {queryset.count()} сеансов')
    duplicate_screening.short_description = "Копировать выбранные сеансы"