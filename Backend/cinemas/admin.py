from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CinemaHall, Seat

class SeatInline(admin.TabularInline):
    """
    Инлайн-редактирование мест в зале
    """
    model = Seat
    extra = 0
    fields = ('row', 'number', 'seat_type', 'is_active')
    list_editable = ('seat_type', 'is_active')
    ordering = ('row', 'number')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hall')

@admin.register(CinemaHall)
class CinemaHallAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления кинозалами
    """
    list_display = ('id', 'name', 'rows', 'seats_per_row', 'total_seats', 
                    'is_active', 'get_seats_link', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    list_per_page = 20
    inlines = [SeatInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Размеры зала', {
            'fields': ('rows', 'seats_per_row'),
            'description': 'После сохранения автоматически создадутся места'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'total_seats')
    
    actions = ['duplicate_hall', 'activate_halls', 'deactivate_halls']
    
    def get_seats_link(self, obj):
        """Ссылка на места в этом зале"""
        count = obj.seats.count()
        url = reverse('admin:cinemas_seat_changelist') + f'?hall__id__exact={obj.id}'
        return format_html('<a href="{}">{} мест</a>', url, count)
    get_seats_link.short_description = 'Места'
    
    def duplicate_hall(self, request, queryset):
        """Копирование выбранных залов"""
        for hall in queryset:
            old_id = hall.id
            hall.pk = None
            hall.name = f"{hall.name} (копия)"
            hall.save()
            
            # Копируем места
            for seat in Seat.objects.filter(hall_id=old_id):
                seat.pk = None
                seat.hall = hall
                seat.save()
        
        self.message_user(request, f"Скопировано {queryset.count()} залов")
    duplicate_hall.short_description = "Скопировать выбранные залы"
    
    def activate_halls(self, request, queryset):
        """Активировать залы"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} залов активированы')
    activate_halls.short_description = "Активировать"
    
    def deactivate_halls(self, request, queryset):
        """Деактивировать залы"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} залов деактивированы')
    deactivate_halls.short_description = "Деактивировать"

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления местами
    """
    list_display = ('id', 'hall', 'row', 'number', 'seat_type', 'is_active')
    list_display_links = ('id',)
    list_filter = ('hall', 'seat_type', 'is_active', 'row')
    search_fields = ('hall__name',)
    list_editable = ('seat_type', 'is_active')
    list_per_page = 50
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('hall', 'row', 'number', 'seat_type', 'is_active')
        }),
    )
    
    actions = ['make_vip', 'make_standard', 'activate_seats', 'deactivate_seats']
    
    def make_vip(self, request, queryset):
        """Сделать места VIP"""
        updated = queryset.update(seat_type='vip')
        self.message_user(request, f'{updated} мест стали VIP')
    make_vip.short_description = "Сделать VIP"
    
    def make_standard(self, request, queryset):
        """Сделать места обычными"""
        updated = queryset.update(seat_type='standard')
        self.message_user(request, f'{updated} мест стали обычными')
    make_standard.short_description = "Сделать обычными"
    
    def activate_seats(self, request, queryset):
        """Активировать места"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} мест активированы')
    activate_seats.short_description = "Активировать"
    
    def deactivate_seats(self, request, queryset):
        """Деактивировать места"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} мест деактивированы')
    deactivate_seats.short_description = "Деактивировать"