import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import api from '../../services/api';

const AdminBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
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
        message: 'Ошибка загрузки бронирований: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancelBooking = async (id) => {
    if (window.confirm('Вы уверены, что хотите отменить это бронирование?')) {
      try {
        await api.patch(`/bookings/${id}/`, { status: 'cancelled' });
        setNotification({ message: 'Бронирование отменено', type: 'success' });
        fetchBookings();
      } catch (error) {
        setNotification({
          message: 'Ошибка отмены: ' + (error.response?.data?.detail || error.message),
          type: 'error'
        });
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

  // Фильтрация
  const filteredBookings = bookings.filter(booking => {
    const matchesSearch = 
      booking.booking_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.user_details?.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.screening_details?.movie_title?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || booking.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  // Пагинация
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredBookings.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredBookings.length / itemsPerPage);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">Управление бронированиями</h2>

      {/* Фильтры и поиск */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div className="flex-1 min-w-[300px]">
          <input
            type="text"
            placeholder="🔍 Поиск по коду, пользователю или фильму..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div className="w-48">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="all">Все статусы</option>
            <option value="confirmed">Подтвержденные</option>
            <option value="cancelled">Отмененные</option>
          </select>
        </div>
      </div>

      {/* Таблица бронирований */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Код
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Пользователь
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Фильм
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Место
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Время
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                QR-код
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {currentItems.map(booking => (
              <tr key={booking.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-mono">
                  {booking.booking_code || '—'}
                </td>
                <td className="px-6 py-4">
                  {booking.user_details?.username || 'Гость'}
                </td>
                <td className="px-6 py-4">
                  {booking.screening_details?.movie_title || '—'}
                </td>
                <td className="px-6 py-4">
                  {booking.seat_details ? 
                    `Ряд ${booking.seat_details.row}, Место ${booking.seat_details.number}` : 
                    '—'}
                </td>
                <td className="px-6 py-4">
                  {formatDateTime(booking.screening_details?.start_time)}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    booking.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                    booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {booking.status === 'confirmed' ? 'Подтверждено' :
                     booking.status === 'cancelled' ? 'Отменено' :
                     booking.status || '—'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => setSelectedBooking(booking)}
                    className="text-primary hover:text-opacity-80 transition"
                    title="Показать QR-код"
                  >
                    🖼️ QR
                  </button>
                </td>
                <td className="px-6 py-4">
                  {booking.status === 'confirmed' && (
                    <button
                      onClick={() => handleCancelBooking(booking.id)}
                      className="text-red-600 hover:text-red-900 transition text-sm"
                      title="Отменить бронирование"
                    >
                      Отменить
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Информация о пустом списке */}
        {filteredBookings.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Бронирования не найдены
          </div>
        )}

        {/* Пагинация */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-4 py-4 border-t">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-300 transition"
            >
              ← Назад
            </button>
            <span className="text-gray-600">
              Страница {currentPage} из {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-300 transition"
            >
              Вперед →
            </button>
          </div>
        )}
      </div>

      {/* Модальное окно с QR-кодом */}
      {selectedBooking && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">QR-код бронирования</h3>
              <button
                onClick={() => setSelectedBooking(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="flex justify-center mb-4">
              <QRCodeSVG
                value={JSON.stringify({
                  code: selectedBooking.booking_code,
                  movie: selectedBooking.screening_details?.movie_title,
                  hall: selectedBooking.screening_details?.hall_name,
                  row: selectedBooking.seat_details?.row,
                  seat: selectedBooking.seat_details?.number,
                  time: selectedBooking.screening_details?.start_time,
                })}
                size={200}
                level="H"
                className="border-2 border-gray-300 p-2"
              />
            </div>

            <div className="space-y-2 text-sm">
              <p><span className="font-bold">Код:</span> {selectedBooking.booking_code}</p>
              <p><span className="font-bold">Фильм:</span> {selectedBooking.screening_details?.movie_title}</p>
              <p><span className="font-bold">Место:</span> Ряд {selectedBooking.seat_details?.row}, Место {selectedBooking.seat_details?.number}</p>
              <p><span className="font-bold">Время:</span> {formatDateTime(selectedBooking.screening_details?.start_time)}</p>
            </div>

            <button
              onClick={() => setSelectedBooking(null)}
              className="w-full bg-primary text-white py-2 px-4 rounded hover:bg-opacity-90 transition mt-4"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminBookings;