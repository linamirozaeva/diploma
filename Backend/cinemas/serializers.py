from rest_framework import serializers
from .models import CinemaHall, Seat

class SeatSerializer(serializers.ModelSerializer):
    """
    Сериализатор для мест в зале
    """
    class Meta:
        model = Seat
        fields = ['id', 'row', 'number', 'seat_type', 'is_active']

class CinemaHallSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра залов
    """
    seats = SeatSerializer(many=True, read_only=True)
    total_seats = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CinemaHall
        fields = [
            'id', 'name', 'rows', 'seats_per_row', 'description', 
            'is_active', 'total_seats', 'seats', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CinemaHallCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания зала (автоматически создает места)
    """
    class Meta:
        model = CinemaHall
        fields = ['name', 'rows', 'seats_per_row', 'description']
    
    def create(self, validated_data):
        # Создаем зал
        hall = CinemaHall.objects.create(**validated_data)
        
        # Автоматически создаем места для зала
        seats = []
        for row in range(1, hall.rows + 1):
            for number in range(1, hall.seats_per_row + 1):
                seats.append(
                    Seat(
                        hall=hall,
                        row=row,
                        number=number,
                        seat_type='standard'
                    )
                )
        Seat.objects.bulk_create(seats)
        
        return hall

class CinemaHallDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о зале
    """
    seats = SeatSerializer(many=True, read_only=True)
    total_seats = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CinemaHall
        fields = [
            'id', 'name', 'rows', 'seats_per_row', 'description',
            'is_active', 'total_seats', 'seats', 'created_at', 'updated_at'
        ]

class SeatUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления типа места
    """
    class Meta:
        model = Seat
        fields = ('id', 'seat_type', 'is_active')  # Добавлен id
        read_only_fields = ('id',)