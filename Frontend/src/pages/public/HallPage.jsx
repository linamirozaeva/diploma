import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const HallPage = () => {
  const { screeningId } = useParams();
  const navigate = useNavigate();
  const [screening, setScreening] = useState(null);
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScreeningData();
  }, [screeningId]);

  const fetchScreeningData = async () => {
    try {
      const screeningResponse = await api.get(`/screenings/${screeningId}/`);
      setScreening(screeningResponse.data);
      
      const seatsResponse = await api.get(`/screenings/${screeningId}/available_seats/`);
      setSeats(seatsResponse.data);
    } catch (error) {
      console.error('Error fetching screening:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSeat = (seat) => {
    if (seat.is_available) {
      setSelectedSeats(prev => {
        const isSelected = prev.some(s => s.seat_id === seat.seat_id);
        if (isSelected) {
          return prev.filter(s => s.seat_id !== seat.seat_id);
        } else {
          return [...prev, seat];
        }
      });
    }
  };

  const getSeatClass = (seat) => {
    if (!seat.is_available) return 'buying-scheme__chair_taken';
    if (selectedSeats.some(s => s.seat_id === seat.seat_id)) return 'buying-scheme__chair_selected';
    if (seat.seat_type === 'vip') return 'buying-scheme__chair_vip';
    return 'buying-scheme__chair_standart';
  };

  const calculateTotal = () => {
    return selectedSeats.reduce((sum, seat) => sum + seat.price, 0);
  };

  const handleBooking = async () => {
    if (selectedSeats.length === 0) {
      alert('Выберите места');
      return;
    }

    try {
      const response = await api.post(`/screenings/${screeningId}/book_seats/`, {
        seat_ids: selectedSeats.map(s => s.seat_id)
      });
      
      // Переходим на страницу оплаты с данными о бронировании
      navigate('/payment', { 
        state: { 
          bookings: response.data,
          screening: screening,
          total: calculateTotal()
        } 
      });
    } catch (error) {
      alert(error.response?.data?.error || 'Ошибка бронирования');
    }
  };

  if (loading) {
    return <div className="text-center py-20 text-2xl">Загрузка...</div>;
  }

  if (!screening) {
    return <div className="text-center py-20 text-2xl">Сеанс не найден</div>;
  }

  // Группируем места по рядам
  const seatsByRow = seats.reduce((acc, seat) => {
    if (!acc[seat.row]) acc[seat.row] = [];
    acc[seat.row].push(seat);
    return acc;
  }, {});

  return (
    <main>
      <section className="bg-white bg-opacity-95 pb-12">
        {/* Информация о сеансе */}
        <div className="flex justify-between items-center p-6">
          <div>
            <h2 className="text-xl font-bold">{screening.movie_details?.title}</h2>
            <p className="text-gray-600 my-2">
              Начало сеанса: {new Date(screening.start_time).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
            </p>
            <p className="font-bold">Зал {screening.hall_details?.name}</p>
          </div>
          <div className="text-center">
            <p className="relative w-40">
              Тапните дважды,<br />чтобы увеличить
            </p>
          </div>
        </div>

        {/* Схема зала */}
        <div className="bg-dark text-center py-6 px-12">
          <div className="inline-block bg-top bg-no-repeat bg-cover pt-12"
               style={{backgroundImage: 'url(/src/assets/screen.png)'}}>
            {Object.entries(seatsByRow).map(([row, rowSeats]) => (
              <div key={row} className="flex justify-center gap-1 my-1">
                {rowSeats.map(seat => (
                  <button
                    key={seat.seat_id}
                    onClick={() => toggleSeat(seat)}
                    className={`w-8 h-8 border border-gray-600 rounded transition-transform ${
                      getSeatClass(seat)
                    } ${selectedSeats.some(s => s.seat_id === seat.seat_id) ? 'scale-110' : ''}`}
                    disabled={!seat.is_available}
                  />
                ))}
              </div>
            ))}
          </div>

          {/* Легенда */}
          <div className="flex justify-center gap-16 text-white mt-8">
            <div>
              <p className="flex items-center gap-2">
                <span className="w-6 h-6 bg-white rounded border border-gray-600"></span>
                Свободно ({screening.price_standard} руб)
              </p>
              <p className="flex items-center gap-2 mt-2">
                <span className="w-6 h-6 bg-accent rounded border border-gray-600"></span>
                Свободно VIP ({screening.price_vip} руб)
              </p>
            </div>
            <div>
              <p className="flex items-center gap-2">
                <span className="w-6 h-6 bg-transparent rounded border border-gray-600"></span>
                Занято
              </p>
              <p className="flex items-center gap-2 mt-2">
                <span className="w-6 h-6 bg-primary rounded border border-gray-600 shadow-lg"></span>
                Выбрано
              </p>
            </div>
          </div>
        </div>

        {/* Кнопка бронирования */}
        <button
          onClick={handleBooking}
          className="block mx-auto mt-12 bg-primary text-white px-16 py-3 rounded shadow-lg uppercase font-medium hover:bg-opacity-90 transition"
        >
          Забронировать ({calculateTotal()} руб)
        </button>
      </section>
    </main>
  );
};

export default HallPage;