import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../../services/api';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    movies: 0,
    halls: 0,
    screenings: 0,
    bookings: 0,
    todayBookings: 0,
    revenue: 0,
  });
  const [loading, setLoading] = useState(true);
  const [recentBookings, setRecentBookings] = useState([]);
  const { setNotification } = useOutletContext();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [movies, halls, screenings, bookings] = await Promise.all([
        api.get('/movies/'),
        api.get('/cinemas/halls/'),
        api.get('/screenings/'),
        api.get('/bookings/'),
      ]);

      // Расчет статистики
      const today = new Date().toISOString().split('T')[0];
      const todayBookings = bookings.data.filter(b => 
        b.created_at?.startsWith(today)
      ).length;

      const revenue = bookings.data
        .filter(b => b.status === 'confirmed')
        .reduce((sum, b) => sum + (b.price || 0), 0);

      setStats({
        movies: movies.data.length,
        halls: halls.data.length,
        screenings: screenings.data.length,
        bookings: bookings.data.length,
        todayBookings,
        revenue,
      });

      // Последние 5 бронирований
      setRecentBookings(bookings.data.slice(0, 5));
    } catch (error) {
      setNotification({
        message: 'Ошибка загрузки статистики',
        type: 'error'
      });
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
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const statsCards = [
    { title: 'Фильмы', value: stats.movies, icon: '🎬', color: 'bg-blue-500' },
    { title: 'Залы', value: stats.halls, icon: '🏛️', color: 'bg-green-500' },
    { title: 'Сеансы', value: stats.screenings, icon: '🎪', color: 'bg-purple-500' },
    { title: 'Бронирования', value: stats.bookings, icon: '🎫', color: 'bg-orange-500' },
    { title: 'Сегодня', value: stats.todayBookings, icon: '📅', color: 'bg-pink-500' },
    { title: 'Выручка', value: `${stats.revenue} ₽`, icon: '💰', color: 'bg-yellow-500' },
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-8">Панель управления</h2>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {statsCards.map((card, index) => (
          <div key={index} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition">
            <div className={`${card.color} p-4`}>
              <div className="flex items-center justify-between">
                <span className="text-4xl text-white">{card.icon}</span>
                <span className="text-3xl font-bold text-white">{card.value}</span>
              </div>
            </div>
            <div className="p-4">
              <h3 className="text-lg font-semibold text-gray-700">{card.title}</h3>
            </div>
          </div>
        ))}
      </div>

      {/* Быстрые действия и последние бронирования */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">Быстрые действия</h3>
          <div className="space-y-3">
            <button 
              onClick={() => window.location.href = '/admin/movies'}
              className="w-full text-left px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition flex items-center gap-3"
            >
              <span className="text-2xl">🎬</span>
              <div>
                <div className="font-semibold">Добавить фильм</div>
                <div className="text-sm text-gray-600">Новый фильм в репертуар</div>
              </div>
            </button>
            <button 
              onClick={() => window.location.href = '/admin/screenings'}
              className="w-full text-left px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition flex items-center gap-3"
            >
              <span className="text-2xl">⏰</span>
              <div>
                <div className="font-semibold">Создать сеанс</div>
                <div className="text-sm text-gray-600">Добавить время показа</div>
              </div>
            </button>
            <button 
              onClick={() => window.location.href = '/admin/halls'}
              className="w-full text-left px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition flex items-center gap-3"
            >
              <span className="text-2xl">🏛️</span>
              <div>
                <div className="font-semibold">Настроить зал</div>
                <div className="text-sm text-gray-600">Изменить схему мест</div>
              </div>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">Последние бронирования</h3>
          {recentBookings.length > 0 ? (
            <div className="space-y-3">
              {recentBookings.map(booking => (
                <div key={booking.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-semibold">{booking.screening_details?.movie_title || 'Фильм'}</div>
                    <div className="text-sm text-gray-600">
                      {booking.user_details?.username || 'Гость'} • {formatDateTime(booking.created_at)}
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    booking.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {booking.status === 'confirmed' ? '✓' : '•'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">Нет последних бронирований</p>
          )}
          <button 
            onClick={() => window.location.href = '/admin/bookings'}
            className="w-full mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-opacity-90 transition"
          >
            Все бронирования
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;