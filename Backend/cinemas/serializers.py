from rest_framework import serializers
from .models import CinemaHall, Seat
from .validators import CinemaHallValidator, SeatValidator

class SeatSerializer(serializers.ModelSerializer):
    """
    Сериализатор для мест в кинозале
    """
    class Meta:
        model = Seat
        fields = ('id', 'row', 'number', 'seat_type', 'is_active')  # Добавлен id
        read_only_fields = ('id',)

class CinemaHallListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка кинозалов
    """
    total_seats = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CinemaHall
        fields = ('id', 'name', 'rows', 'seats_per_row', 'total_seats', 'is_active', 'description')
        # ID добавлен

class CinemaHallDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о кинозале
    """
    seats = SeatSerializer(many=True, read_only=True)
    total_seats = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CinemaHall
        fields = ('id', 'name', 'rows', 'seats_per_row', 'description', 'is_active', 
                  'total_seats', 'seats', 'created_at', 'updated_at')
        # ID добавлен

class CinemaHallCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания кинозала
    """
    class Meta:
        model = CinemaHall
        fields = ('id', 'name', 'rows', 'seats_per_row', 'description')  # Добавлен id
        read_only_fields = ('id', 'created_at', 'updated_at')  # ID только для чтения
    
    def validate(self, data):
        # Проверка размеров зала
        dimension_errors = CinemaHallValidator.validate_hall_dimensions(
            rows=data['rows'],
            seats_per_row=data['seats_per_row']
        )
        if dimension_errors:
            raise serializers.ValidationError(dimension_errors)
        
        # Проверка уникальности имени зала
        if CinemaHall.objects.filter(name=data['name']).exists():
            raise serializers.ValidationError({
                "name": "Зал с таким названием уже существует"
            })
        
        return data
    
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
        
        if seats:
            Seat.objects.bulk_create(seats)
        
        return hall

class SeatUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления типа места
    """
    class Meta:
        model = Seat
        fields = ('id', 'seat_type', 'is_active')  # Добавлен id
        read_only_fields = ('id',)