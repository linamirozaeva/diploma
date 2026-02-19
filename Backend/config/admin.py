from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import reverse

class CustomAdminSite(AdminSite):
    """
    Кастомная админ-панель
    """
    site_header = 'Cinema Booking System'
    site_title = 'Администрирование'
    index_title = 'Панель управления кинотеатром'
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Добавляем статистику
        from bookings.models import Booking
        from movies.models import Movie
        from screenings.models import Screening
        
        extra_context['stats'] = {
            'bookings_today': Booking.objects.filter(created_at__date=timezone.now().date()).count(),
            'active_movies': Movie.objects.filter(is_active=True).count(),
            'today_screenings': Screening.objects.filter(start_time__date=timezone.now().date()).count(),
        }
        
        return super().index(request, extra_context)

# Переопределяем стандартную админку
admin.site = CustomAdminSite()
admin.site.site_header = 'Cinema Booking System'
admin.site.site_title = 'Администрирование'
admin.site.index_title = 'Панель управления кинотеатром'