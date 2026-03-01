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
      setBookings(response.data);
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
      day: '2-digit',
      month: '2-digit',
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
      default: return status;
    }
  };

  const getStatusClass = (status) => {
    switch(status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'used': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Загрузка билетов...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8 relative z-10">
      <h1 className="text-3xl font-bold mb-8 text-white">Мои билеты</h1>

      {bookings.length === 0 ? (
        <div className="text-center py-12 bg-white bg-opacity-95 rounded-lg relative z-20">
          <p className="text-xl text-gray-600 mb-4">У вас пока нет билетов</p>
          <Link
            to="/"
            className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-opacity-90 transition inline-block"
          >
            Купить билеты
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 relative z-20">
          {bookings.map((booking) => {
            // Получаем данные из разных возможных структур ответа API
            const movieTitle = booking.movie_details?.title || 
                              booking.screening_details?.movie_title || 
                              'Фильм';
            const hallName = booking.hall_details?.name || 
                            booking.screening_details?.hall_name || 
                            'Зал';
            const seatRow = booking.seat_details?.row || '—';
            const seatNumber = booking.seat_details?.number || '—';
            const startTime = booking.screening_details?.start_time;
            const price = booking.price || 0;
            
            return (
              <div key={booking.id} className="bg-white bg-opacity-95 rounded-lg p-6 shadow-lg relative z-20 hover:shadow-xl transition">
                <div className="flex flex-col md:flex-row gap-6">
                  {/* QR-код */}
                  <div className="flex-shrink-0 flex justify-center md:justify-start">
                    <QRCodeSVG
                      value={JSON.stringify({
                        code: booking.booking_code,
                        movie: movieTitle,
                        row: seatRow,
                        seat: seatNumber,
                        time: startTime
                      })}
                      size={120}
                      level="H"
                      className="border-2 border-gray-300 p-1 rounded"
                    />
                  </div>

                  {/* Информация о билете */}
                  <div className="flex-grow">
                    <div className="flex flex-col md:flex-row justify-between items-start gap-4 mb-4">
                      <h3 className="text-xl font-bold">{movieTitle}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusClass(booking.status)}`}>
                        {getStatusText(booking.status)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                      <div className="bg-gray-50 p-3 rounded">
                        <p className="text-gray-500 text-xs mb-1">Код бронирования</p>
                        <p className="font-mono font-bold break-all">{booking.booking_code}</p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <p className="text-gray-500 text-xs mb-1">Зал</p>
                        <p className="font-bold">{hallName}</p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <p className="text-gray-500 text-xs mb-1">Ряд / Место</p>
                        <p className="font-bold">{seatRow} / {seatNumber}</p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <p className="text-gray-500 text-xs mb-1">Время сеанса</p>
                        <p className="font-bold">{formatDateTime(startTime)}</p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <p className="text-gray-500 text-xs mb-1">Стоимость</p>
                        <p className="font-bold">{price} ₽</p>
                      </div>
                    </div>
                  </div>

                  {/* Кнопка просмотра */}
                  <div className="flex-shrink-0 flex items-center justify-center md:justify-end">
                    <Link
                      to={`/ticket/${booking.id}`}
                      className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-opacity-90 transition text-center w-full md:w-auto"
                    >
                      Подробнее
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
};

export default MyTicketsPage;