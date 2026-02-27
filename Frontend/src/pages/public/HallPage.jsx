import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOutletContext } from 'react-router-dom';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const HallPage = () => {
  const { screeningId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { setNotification } = useOutletContext();
  
  const [screening, setScreening] = useState(null);
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bookingInProgress, setBookingInProgress] = useState(false);
  const [error, setError] = useState(null);

  // Загрузка данных о сеансе и местах
  useEffect(() => {
    const fetchScreeningData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Получаем информацию о сеансе
        const screeningResponse = await api.get(`/screenings/${screeningId}/`);
        setScreening(screeningResponse.data);
        
        // Получаем информацию о доступных местах
        const seatsResponse = await api.get(`/screenings/${screeningId}/available-seats/`);
        setSeats(seatsResponse.data);
      } catch (error) {
        console.error('Error fetching screening:', error);
        setError('Не удалось загрузить информацию о сеансе');
        setNotification({
          message: 'Ошибка загрузки данных сеанса',
          type: 'error'
        });
      } finally {
        setLoading(false);
      }
    };

    if (screeningId) {
      fetchScreeningData();
    }
  }, [screeningId, setNotification]);

  // Проверка авторизации при попытке бронирования
  useEffect(() => {
    if (selectedSeats.length > 0 && !isAuthenticated) {
      // Сохраняем выбранные места в localStorage и перенаправляем на логин
      localStorage.setItem('pendingBooking', JSON.stringify({
        screeningId,
        selectedSeats: selectedSeats.map(s => s.seat_id),
        total: calculateTotal()
      }));
      
      setNotification({
        message: 'Для бронирования необходимо войти в систему',
        type: 'info'
      });
      
      navigate('/login', { 
        state: { from: `/hall/${screeningId}` }
      });
    }
  }, [selectedSeats, isAuthenticated, navigate, screeningId, setNotification]);

  // Переключение выбора места
  const toggleSeat = (seat) => {
    if (!seat.is_available) return; // Нельзя выбрать занятое место

    setSelectedSeats(prev => {
      const isSelected = prev.some(s => s.seat_id === seat.seat_id);
      if (isSelected) {
        return prev.filter(s => s.seat_id !== seat.seat_id);
      } else {
        return [...prev, seat];
      }
    });
  };

  // Получение CSS класса для места
  const getSeatClass = (seat) => {
    const baseClass = 'w-8 h-8 border rounded transition-all duration-200 ';
    
    if (!seat.is_available) {
      return baseClass + 'bg-gray-600 border-gray-700 cursor-not-allowed opacity-50';
    }
    
    const isSelected = selectedSeats.some(s => s.seat_id === seat.seat_id);
    if (isSelected) {
      return baseClass + 'bg-primary border-primary scale-110 shadow-lg shadow-primary/50';
    }
    
    if (seat.seat_type === 'vip') {
      return baseClass + 'bg-accent border-accent hover:scale-105 hover:shadow-md hover:shadow-accent/50';
    }
    
    return baseClass + 'bg-white border-gray-400 hover:scale-105 hover:shadow-md hover:border-primary';
  };

  // Подсчет общей стоимости
  const calculateTotal = () => {
    return selectedSeats.reduce((sum, seat) => sum + seat.price, 0);
  };

  // Обработка бронирования
  const handleBooking = async () => {
    if (selectedSeats.length === 0) {
      setNotification({
        message: 'Выберите места для бронирования',
        type: 'error'
      });
      return;
    }

    if (!isAuthenticated) {
      setNotification({
        message: 'Необходимо войти в систему',
        type: 'info'
      });
      navigate('/login', { state: { from: `/hall/${screeningId}` } });
      return;
    }

    setBookingInProgress(true);
    setError(null);

    try {
      const response = await api.post(`/screenings/${screeningId}/book-seats/`, {
        seat_ids: selectedSeats.map(s => s.seat_id)
      });
      
      setNotification({
        message: 'Места успешно забронированы!',
        type: 'success'
      });
      
      navigate('/payment', { 
        state: { 
          bookings: response.data,
          screening: screening,
          total: calculateTotal()
        } 
      });
    } catch (error) {
      console.error('Booking error:', error);
      
      // Обработка различных ошибок
      if (error.response?.status === 401) {
        setNotification({
          message: 'Сессия истекла. Войдите снова',
          type: 'error'
        });
        navigate('/login', { state: { from: `/hall/${screeningId}` } });
      } else if (error.response?.status === 400) {
        const errorData = error.response.data;
        let errorMessage = 'Ошибка бронирования:\n';
        
        if (typeof errorData === 'object') {
          Object.keys(errorData).forEach(key => {
            errorMessage += `${key}: ${Array.isArray(errorData[key]) ? errorData[key].join(', ') : errorData[key]}\n`;
          });
        } else {
          errorMessage = errorData.error || 'Некоторые места уже заняты';
        }
        
        setNotification({
          message: errorMessage,
          type: 'error'
        });
        
        // Обновляем данные о местах
        const seatsResponse = await api.get(`/screenings/${screeningId}/available-seats/`);
        setSeats(seatsResponse.data);
        setSelectedSeats([]);
      } else {
        setNotification({
          message: 'Произошла ошибка при бронировании',
          type: 'error'
        });
      }
    } finally {
      setBookingInProgress(false);
    }
  };

  // Группировка мест по рядам
  const seatsByRow = seats.reduce((acc, seat) => {
    if (!acc[seat.row]) acc[seat.row] = [];
    acc[seat.row].push(seat);
    return acc;
  }, {});

  // Сортировка рядов
  const sortedRows = Object.keys(seatsByRow).sort((a, b) => parseInt(a) - parseInt(b));

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Загрузка схемы зала...</p>
        </div>
      </div>
    );
  }

  if (error || !screening) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center bg-white bg-opacity-95 p-8 rounded-lg">
          <p className="text-2xl text-red-600 mb-4">⚠️ {error || 'Сеанс не найден'}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-opacity-90 transition"
          >
            Вернуться на главную
          </button>
        </div>
      </div>
    );
  }

  return (
    <main>
      <section className="bg-white bg-opacity-95 pb-12">
        {/* Информация о сеансе */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center p-6 border-b">
          <div>
            <h2 className="text-2xl md:text-3xl font-bold mb-2">{screening.movie_details?.title}</h2>
            <div className="flex flex-wrap gap-4 text-gray-600">
              <p>
                <span className="font-semibold">Начало:</span>{' '}
                {new Date(screening.start_time).toLocaleString('ru-RU', {
                  day: 'numeric',
                  month: 'long',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
              <p>
                <span className="font-semibold">Зал:</span> {screening.hall_details?.name}
              </p>
              <p>
                <span className="font-semibold">Длительность:</span> {screening.movie_details?.duration} мин
              </p>
            </div>
          </div>
          
          {/* Подсказка */}
          <div className="mt-4 md:mt-0 bg-gray-100 p-3 rounded-lg">
            <p className="text-sm text-gray-600 flex items-center gap-2">
              <span className="text-2xl">👆</span>
              <span>Нажмите на место для выбора</span>
            </p>
          </div>
        </div>

        {/* Схема зала */}
        <div className="bg-dark py-8 px-4">
          <div className="max-w-4xl mx-auto">
            {/* Экран */}
            <div className="text-center mb-8">
              <div className="w-full h-2 bg-gradient-to-b from-gray-400 to-transparent rounded-t-lg"></div>
              <p className="text-white text-sm mt-1">ЭКРАН</p>
            </div>
            
            {/* Места */}
            <div className="bg-dark-light rounded-lg p-6 overflow-x-auto">
              {sortedRows.map(rowNum => (
                <div key={rowNum} className="flex justify-center items-center gap-1 mb-2">
                  <span className="text-white text-xs w-6 text-right mr-2">Ряд {rowNum}</span>
                  <div className="flex flex-wrap justify-center gap-1">
                    {seatsByRow[rowNum]
                      .sort((a, b) => a.number - b.number)
                      .map(seat => (
                        <button
                          key={seat.seat_id}
                          onClick={() => toggleSeat(seat)}
                          disabled={!seat.is_available || bookingInProgress}
                          className={getSeatClass(seat)}
                          title={`Ряд ${seat.row}, Место ${seat.number} - ${seat.seat_type === 'vip' ? 'VIP' : 'Обычное'} - ${seat.price}₽`}
                        />
                      ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Легенда */}
            <div className="flex flex-wrap justify-center gap-6 md:gap-12 text-white mt-8">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-white border border-gray-400 rounded"></span>
                <span>Обычное ({screening.price_standard} ₽)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-accent border border-accent rounded"></span>
                <span>VIP ({screening.price_vip} ₽)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-gray-600 border border-gray-700 rounded opacity-50"></span>
                <span>Занято</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-primary border border-primary rounded shadow-lg shadow-primary/50"></span>
                <span>Выбрано</span>
              </div>
            </div>

            {/* Информация о выбранных местах */}
            {selectedSeats.length > 0 && (
              <div className="mt-6 p-4 bg-primary bg-opacity-20 rounded-lg">
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                  <div>
                    <p className="text-white font-semibold">Выбрано мест: {selectedSeats.length}</p>
                    <p className="text-white">
                      {selectedSeats.map(s => `${s.row}-${s.number}`).join(', ')}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-white text-2xl font-bold">{calculateTotal()} ₽</p>
                    <p className="text-white text-sm">Общая стоимость</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Кнопка бронирования */}
        <div className="text-center mt-8">
          <button
            onClick={handleBooking}
            disabled={selectedSeats.length === 0 || bookingInProgress}
            className={`px-8 py-4 text-lg font-bold rounded-lg transition ${
              selectedSeats.length === 0 || bookingInProgress
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-primary hover:bg-opacity-90 transform hover:scale-105'
            } text-white shadow-lg`}
          >
            {bookingInProgress ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Обработка...
              </span>
            ) : (
              `Забронировать ${calculateTotal() > 0 ? `за ${calculateTotal()} ₽` : ''}`
            )}
          </button>
          
          {!isAuthenticated && selectedSeats.length > 0 && (
            <p className="text-sm text-red-600 mt-2">
              Для бронирования необходимо войти в систему
            </p>
          )}
        </div>
      </section>
    </main>
  );
};

export default HallPage;