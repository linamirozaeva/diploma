import React, { useState, useEffect } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import api from '../../services/api';
import AccordionSection from './components/AccordionSection';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    movies: 0,
    halls: 0,
    screenings: 0,
    bookings: 0,
    revenue: 0,
    todayBookings: 0
  });
  const [loading, setLoading] = useState(true);
  const [recentBookings, setRecentBookings] = useState([]);
  const { setNotification } = useOutletContext();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      // Загружаем данные параллельно
      const [moviesRes, hallsRes, screeningsRes, bookingsRes] = await Promise.all([
        api.get('/movies/'),
        api.get('/cinemas/halls/'),
        api.get('/screenings/'),
        api.get('/bookings/')
      ]);

      // Получаем сегодняшнюю дату для фильтрации
      const today = new Date().toISOString().split('T')[0];
      
      // Фильтруем бронирования за сегодня
      const todayBookings = bookingsRes.data.filter(booking => 
        booking.created_at?.startsWith(today)
      ).length;

      // Считаем общую выручку
      const totalRevenue = bookingsRes.data
        .filter(b => b.status === 'confirmed')
        .reduce((sum, b) => sum + (b.price || 0), 0);

      setStats({
        movies: moviesRes.data.length,
        halls: hallsRes.data.length,
        screenings: screeningsRes.data.length,
        bookings: bookingsRes.data.length,
        revenue: totalRevenue,
        todayBookings: todayBookings
      });

      // Берем последние 5 бронирований
      setRecentBookings(bookingsRes.data.slice(0, 5));
    } catch (error) {
      console.error('Error fetching stats:', error);
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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <>
      {/* Секция 1: Приветствие */}
      <AccordionSection title="Панель управления" sectionNumber={1}>
        <p className="conf-step__paragraph">
          Добро пожаловать в административную панель кинотеатра "ИдёмВКино".
          Здесь вы можете управлять залами, фильмами, сеансами и бронированиями.
        </p>
      </AccordionSection>

      {/* Секция 2: Статистика */}
      <AccordionSection title="Статистика" sectionNumber={2}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-600">Фильмы</h3>
            <p className="text-3xl font-bold text-primary">{stats.movies}</p>
          </div>
          <div className="bg-white p-4 rounded shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-600">Залы</h3>
            <p className="text-3xl font-bold text-secondary">{stats.halls}</p>
          </div>
          <div className="bg-white p-4 rounded shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-600">Сеансы</h3>
            <p className="text-3xl font-bold text-accent">{stats.screenings}</p>
          </div>
          <div className="bg-white p-4 rounded shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-600">Всего бронирований</h3>
            <p className="text-3xl font-bold text-purple-600">{stats.bookings}</p>
          </div>
          <div className="bg-white p-4 rounded shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-600">За сегодня</h3>
            <p className="text-3xl font-bold text-green-600">{stats.todayBookings}</p>
          </div>
          <div className="bg-white p-4 rounded shadow hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-600">Выручка</h3>
            <p className="text-3xl font-bold text-orange-600">{stats.revenue.toLocaleString()} ₽</p>
          </div>
        </div>
      </AccordionSection>

      {/* Секция 3: Быстрые действия */}
      <AccordionSection title="Быстрые действия" sectionNumber={3}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link 
            to="/admin/movies" 
            className="bg-blue-100 p-4 rounded-lg text-center hover:bg-blue-200 transition group"
          >
            <span className="text-4xl mb-2 block group-hover:scale-110 transition">🎬</span>
            <span className="font-semibold">Добавить фильм</span>
            <p className="text-sm text-gray-600 mt-1">Новый фильм в репертуар</p>
          </Link>
          <Link 
            to="/admin/halls" 
            className="bg-green-100 p-4 rounded-lg text-center hover:bg-green-200 transition group"
          >
            <span className="text-4xl mb-2 block group-hover:scale-110 transition">🏛️</span>
            <span className="font-semibold">Настроить зал</span>
            <p className="text-sm text-gray-600 mt-1">Изменить схему мест</p>
          </Link>
          <Link 
            to="/admin/screenings" 
            className="bg-purple-100 p-4 rounded-lg text-center hover:bg-purple-200 transition group"
          >
            <span className="text-4xl mb-2 block group-hover:scale-110 transition">⏰</span>
            <span className="font-semibold">Создать сеанс</span>
            <p className="text-sm text-gray-600 mt-1">Добавить время показа</p>
          </Link>
        </div>
      </AccordionSection>

      {/* Секция 4: Последние бронирования */}
      <AccordionSection title="Последние бронирования" sectionNumber={4}>
        {recentBookings.length > 0 ? (
          <div className="bg-white rounded shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-3 text-left">Код</th>
                  <th className="p-3 text-left">Фильм</th>
                  <th className="p-3 text-left">Пользователь</th>
                  <th className="p-3 text-left">Время</th>
                  <th className="p-3 text-left">Статус</th>
                </tr>
              </thead>
              <tbody>
                {recentBookings.map(booking => (
                  <tr key={booking.id} className="border-t hover:bg-gray-50">
                    <td className="p-3 font-mono text-sm">{booking.booking_code}</td>
                    <td className="p-3">{booking.screening_details?.movie_title || '—'}</td>
                    <td className="p-3">{booking.user_details?.username || '—'}</td>
                    <td className="p-3">{formatDateTime(booking.created_at)}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        booking.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                        booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {booking.status === 'confirmed' ? 'Подтверждено' :
                         booking.status === 'cancelled' ? 'Отменено' :
                         booking.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="p-3 text-center border-t">
              <Link 
                to="/admin/bookings" 
                className="text-primary hover:underline"
              >
                Все бронирования →
              </Link>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">Нет последних бронирований</p>
        )}
      </AccordionSection>
    </>
  );
};

export default AdminDashboard;