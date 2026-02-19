from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from movies.models import Movie
from config.permissions import IsAdminOrReadOnly, IsAdminUser
from .serializers import (
    MovieListSerializer, MovieDetailSerializer,
    MovieCreateUpdateSerializer
)
from screenings.models import Screening
from bookings.models import Booking

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение: админы могут всё, остальные только чтение
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_admin_user

class MovieViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления фильмами
    
    list: Все пользователи (включая гостей)
    retrieve: Все пользователи
    create: Только админы
    update: Только админы
    partial_update: Только админы
    destroy: Только админы
    """
    queryset = Movie.objects.all()
    permission_classes = [IsAdminOrReadOnly]  # Админы могут всё, остальные только чтение
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'director', 'description', 'cast']
    ordering_fields = ['title', 'release_date', 'duration', 'created_at']
    
    def get_queryset(self):
        """Фильтрация фильмов"""
        queryset = super().get_queryset()
        
        # Все видят только активные фильмы
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Выбор сериализатора"""
        if self.action in ['create', 'update', 'partial_update']:
            return MovieCreateUpdateSerializer
        elif self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieListSerializer
    
    @action(detail=False, methods=['get'])
    def now_showing(self, request):
        """
        Фильмы, которые сейчас в прокате
        GET /api/movies/now_showing/
        """
        # Находим фильмы, у которых есть сеансы на сегодня или в будущем
        today = timezone.now().date()
        movies_with_screenings = Screening.objects.filter(
        start_time__date__gte=today,
        is_active=True
        ).values_list('movie_id', flat=True).distinct()
    
        movies = self.queryset.filter(id__in=movies_with_screenings, is_active=True)
        serializer = self.get_serializer(movies, many=True)
    
        # Добавляем информацию о ближайших сеансах
        result = []
        for movie_data in serializer.data:
            movie_id = movie_data['id']
            next_screenings = Screening.objects.filter(
                movie_id=movie_id,
                start_time__gte=timezone.now(),
                is_active=True
            ).order_by('start_time')[:3]
        
            movie_data['next_screenings'] = [
                {
                    'id': s.id,
                    'start_time': s.start_time,
                    'hall_name': s.hall.name if s.hall else None,
                    'price_from': min(s.price_standard, s.price_vip)
                }
                for s in next_screenings
            ]
            result.append(movie_data)
    
        return Response(result)  # <- Здесь должна быть ОДНА закрывающая скобка
    
    @action(detail=True, methods=['get'])
    def screenings(self, request, pk=None):
        """
        Сеансы фильма - доступно всем
        """
        movie = self.get_object()
        
        screenings = Screening.objects.filter(
            movie=movie,
            start_time__gte=timezone.now(),
            is_active=True
        ).order_by('start_time')
        
        from screenings.serializers import ScreeningListSerializer
        serializer = ScreeningListSerializer(screenings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request, pk=None):
        """
        Статистика по фильму - только для админов
        """
        movie = self.get_object()
        
        total_screenings = Screening.objects.filter(movie=movie).count()
        total_bookings = Booking.objects.filter(screening__movie=movie).count()
        total_revenue = Booking.objects.filter(
            screening__movie=movie,
            status='confirmed'
        ).aggregate(total=Sum('price'))['total'] or 0
        
        return Response({
            'total_screenings': total_screenings,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue
        })    
        """
    ViewSet для управления фильмами
    
    list: Получить список всех фильмов
    retrieve: Получить детальную информацию о фильме
    create: Создать новый фильм (только админ)
    update: Обновить фильм (только админ)
    partial_update: Частично обновить фильм (только админ)
    destroy: Удалить фильм (только админ)
    """
    queryset = Movie.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'director', 'description', 'cast']
    ordering_fields = ['title', 'release_date', 'duration', 'created_at']
    
    def get_queryset(self):
        """Фильтрация фильмов по параметрам запроса"""
        queryset = super().get_queryset()
        
        # Фильтр по активности
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Фильтр по длительности
        min_duration = self.request.query_params.get('min_duration')
        max_duration = self.request.query_params.get('max_duration')
        
        if min_duration:
            queryset = queryset.filter(duration__gte=int(min_duration))
        if max_duration:
            queryset = queryset.filter(duration__lte=int(max_duration))
        
        # Фильтр по году выпуска
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(release_date__year=year)
        
        # Поиск по названию
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(director__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-release_date', '-created_at')
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action in ['create', 'update', 'partial_update']:
            return MovieCreateUpdateSerializer
        elif self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieListSerializer
    
    @action(detail=False, methods=['get'])
    def now_showing(self, request):
        """
        Фильмы, которые сейчас в прокате
        GET /api/movies/now_showing/
        """
        # Находим фильмы, у которых есть сеансы на сегодня или в будущем
        today = timezone.now().date()
        movies_with_screenings = Screening.objects.filter(
            start_time__date__gte=today,
            is_active=True
        ).values_list('movie_id', flat=True).distinct()
        
        movies = self.queryset.filter(id__in=movies_with_screenings, is_active=True)
        serializer = self.get_serializer(movies, many=True)
        
        # Добавляем информацию о ближайших сеансах
        result = []
        for movie_data in serializer.data:
            movie_id = movie_data['id']
            next_screenings = Screening.objects.filter(
                movie_id=movie_id,
                start_time__gte=timezone.now(),
                is_active=True
            ).order_by('start_time')[:3]
            
            movie_data['next_screenings'] = [
                {
                    'id': s.id,
                    'start_time': s.start_time,
                    'hall_name': s.hall.name if s.hall else None,
                    'price_from': min(s.price_standard, s.price_vip)
                }
                for s in next_screenings
            ]
            result.append(movie_data)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def coming_soon(self, request):
        """
        Фильмы, которые скоро выйдут
        GET /api/movies/coming_soon/
        """
        today = timezone.now().date()
        month_later = today + timedelta(days=30)
        
        movies = self.queryset.filter(
            release_date__gte=today,
            release_date__lte=month_later,
            is_active=True
        ).order_by('release_date')
        
        serializer = self.get_serializer(movies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def screenings(self, request, pk=None):
        """
        Получить все сеансы для конкретного фильма
        GET /api/movies/{id}/screenings/
        """
        movie = self.get_object()
        
        # Параметры фильтрации
        date = request.query_params.get('date')
        hall_id = request.query_params.get('hall')
        
        screenings = Screening.objects.filter(movie=movie, is_active=True)
        
        if date:
            screenings = screenings.filter(start_time__date=date)
        else:
            # По умолчанию показываем будущие сеансы
            screenings = screenings.filter(start_time__gte=timezone.now())
        
        if hall_id:
            screenings = screenings.filter(hall_id=hall_id)
        
        screenings = screenings.order_by('start_time')
        
        from screenings.serializers import ScreeningListSerializer
        serializer = ScreeningListSerializer(screenings, many=True)
        
        # Группировка по датам
        from collections import defaultdict
        grouped = defaultdict(list)
        for screening in serializer.data:
            date_str = screening['start_time'][:10]  # YYYY-MM-DD
            grouped[date_str].append(screening)
        
        return Response({
            'movie_id': movie.id,
            'movie_title': movie.title,
            'total_screenings': screenings.count(),
            'by_date': dict(grouped)
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Статистика по фильму
        GET /api/movies/{id}/stats/
        """
        movie = self.get_object()
        
        # Общее количество сеансов
        total_screenings = Screening.objects.filter(movie=movie).count()
        future_screenings = Screening.objects.filter(
            movie=movie,
            start_time__gte=timezone.now()
        ).count()
        
        # Количество бронирований
        total_bookings = Booking.objects.filter(
            screening__movie=movie
        ).count()
        
        # Выручка
        total_revenue = Booking.objects.filter(
            screening__movie=movie,
            status='confirmed'
        ).aggregate(total=Sum('price'))['total'] or 0
        
        return Response({
            'movie_id': movie.id,
            'movie_title': movie.title,
            'total_screenings': total_screenings,
            'future_screenings': future_screenings,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue
        })