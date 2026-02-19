import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../../services/api';

const AdminMovies = () => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingMovie, setEditingMovie] = useState(null);
  const [posterPreview, setPosterPreview] = useState(null);
  const { setNotification } = useOutletContext();
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    duration: 120,
    release_date: '',
    country: '',
    director: '',
    cast: '',
    age_rating: '12+',
    poster: null,
    trailer_url: '',
  });

  useEffect(() => {
    fetchMovies();
  }, []);

  const fetchMovies = async () => {
    try {
      const response = await api.get('/movies/');
      setMovies(response.data);
    } catch (error) {
      setNotification({
        message: 'Ошибка загрузки фильмов: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'poster') {
      const file = files[0];
      setFormData({ ...formData, poster: file });
      // Создаем превью
      if (file) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setPosterPreview(reader.result);
        };
        reader.readAsDataURL(file);
      }
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formDataToSend = new FormData();
    Object.keys(formData).forEach(key => {
      if (formData[key] !== null && formData[key] !== '') {
        formDataToSend.append(key, formData[key]);
      }
    });

    try {
      if (editingMovie) {
        await api.put(`/movies/${editingMovie.id}/`, formDataToSend, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setNotification({ message: 'Фильм успешно обновлен!', type: 'success' });
      } else {
        await api.post('/movies/', formDataToSend, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setNotification({ message: 'Фильм успешно создан!', type: 'success' });
      }
      fetchMovies();
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
    if (window.confirm('Вы уверены, что хотите удалить этот фильм?')) {
      try {
        await api.delete(`/movies/${id}/`);
        setNotification({ message: 'Фильм успешно удален!', type: 'success' });
        fetchMovies();
      } catch (error) {
        setNotification({
          message: 'Ошибка удаления: ' + (error.response?.data?.detail || error.message),
          type: 'error'
        });
      }
    }
  };

  const handleEdit = (movie) => {
    setEditingMovie(movie);
    setFormData({
      title: movie.title,
      description: movie.description,
      duration: movie.duration,
      release_date: movie.release_date || '',
      country: movie.country || '',
      director: movie.director || '',
      cast: movie.cast || '',
      age_rating: movie.age_rating || '12+',
      poster: null,
      trailer_url: movie.trailer_url || '',
    });
    setPosterPreview(movie.poster_url);
    setShowModal(true);
  };

  const resetForm = () => {
    setEditingMovie(null);
    setFormData({
      title: '',
      description: '',
      duration: 120,
      release_date: '',
      country: '',
      director: '',
      cast: '',
      age_rating: '12+',
      poster: null,
      trailer_url: '',
    });
    setPosterPreview(null);
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
        <h2 className="text-3xl font-bold">Управление фильмами</h2>
        <button
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
          className="bg-primary text-white px-4 py-2 rounded hover:bg-opacity-90 transition flex items-center gap-2"
        >
          <span>➕</span> Добавить фильм
        </button>
      </div>

      {/* Список фильмов */}
      <div className="grid grid-cols-1 gap-4">
        {movies.map(movie => (
          <div key={movie.id} className="bg-white rounded-lg shadow-lg p-4 hover:shadow-xl transition">
            <div className="flex gap-4">
              <img
                src={movie.poster_url || '/src/assets/no-poster.jpg'}
                alt={movie.title}
                className="w-24 h-32 object-cover rounded"
                onError={(e) => {
                  e.target.src = '/src/assets/no-poster.jpg';
                }}
              />
              
              <div className="flex-grow">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold">{movie.title}</h3>
                    <p className="text-gray-600">{movie.duration} мин | {movie.age_rating}</p>
                    {movie.country && <p className="text-gray-500 text-sm">{movie.country}</p>}
                    <p className="text-gray-500 text-sm mt-2 line-clamp-2">{movie.description}</p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(movie)}
                      className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                      title="Редактировать"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(movie.id)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition"
                      title="Удалить"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Модальное окно */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 overflow-y-auto z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full my-8">
            <h3 className="text-2xl font-bold mb-4">
              {editingMovie ? 'Редактировать фильм' : 'Новый фильм'}
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Превью постера */}
              {posterPreview && (
                <div className="mb-4 text-center">
                  <img src={posterPreview} alt="Превью" className="h-32 mx-auto rounded" />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название фильма *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Описание
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Длительность (мин) *
                  </label>
                  <input
                    type="number"
                    name="duration"
                    value={formData.duration}
                    onChange={handleInputChange}
                    min="1"
                    max="300"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Дата выхода
                  </label>
                  <input
                    type="date"
                    name="release_date"
                    value={formData.release_date}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Страна
                  </label>
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Режиссер
                  </label>
                  <input
                    type="text"
                    name="director"
                    value={formData.director}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  В ролях
                </label>
                <input
                  type="text"
                  name="cast"
                  value={formData.cast}
                  onChange={handleInputChange}
                  placeholder="Актер 1, Актер 2, ..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Возрастной рейтинг
                  </label>
                  <select
                    name="age_rating"
                    value={formData.age_rating}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="0+">0+</option>
                    <option value="6+">6+</option>
                    <option value="12+">12+</option>
                    <option value="16+">16+</option>
                    <option value="18+">18+</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ссылка на трейлер
                  </label>
                  <input
                    type="url"
                    name="trailer_url"
                    value={formData.trailer_url}
                    onChange={handleInputChange}
                    placeholder="https://youtube.com/..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Постер
                </label>
                <input
                  type="file"
                  name="poster"
                  onChange={handleInputChange}
                  accept="image/*"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Рекомендуемый размер: 300x450 пикселей
                </p>
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
                  {editingMovie ? 'Сохранить' : 'Создать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMovies;