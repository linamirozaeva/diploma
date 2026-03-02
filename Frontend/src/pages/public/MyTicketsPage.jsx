import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const MyTicketsPage = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchBookings();
  }, [isAuthenticated, navigate]);

  const fetchBookings = async () => {
    try {
      const response = await api.get('/bookings/my_bookings/');
      
      if (Array.isArray(response.data)) {
        setBookings(response.data);
      } else if (response.data && Array.isArray(response.data.bookings)) {
        setBookings(response.data.bookings);
      } else {
        setBookings([]);
      }
    } catch (error) {
      console.error('Error fetching bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusText = (status) => {
    switch(status) {
      case 'confirmed': return 'Подтверждено';
      case 'cancelled': return 'Отменено';
      case 'used': return 'Использовано';
      default: return status || 'Неизвестно';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary"></div>
      </div>
    );
  }

  const bookingsArray = Array.isArray(bookings) ? bookings : [];

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-white">Мои билеты</h1>

      {bookingsArray.length === 0 ? (
        <div className="max-w-2xl mx-auto">
          <section className="ticket">
            <header className="tichet__check">
              <h2 className="ticket__check-title">Нет билетов</h2>
            </header>
            <div className="ticket__info-wrapper text-center">
              <p className="ticket__info">У вас пока нет забронированных билетов</p>
              <Link to="/" className="acceptin-button inline-block mt-4">
                Купить билеты
              </Link>
            </div>
          </section>
        </div>
      ) : (
        <div className="space-y-6">
          {bookingsArray.map((booking) => {
            const movieTitle = booking.movie_details?.title || 
                              booking.screening_details?.movie_title || 
                              booking.movie_title ||
                              'Фильм';
            const hallName = booking.hall_details?.name || 
                            booking.screening_details?.hall_name || 
                            booking.hall_name ||
                            'Зал';
            const seatRow = booking.seat_details?.row || booking.row || '—';
            const seatNumber = booking.seat_details?.number || booking.number || '—';
            const startTime = booking.screening_details?.start_time || booking.start_time;
            const price = booking.price || 0;
            const status = booking.status || 'confirmed';
            
            // Формируем данные для QR-кода
            const qrData = JSON.stringify({
              code: booking.booking_code,
              movie: movieTitle,
              hall: hallName,
              row: seatRow,
              seat: seatNumber,
              time: startTime,
            });

            return (
              <div key={booking.id} className="max-w-2xl mx-auto">
                <section className="ticket">
                  <header className="tichet__check">
                    <h2 className="ticket__check-title">Электронный билет</h2>
                  </header>
                  
                  <div className="ticket__info-wrapper">
                    <p className="ticket__info">
                      На фильм: <span className="ticket__details ticket__title">{movieTitle}</span>
                    </p>
                    
                    <p className="ticket__info">
                      Места: <span className="ticket__details ticket__chairs">
                        Ряд {seatRow}, Место {seatNumber}
                      </span>
                    </p>
                    
                    <p className="ticket__info">
                      В зале: <span className="ticket__details ticket__hall">{hallName}</span>
                    </p>
                    
                    <p className="ticket__info">
                      Начало сеанса: <span className="ticket__details ticket__start">
                        {formatDateTime(startTime)}
                      </span>
                    </p>
                    
                    <p className="ticket__info">
                      Статус: <span className="ticket__details">
                        {getStatusText(status)}
                      </span>
                    </p>
                    
                    <p className="ticket__info">
                      Стоимость: <span className="ticket__details ticket__cost">{price}</span> рублей
                    </p>

                    {/* QR-код */}
                    <div className="flex justify-center my-6">
                      <QRCodeSVG
                        value={qrData}
                        size={200}
                        level="H"
                        includeMargin={true}
                        className="ticket__info-qr"
                      />
                    </div>

                    {/* Подсказки */}
                    <p className="ticket__hint">
                      Покажите QR-код нашему контроллеру для подтверждения бронирования.
                    </p>
                    <p className="ticket__hint">
                      Приятного просмотра!
                    </p>

                    {/* Кнопка для возврата (опционально) */}
                    <div className="text-center mt-6">
                      <Link to="/" className="text-primary hover:underline">
                        ← На главную
                      </Link>
                    </div>
                  </div>
                </section>
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
};

export default MyTicketsPage;