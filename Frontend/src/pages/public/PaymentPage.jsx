import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const PaymentPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);

  // Получаем данные из состояния навигации
  const { bookings = [], screening = null, total = 0 } = location.state || {};

  console.log('Payment page state:', location.state);

  if (!screening || bookings.length === 0) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-3xl mb-4 text-white">Нет данных о бронировании</h2>
        <p className="text-gray-300 mb-4">Попробуйте выбрать места заново</p>
        <button
          onClick={() => navigate('/')}
          className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-opacity-90 transition"
        >
          На главную
        </button>
      </div>
    );
  }

  const handleGetCode = async () => {
    setProcessing(true);
    
    // Имитация получения кода бронирования
    setTimeout(() => {
      navigate(`/ticket/${bookings[0].id}`, {
        state: { booking: bookings[0] }
      });
    }, 1000);
  };

  // Форматируем места для отображения
  const formatSeats = () => {
    if (bookings.length === 0) return '';
    
    if (bookings[0].seat_details) {
      return bookings.map(b => 
        `Ряд ${b.seat_details.row}, Место ${b.seat_details.number}`
      ).join('; ');
    }
    
    return bookings.map(b => b.seat || b).join(', ');
  };

  return (
    <main>
      <section className="ticket" style={{ maxWidth: '600px', margin: '2rem auto' }}>
        
        <header className="tichet__check">
          <h2 className="ticket__check-title">Вы выбрали билеты:</h2>
        </header>
        
        <div className="ticket__info-wrapper">
          <p className="ticket__info">
            На фильм: <span className="ticket__details ticket__title">
              {screening.movie_details?.title || screening.movie_title}
            </span>
          </p>
          
          <p className="ticket__info">
            Места: <span className="ticket__details ticket__chairs">
              {formatSeats()}
            </span>
          </p>
          
          <p className="ticket__info">
            В зале: <span className="ticket__details ticket__hall">
              {screening.hall_details?.name || screening.hall_name}
            </span>
          </p>
          
          <p className="ticket__info">
            Начало сеанса: <span className="ticket__details ticket__start">
              {new Date(screening.start_time).toLocaleString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit',
                day: 'numeric',
                month: 'long'
              })}
            </span>
          </p>
          
          <p className="ticket__info">
            Стоимость: <span className="ticket__details ticket__cost">{total}</span> рублей
          </p>

          <button 
            className="acceptin-button" 
            onClick={handleGetCode}
            disabled={processing}
            style={{ marginTop: '2rem' }}
          >
            {processing ? 'Обработка...' : 'Получить код бронирования'}
          </button>

          <p className="ticket__hint">
            После оплаты билет будет доступен в этом окне, а также придёт вам на почту. Покажите QR-код нашему контроллёру у входа в зал.
          </p>
          <p className="ticket__hint">
            Приятного просмотра!
          </p>
        </div>
      </section>     
    </main>
  );
};

export default PaymentPage;