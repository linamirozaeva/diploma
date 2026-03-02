from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import CinemaHall, Seat
from .serializers import (
    CinemaHallSerializer,
    CinemaHallCreateSerializer,
    CinemaHallDetailSerializer,
    SeatSerializer
)

class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра мест (только чтение)
    Доступно всем пользователям
    """
    queryset = Seat.objects.filter(is_active=True)
    serializer_class = SeatSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """
        Фильтрация мест по залу
        """
        queryset = super().get_queryset()
        hall_id = self.request.query_params.get('hall')
        if hall_id:
            queryset = queryset.filter(hall_id=hall_id)
        return queryset.order_by('row', 'number')

router = DefaultRouter()
router.register(r'halls', views.CinemaHallViewSet, basename='cinemahall')
# Убираем регистрацию SeatViewSet, так как его нет в views.py
# Места доступны через действие seats у CinemaHallViewSet

urlpatterns = [
    path('', include(router.urls)),
]