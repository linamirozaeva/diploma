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
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white bg-opacity-95 rounded-lg p-8 relative">
          {/* Декоративные полоски сверху */}
          <div className="absolute top-0 left-0 right-0 h-[3px] bg-repeat-x"
               style={{backgroundImage: 'url(/src/assets/border-top.png)'}}></div>

          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-orange-600 uppercase">
              Электронный билет
            </h2>
          </div>

          {/* Информация о билете */}
          <div className="space-y-4 mb-8">
            <p className="text-lg">
              На фильм:{' '}
              <span className="font-bold">{booking.screening_details?.movie_title}</span>
            </p>
            
            <p className="text-lg">
              Места:{' '}
              <span className="font-bold">
                Ряд {booking.seat_details?.row}, Место {booking.seat_details?.number}
              </span>
            </p>
            
            <p className="text-lg">
              В зале:{' '}
              <span className="font-bold">{booking.screening_details?.hall_name}</span>
            </p>
            
            <p className="text-lg">
              Начало сеанса:{' '}
              <span className="font-bold">
                {new Date(booking.screening_details?.start_time).toLocaleString('ru-RU', {
                  day: 'numeric',
                  month: 'long',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </p>
          </div>

          {/* ====================================================
              КАРТИНКА: QR-код (генерируется динамически)
              Не требует файла изображения, создается кодом
              Содержит: код бронирования, фильм, ряд, место, время
              ==================================================== */}
          <div className="flex justify-center mb-8">
            <QRCodeSVG
              value={qrData}
              size={200}
              level="H"
              includeMargin={true}
              className="border-2 border-gray-300 p-2"
            />
          </div>

          {/* Подсказки */}
          <div className="text-sm text-gray-600 space-y-2 text-center">
            <p>
              Покажите QR-код нашему контроллеру для подтверждения бронирования.
            </p>
            <p className="font-semibold">Приятного просмотра!</p>
          </div>

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

          {/* Декоративные полоски снизу */}
          <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-repeat-x"
               style={{backgroundImage: 'url(/src/assets/border-bottom.png)'}}></div>
        </div>
      </div>
    </main>
  );
};

export default TicketPage;