import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../../services/api';

const AdminScreenings = () => {
  const [screenings, setScreenings] = useState([]);
  const [movies, setMovies] = useState([]);
  const [halls, setHalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingScreening, setEditingScreening] = useState(null);
  const { setNotification } = useOutletContext();
  
  const [formData, setFormData] = useState({
    movie: '',
    hall: '',
    start_time: '',
    price_standard: 250,
    price_vip: 350,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [screeningsRes, moviesRes, hallsRes] = await Promise.all([
        api.get('/screenings/'),
        api.get('/movies/'),
        api.get('/cinemas/halls/'),
      ]);
      setScreenings(screeningsRes.data);
      setMovies(moviesRes.data);
      setHalls(hallsRes.data);
    } catch (error) {
      setNotification({
        message: 'Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingScreening) {
        await api.put(`/screenings/${editingScreening.id}/`, formData);
        setNotification({ message: 'Сеанс успешно обновлен!', type: 'success' });
      } else {
        await api.post('/screenings/', formData);
        setNotification({ message: 'Сеанс успешно создан!', type: 'success' });
      }
      fetchData();
      setShowModal(false);
      resetForm();
    } catch (error) {
      setNotification({
        message: 'Ошибка сохранения: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Вы уверены, что хотите удалить этот сеанс?')) {
      try {
        await api.delete(`/screenings/${id}/`);
        setNotification({ message: 'Сеанс успешно удален!', type: 'success' });
        fetchData();
      } catch (error) {
        setNotification({
          message: 'Ошибка удаления: ' + (error.response?.data?.detail || error.message),
          type: 'error'
        });
      }
    }
  };

  const handleEdit = (screening) => {
    setEditingScreening(screening);
    setFormData({
      movie: screening.movie,
      hall: screening.hall,
      start_time: screening.start_time.slice(0, 16),
      price_standard: screening.price_standard,
      price_vip: screening.price_vip,
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setEditingScreening(null);
    setFormData({
      movie: '',
      hall: '',
      start_time: '',
      price_standard: 250,
      price_vip: 350,
    });
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
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
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold">Управление сеансами</h2>
        <button
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
          className="bg-primary text-white px-4 py-2 rounded hover:bg-opacity-90 transition flex items-center gap-2"
        >
          <span>➕</span> Добавить сеанс
        </button>
      </div>

      {/* Таблица сеансов */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Фильм
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Зал
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Время
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Цена (обычный/VIP)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {screenings.map(screening => (
              <tr key={screening.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="font-medium">{screening.movie_details?.title}</div>
                </td>
                <td className="px-6 py-4">
                  {screening.hall_details?.name}
                </td>
                <td className="px-6 py-4">
                  {formatDateTime(screening.start_time)}
                </td>
                <td className="px-6 py-4">
                  {screening.price_standard} / {screening.price_vip} ₽
                </td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(screening)}
                      className="text-blue-600 hover:text-blue-900 transition"
                      title="Редактировать"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(screening.id)}
                      className="text-red-600 hover:text-red-900 transition"
                      title="Удалить"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Модальное окно */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-2xl font-bold mb-4">
              {editingScreening ? 'Редактировать сеанс' : 'Новый сеанс'}
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Фильм *
                </label>
                <select
                  name="movie"
                  value={formData.movie}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                >
                  <option value="">Выберите фильм</option>
                  {movies.map(movie => (
                    <option key={movie.id} value={movie.id}>
                      {movie.title} ({movie.duration} мин)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Зал *
                </label>
                <select
                  name="hall"
                  value={formData.hall}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                >
                  <option value="">Выберите зал</option>
                  {halls.map(hall => (
                    <option key={hall.id} value={hall.id}>
                      {hall.name} ({hall.rows}x{hall.seats_per_row})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Время начала *
                </label>
                <input
                  type="datetime-local"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Цена обычного места *
                  </label>
                  <input
                    type="number"
                    name="price_standard"
                    value={formData.price_standard}
                    onChange={handleInputChange}
                    min="0"
                    step="10"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Цена VIP места *
                  </label>
                  <input
                    type="number"
                    name="price_vip"
                    value={formData.price_vip}
                    onChange={handleInputChange}
                    min="0"
                    step="10"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-opacity-90 transition"
                >
                  {editingScreening ? 'Сохранить' : 'Создать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminScreenings;