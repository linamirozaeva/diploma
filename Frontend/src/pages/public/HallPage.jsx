import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const HallPage = () => {
  const { screeningId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [notification, setNotification] = useState(null);
  const [screening, setScreening] = useState(null);
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bookingInProgress, setBookingInProgress] = useState(false);
  const [error, setError] = useState(null);

  // Функция для показа уведомлений
  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  // Загрузка данных о сеансе и местах
  useEffect(() => {
    const fetchScreeningData = async () => {
      if (!screeningId || screeningId === '_') {
        setError('Некорректный ID сеанса');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        console.log('Fetching screening with ID:', screeningId);
        
        // Получаем информацию о сеансе
        const screeningResponse = await api.get(`/screenings/${screeningId}/`);
        console.log('Screening data:', screeningResponse.data);
        setScreening(screeningResponse.data);
        
        // Получаем информацию о доступных местах
        const seatsResponse = await api.get(`/screenings/${screeningId}/available_seats/`);
        console.log('Seats data:', seatsResponse.data);
        setSeats(seatsResponse.data);
      } catch (error) {
        console.error('Error fetching screening:', error);
        if (error.response?.status === 404) {
          setError(`Сеанс с ID ${screeningId} не найден в базе данных. Создайте сеанс в админке.`);
        } else {
          setError('Не удалось загрузить информацию о сеансе');
        }
        showNotification('Ошибка загрузки данных сеанса', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchScreeningData();
  }, [screeningId]);

  // Проверка авторизации при попытке бронирования
  useEffect(() => {
    if (selectedSeats.length > 0 && !isAuthenticated) {
      localStorage.setItem('pendingBooking', JSON.stringify({
        screeningId,
        selectedSeats: selectedSeats.map(s => s.seat_id),
        total: calculateTotal()
      }));
      
      showNotification('Для бронирования необходимо войти в систему', 'info');
      
      navigate('/login', { 
        state: { from: `/hall/${screeningId}` }
      });
    }
  }, [selectedSeats, isAuthenticated, navigate, screeningId]);

  // Переключение выбора места
  const toggleSeat = (seat) => {
    if (!seat.is_available) return;

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
    const baseClass = 'buying-scheme__chair ';
    
    if (!seat.is_available) {
      return baseClass + 'buying-scheme__chair_taken';
    }
    
    const isSelected = selectedSeats.some(s => s.seat_id === seat.seat_id);
    if (isSelected) {
      return baseClass + 'buying-scheme__chair_selected';
    }
    
    if (seat.seat_type === 'vip') {
      return baseClass + 'buying-scheme__chair_vip';
    }
    
    return baseClass + 'buying-scheme__chair_standart';
  };

  // Подсчет общей стоимости
  const calculateTotal = () => {
    return selectedSeats.reduce((sum, seat) => sum + seat.price, 0);
  };

  // Обработка бронирования
  const handleBooking = async () => {
    if (selectedSeats.length === 0) {
      showNotification('Выберите места для бронирования', 'error');
      return;
    }

    if (!isAuthenticated) {
      showNotification('Необходимо войти в систему', 'info');
      navigate('/login', { state: { from: `/hall/${screeningId}` } });
      return;
    }

    setBookingInProgress(true);
    setError(null);

    try {
      const response = await api.post(`/screenings/${screeningId}/book_seats/`, {
        seat_ids: selectedSeats.map(s => s.seat_id)
      });
      
      showNotification('Места успешно забронированы!', 'success');
      
      navigate('/payment', { 
        state: { 
          bookings: response.data,
          screening: screening,
          total: calculateTotal()
        } 
      });
    } catch (error) {
      console.error('Booking error:', error);
      
      if (error.response?.status === 401) {
        showNotification('Сессия истекла. Войдите снова', 'error');
        navigate('/login', { state: { from: `/hall/${screeningId}` } });
      } else if (error.response?.status === 400) {
        const errorData = error.response.data;
        let errorMessage = 'Ошибка бронирования';
        
        if (typeof errorData === 'object') {
          errorMessage = Object.keys(errorData).map(key => 
            `${key}: ${Array.isArray(errorData[key]) ? errorData[key].join(', ') : errorData[key]}`
          ).join('\n');
        } else {
          errorMessage = errorData.error || 'Некоторые места уже заняты';
        }
        
        showNotification(errorMessage, 'error');
        
        // Обновляем данные о местах
        const seatsResponse = await api.get(`/screenings/${screeningId}/available_seats/`);
        setSeats(seatsResponse.data);
        setSelectedSeats([]);
      } else {
        showNotification('Произошла ошибка при бронировании', 'error');
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
        <div className="text-center bg-white bg-opacity-95 p-8 rounded-lg max-w-md">
          <p className="text-2xl text-red-600 mb-4">⚠️ Ошибка</p>
          <p className="text-gray-700 mb-4">{error || 'Сеанс не найден'}</p>
          <p className="text-sm text-gray-500 mb-4">ID сеанса: {screeningId}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-opacity-90 transition w-full"
          >
            Вернуться на главную
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="relative">
      {/* Уведомление */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg ${
          notification.type === 'success' ? 'bg-green-500' :
          notification.type === 'error' ? 'bg-red-500' :
          'bg-blue-500'
        } text-white`}>
          <div className="flex items-center gap-3">
            <span className="text-xl">
              {notification.type === 'success' ? '✅' :
               notification.type === 'error' ? '❌' : 'ℹ️'}
            </span>
            <span className="font-medium">{notification.message}</span>
            <button 
              onClick={() => setNotification(null)}
              className="ml-4 text-white hover:text-gray-200"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <section className="buying">
        {/* Информация о сеансе */}
        <div className="buying__info">
          <div className="buying__info-description">
            <h2 className="buying__info-title">{screening.movie_details?.title}</h2>
            <p className="buying__info-start">
              Начало сеанса: {new Date(screening.start_time).toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
            <p className="buying__info-hall">Зал {screening.hall_details?.name}</p>
          </div>
          
          {/* Иконка-подсказка из CSS */}
          <div className="buying__info-hint">
            <p>Тапните дважды,<br />чтобы увеличить</p>
          </div>
        </div>

        {/* Схема зала */}
        <div className="buying-scheme">
          <div className="buying-scheme__wrapper">
            {/* Экран уже есть в CSS как background-image */}
            
            {/* Места */}
            {sortedRows.map(rowNum => (
              <div key={rowNum} className="buying-scheme__row">
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
            ))}
          </div>

          {/* Легенда из CSS */}
          <div className="buying-scheme__legend">
            <div className="col">
              <p className="buying-scheme__legend-price">
                <span className="buying-scheme__chair buying-scheme__chair_standart"></span>
                Свободно ({screening.price_standard} руб)
              </p>
              <p className="buying-scheme__legend-price">
                <span className="buying-scheme__chair buying-scheme__chair_vip"></span>
                Свободно VIP ({screening.price_vip} руб)
              </p>
            </div>
            <div className="col">
              <p className="buying-scheme__legend-price">
                <span className="buying-scheme__chair buying-scheme__chair_taken"></span>
                Занято
              </p>
              <p className="buying-scheme__legend-price">
                <span className="buying-scheme__chair buying-scheme__chair_selected"></span>
                Выбрано
              </p>
            </div>
          </div>
        </div>

        {/* Информация о выбранных местах */}
        {selectedSeats.length > 0 && (
          <div className="max-w-4xl mx-auto mt-6 p-4 bg-primary bg-opacity-20 rounded-lg">
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

        {/* Кнопка бронирования */}
        <button
          onClick={handleBooking}
          disabled={selectedSeats.length === 0 || bookingInProgress}
          className="acceptin-button"
        >
          {bookingInProgress ? (
            <span className="flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Обработка...
            </span>
          ) : (
            `Забронировать ${calculateTotal() > 0 ? `за ${calculateTotal()} ₽` : ''}`
          )}
        </button>
        
        {!isAuthenticated && selectedSeats.length > 0 && (
          <p className="text-center text-sm text-red-600 mt-2">
            Для бронирования необходимо войти в систему
          </p>
        )}
      </section>
    </main>
  );
};

export default HallPage;