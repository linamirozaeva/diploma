from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления фильмами
    """
    list_display = ('id', 'title', 'duration', 'release_date', 'director', 
                    'is_active', 'get_poster_preview', 'get_screenings_link')
    list_display_links = ('id', 'title')
    list_filter = ('is_active', 'release_date', 'director')
    search_fields = ('title', 'director', 'description', 'cast')
    list_editable = ('is_active',)
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'duration', 'is_active')
        }),
        ('Даты и создатели', {
            'fields': ('release_date', 'director', 'cast')
        }),
        ('Медиа', {
            'fields': ('poster',),
            'description': 'Загрузите постер фильма'
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'get_poster_preview')
    
    actions = ['activate_movies', 'deactivate_movies', 'duplicate_movie']
    
    def get_poster_preview(self, obj):
        """Превью постера"""
        if obj.poster:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', 
                             obj.poster.url)
        return "Нет постера"
    get_poster_preview.short_description = 'Превью'
    
    def get_screenings_link(self, obj):
        """Ссылка на сеансы этого фильма"""
        from screenings.models import Screening
        count = Screening.objects.filter(movie=obj).count()
        url = reverse('admin:screenings_screening_changelist') + f'?movie__id__exact={obj.id}'
        return format_html('<a href="{}">{} сеансов</a>', url, count)
    get_screenings_link.short_description = 'Сеансы'
    
    def activate_movies(self, request, queryset):
        """Активировать фильмы"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} фильмов активированы')
    activate_movies.short_description = "Активировать"
    
    def deactivate_movies(self, request, queryset):
        """Деактивировать фильмы"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} фильмов деактивированы')
    deactivate_movies.short_description = "Деактивировать"
    
    def duplicate_movie(self, request, queryset):
        """Копировать фильм"""
        for movie in queryset:
            movie.pk = None
            movie.title = f"{movie.title} (копия)"
            movie.save()
        self.message_user(request, f'Скопировано {queryset.count()} фильмов')
    duplicate_movie.short_description = "Копировать выбранные фильмы"