import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import api from '../../services/api';

const TicketPage = () => {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBooking();
  }, [bookingId]);

  const fetchBooking = async () => {
    try {
      const response = await api.get(`/bookings/${bookingId}/`);
      setBooking(response.data);
    } catch (error) {
      console.error('Error fetching booking:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-2xl">Загрузка билета...</div>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-3xl mb-4">Билет не найден</h2>
        <button
          onClick={() => navigate('/')}
          className="text-primary hover:underline"
        >
          Вернуться на главную
        </button>
      </div>
    );
  }

  // Формируем данные для QR-кода
  const qrData = JSON.stringify({
    code: booking.booking_code,
    movie: booking.screening_details?.movie_title,
    hall: booking.screening_details?.hall_name,
    row: booking.seat_details?.row,
    seat: booking.seat_details?.number,
    time: booking.screening_details?.start_time,
  });

  return (
    <main>
      <section className="ticket">
        <header className="tichet__check">
          <h2 className="ticket__check-title">Электронный билет</h2>
        </header>
        
        <div className="ticket__info-wrapper">
          <p className="ticket__info">
            На фильм: <span className="ticket__details ticket__title">{booking.screening_details?.movie_title}</span>
          </p>
          
          <p className="ticket__info">
            Места: <span className="ticket__details ticket__chairs">
              Ряд {booking.seat_details?.row}, Место {booking.seat_details?.number}
            </span>
          </p>
          
          <p className="ticket__info">
            В зале: <span className="ticket__details ticket__hall">{booking.screening_details?.hall_name}</span>
          </p>
          
          <p className="ticket__info">
            Начало сеанса: <span className="ticket__details ticket__start">
              {new Date(booking.screening_details?.start_time).toLocaleString('ru-RU', {
                day: 'numeric',
                month: 'long',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </p>
          
          <p className="ticket__info">
            Стоимость: <span className="ticket__details ticket__cost">{booking.price}</span> рублей
          </p>

          {/* QR-код */}
          <div className="flex justify-center mb-8">
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

          {/* Кнопки действий */}
          <div className="flex gap-4 mt-8">
            <button
              onClick={handlePrint}
              className="flex-1 bg-gray-200 text-gray-800 py-3 px-6 rounded-lg hover:bg-gray-300 transition"
            >
              Распечатать
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex-1 bg-primary text-white py-3 px-6 rounded-lg hover:bg-opacity-90 transition"
            >
              На главную
            </button>
          </div>
        </div>
      </section>
    </main>
  );
};

export default TicketPage;