import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import api from '../../services/api';
import AccordionSection from './components/AccordionSection';

const AdminBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const { setNotification } = useOutletContext();

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    try {
      const response = await api.get('/bookings/');
      setBookings(response.data);
    } catch (error) {
      setNotification({
        message: 'Ошибка загрузки бронирований',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancelBooking = async (id) => {
    if (window.confirm('Отменить бронирование?')) {
      try {
        await api.post(`/bookings/${id}/cancel/`);
        setNotification({ message: 'Бронирование отменено', type: 'success' });
        fetchBookings();
      } catch (error) {
        setNotification({ message: 'Ошибка отмены', type: 'error' });
      }
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

  const filteredBookings = bookings.filter(booking => {
    const matchesSearch = 
      booking.booking_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.user_details?.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.screening_details?.movie_title?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || booking.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return <div className="text-center py-20">Загрузка...</div>;
  }

  return (
    <>
      <AccordionSection title="Управление бронированиями" sectionNumber={1}>
        {/* Фильтры */}
        <div className="mb-6 flex gap-4">
          <input
            type="text"
            placeholder="Поиск по коду, пользователю, фильму..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-grow p-2 border rounded"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-48 p-2 border rounded"
          >
            <option value="all">Все статусы</option>
            <option value="confirmed">Подтвержденные</option>
            <option value="cancelled">Отмененные</option>
            <option value="used">Использованные</option>
          </select>
        </div>

        {/* Таблица бронирований */}
        <div className="bg-white rounded shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-3 text-left">Код</th>
                <th className="p-3 text-left">Пользователь</th>
                <th className="p-3 text-left">Фильм</th>
                <th className="p-3 text-left">Место</th>
                <th className="p-3 text-left">Время</th>
                <th className="p-3 text-left">Статус</th>
                <th className="p-3 text-left">QR</th>
                <th className="p-3 text-left">Действия</th>
              </tr>
            </thead>
            <tbody>
              {filteredBookings.map(booking => (
                <tr key={booking.id} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-mono">{booking.booking_code}</td>
                  <td className="p-3">{booking.user_details?.username || '—'}</td>
                  <td className="p-3">{booking.screening_details?.movie_title || '—'}</td>
                  <td className="p-3">
                    {booking.seat_details ? 
                      `Ряд ${booking.seat_details.row}, М. ${booking.seat_details.number}` : 
                      '—'}
                  </td>
                  <td className="p-3">{formatDateTime(booking.screening_details?.start_time)}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      booking.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                      booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                      booking.status === 'used' ? 'bg-gray-100 text-gray-800' :
                      'bg-gray-100'
                    }`}>
                      {booking.status === 'confirmed' ? 'Подтверждено' :
                       booking.status === 'cancelled' ? 'Отменено' :
                       booking.status === 'used' ? 'Использовано' : booking.status}
                    </span>
                  </td>
                  <td className="p-3">
                    <button
                      onClick={() => setSelectedBooking(booking)}
                      className="text-blue-600 hover:text-blue-800"
                      title="Показать QR-код"
                    >
                      QR
                    </button>
                  </td>
                  <td className="p-3">
                    {booking.status === 'confirmed' && (
                      <button
                        onClick={() => handleCancelBooking(booking.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Отменить
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AccordionSection>

      {/* Модальное окно с QR-кодом */}
      {selectedBooking && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-sm w-full">
            <h3 className="text-xl font-bold mb-4">QR-код бронирования</h3>
            
            <div className="flex justify-center mb-4">
              <QRCodeSVG
                value={JSON.stringify({
                  code: selectedBooking.booking_code,
                  movie: selectedBooking.screening_details?.movie_title,
                  row: selectedBooking.seat_details?.row,
                  seat: selectedBooking.seat_details?.number,
                })}
                size={200}
                level="H"
                className="border p-2"
              />
            </div>

            <p className="text-center mb-2">
              <span className="font-bold">Код:</span> {selectedBooking.booking_code}
            </p>
            <p className="text-center mb-4 text-sm text-gray-600">
              {selectedBooking.screening_details?.movie_title} - Ряд {selectedBooking.seat_details?.row}, Место {selectedBooking.seat_details?.number}
            </p>

            <button
              onClick={() => setSelectedBooking(null)}
              className="w-full bg-primary text-white py-2 rounded hover:bg-opacity-90"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default AdminBookings;