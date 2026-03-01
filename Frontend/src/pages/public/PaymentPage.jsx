import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const PaymentPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);

  console.log('Payment page state:', location.state);

  // Получаем данные из состояния навигации
  const { bookings = [], screening = null, total = 0 } = location.state || {};

  if (!screening || bookings.length === 0) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-3xl mb-4">Нет данных о бронировании</h2>
        <p className="text-gray-300 mb-4">Попробуйте выбрать места заново</p>
        <button
          onClick={() => navigate('/')}
          className="text-primary hover:underline"
        >
          Вернуться на главную
        </button>
      </div>
    );
  }

  const handlePayment = async () => {
    setProcessing(true);
    
    // Имитация обработки платежа
    setTimeout(() => {
      // Переходим на страницу с билетами, передавая ID первого бронирования
      navigate(`/ticket/${bookings[0].id}`, {
        state: { booking: bookings[0] }
      });
    }, 2000);
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white bg-opacity-95 rounded-lg p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-orange-600 uppercase mb-4">
              Вы выбрали билеты:
            </h2>
          </div>

          {/* Информация о заказе */}
          <div className="space-y-4 mb-8">
            <p className="text-lg">
              На фильм:{' '}
              <span className="font-bold">{screening.movie_details?.title}</span>
            </p>
            
            <p className="text-lg">
              Места:{' '}
              <span className="font-bold">
                {bookings.map(b => 
                  `Ряд ${b.seat_details?.row} Место ${b.seat_details?.number}`
                ).join(', ')}
              </span>
            </p>
            
            <p className="text-lg">
              В зале:{' '}
              <span className="font-bold">{screening.hall_details?.name}</span>
            </p>
            
            <p className="text-lg">
              Начало сеанса:{' '}
              <span className="font-bold">
                {new Date(screening.start_time).toLocaleTimeString('ru-RU', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </p>
            
            <p className="text-lg">
              Стоимость:{' '}
              <span className="font-bold text-primary">{total}</span> рублей
            </p>
          </div>

          {/* Кнопка оплаты */}
          <button
            onClick={handlePayment}
            disabled={processing}
            className="w-full bg-primary text-white py-4 px-8 rounded-lg text-xl font-bold uppercase hover:bg-opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {processing ? 'Обработка платежа...' : 'Оплатить'}
          </button>

          {/* Подсказки */}
          <div className="mt-8 text-sm text-gray-600 space-y-2">
            <p>
              После оплаты билет будет доступен в этом окне, а также придёт вам на почту. 
              Покажите QR-код нашему контроллёру у входа в зал.
            </p>
            <p className="font-semibold">Приятного просмотра!</p>
          </div>
        </div>
      </div>
    </main>
  );
};

export default PaymentPage;