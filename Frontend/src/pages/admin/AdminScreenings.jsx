import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../../services/api';
import AccordionSection from './components/AccordionSection';

const AdminScreenings = () => {
  const [screenings, setScreenings] = useState([]);
  const [movies, setMovies] = useState([]);
  const [halls, setHalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingScreening, setEditingScreening] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});
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
      
      console.log('Movies loaded:', moviesRes.data);
      console.log('Halls loaded:', hallsRes.data);
      console.log('Screenings loaded:', screeningsRes.data);
      
      setMovies(moviesRes.data);
      setHalls(hallsRes.data);
      setScreenings(screeningsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setNotification({
        message: 'Ошибка загрузки данных',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    if (validationErrors[name]) {
      setValidationErrors({
        ...validationErrors,
        [name]: null
      });
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.movie) {
      errors.movie = 'Выберите фильм';
    }
    if (!formData.hall) {
      errors.hall = 'Выберите зал';
    }
    if (!formData.start_time) {
      errors.start_time = 'Укажите время начала';
    }
    if (!formData.price_standard || formData.price_standard < 0) {
      errors.price_standard = 'Укажите корректную цену';
    }
    if (!formData.price_vip || formData.price_vip < 0) {
      errors.price_vip = 'Укажите корректную цену';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      setNotification({
        message: 'Заполните все обязательные поля',
        type: 'error'
      });
      return;
    }
  
    const selectedMovie = movies.find(m => m.id === parseInt(formData.movie));
    
    if (!selectedMovie) {
      setNotification({
        message: 'Выбранный фильм не найден',
        type: 'error'
      });
      return;
    }
  
    const startTime = new Date(formData.start_time);
    
    const endTime = new Date(startTime.getTime() + selectedMovie.duration * 60000);
    
    const formatDateForDjango = (date) => {
      return date.toISOString().slice(0, 19).replace('T', ' ');
    };
  
    const screeningData = {
      movie: parseInt(formData.movie),
      hall: parseInt(formData.hall),
      start_time: formatDateForDjango(startTime),
      end_time: formatDateForDjango(endTime),  
      price_standard: parseInt(formData.price_standard),
      price_vip: parseInt(formData.price_vip)
    };
  
    console.log('Selected movie:', selectedMovie);
    console.log('Duration:', selectedMovie.duration);
    console.log('Start time:', startTime);
    console.log('End time:', endTime);
    console.log('Sending screening data:', screeningData);
  
    try {
      let response;
      if (editingScreening) {
        response = await api.put(`/screenings/${editingScreening.id}/`, screeningData);
        console.log('Update response:', response.data);
        setNotification({ message: 'Сеанс обновлен', type: 'success' });
      } else {
        response = await api.post('/screenings/', screeningData);
        console.log('Create response:', response.data);
        setNotification({ message: 'Сеанс создан', type: 'success' });
      }
      
      await fetchData();
      setShowModal(false);
      resetForm();
      
    } catch (error) {
      console.error('Error saving screening:', error);
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      
      if (error.response?.data) {
        const serverErrors = error.response.data;
        let errorMessage = '';
        
        if (typeof serverErrors === 'object') {
          errorMessage = Object.entries(serverErrors)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
            .join('\n');
          setValidationErrors(serverErrors);
        } else {
          errorMessage = serverErrors;
        }
        
        setNotification({
          message: errorMessage || 'Ошибка сохранения',
          type: 'error'
        });
      } else {
        setNotification({
          message: 'Ошибка соединения с сервером',
          type: 'error'
        });
      }
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Вы уверены, что хотите удалить этот сеанс?')) {
      try {
        await api.delete(`/screenings/${id}/`);
        setNotification({ message: 'Сеанс удален', type: 'success' });
        fetchData();
      } catch (error) {
        console.error('Error deleting screening:', error);
        setNotification({
          message: 'Ошибка удаления сеанса',
          type: 'error'
        });
      }
    }
  };

  const handleEdit = (screening) => {
    setEditingScreening(screening);
    const startTime = new Date(screening.start_time);
    const formattedDate = startTime.toISOString().slice(0, 16);
    
    setFormData({
      movie: screening.movie,
      hall: screening.hall,
      start_time: formattedDate,
      price_standard: screening.price_standard,
      price_vip: screening.price_vip,
    });
    setValidationErrors({});
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
    setValidationErrors({});
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
    <>
      <AccordionSection title="Управление сеансами" sectionNumber={1}>
        <div className="flex justify-end mb-4">
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="conf-step__button conf-step__button-accent"
          >
            + Добавить сеанс
          </button>
        </div>

        {screenings.length === 0 ? (
          <div className="text-center py-8 bg-white rounded shadow">
            <p className="text-gray-500">Нет сеансов. Создайте первый сеанс!</p>
          </div>
        ) : (
          <div className="bg-white rounded shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-3 text-left">Фильм</th>
                  <th className="p-3 text-left">Зал</th>
                  <th className="p-3 text-left">Время</th>
                  <th className="p-3 text-left">Цена (обыч/VIP)</th>
                  <th className="p-3 text-left">Действия</th>
                </tr>
              </thead>
              <tbody>
                {screenings.map((screening) => (
                  <tr key={screening.id} className="border-t hover:bg-gray-50">
                    <td className="p-3">{screening.movie_details?.title || '—'}</td>
                    <td className="p-3">{screening.hall_details?.name || '—'}</td>
                    <td className="p-3">{formatDateTime(screening.start_time)}</td>
                    <td className="p-3">{screening.price_standard} / {screening.price_vip} ₽</td>
                    <td className="p-3">
                      <button
                        onClick={() => handleEdit(screening)}
                        className="mr-2 text-blue-600 hover:text-blue-800"
                        title="Редактировать"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDelete(screening.id)}
                        className="text-red-600 hover:text-red-800"
                        title="Удалить"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </AccordionSection>

      {/* Модальное окно */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full max-h-screen overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingScreening ? 'Редактировать сеанс' : 'Новый сеанс'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block mb-1 font-medium">
                  Фильм <span className="text-red-500">*</span>
                </label>
                <select
                  name="movie"
                  value={formData.movie}
                  onChange={handleInputChange}
                  className={`w-full p-2 border rounded ${validationErrors.movie ? 'border-red-500' : ''}`}
                  required
                >
                  <option value="">Выберите фильм</option>
                  {movies.map(movie => (
                    <option key={movie.id} value={movie.id}>
                      {movie.title} ({movie.duration} мин)
                    </option>
                  ))}
                </select>
                {validationErrors.movie && (
                  <p className="text-red-500 text-sm mt-1">{validationErrors.movie}</p>
                )}
              </div>

              <div>
                <label className="block mb-1 font-medium">
                  Зал <span className="text-red-500">*</span>
                </label>
                <select
                  name="hall"
                  value={formData.hall}
                  onChange={handleInputChange}
                  className={`w-full p-2 border rounded ${validationErrors.hall ? 'border-red-500' : ''}`}
                  required
                >
                  <option value="">Выберите зал</option>
                  {halls.map(hall => (
                    <option key={hall.id} value={hall.id}>
                      {hall.name} ({hall.rows}x{hall.seats_per_row})
                    </option>
                  ))}
                </select>
                {validationErrors.hall && (
                  <p className="text-red-500 text-sm mt-1">{validationErrors.hall}</p>
                )}
              </div>

              <div>
                <label className="block mb-1 font-medium">
                  Время начала <span className="text-red-500">*</span>
                </label>
                <input
                  type="datetime-local"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleInputChange}
                  className={`w-full p-2 border rounded ${validationErrors.start_time ? 'border-red-500' : ''}`}
                  required
                />
                {validationErrors.start_time && (
                  <p className="text-red-500 text-sm mt-1">{validationErrors.start_time}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block mb-1 font-medium">
                    Цена обычного <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="price_standard"
                    value={formData.price_standard}
                    onChange={handleInputChange}
                    min="0"
                    step="10"
                    className={`w-full p-2 border rounded ${validationErrors.price_standard ? 'border-red-500' : ''}`}
                    required
                  />
                  {validationErrors.price_standard && (
                    <p className="text-red-500 text-sm mt-1">{validationErrors.price_standard}</p>
                  )}
                </div>
                <div>
                  <label className="block mb-1 font-medium">
                    Цена VIP <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="price_vip"
                    value={formData.price_vip}
                    onChange={handleInputChange}
                    min="0"
                    step="10"
                    className={`w-full p-2 border rounded ${validationErrors.price_vip ? 'border-red-500' : ''}`}
                    required
                  />
                  {validationErrors.price_vip && (
                    <p className="text-red-500 text-sm mt-1">{validationErrors.price_vip}</p>
                  )}
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-opacity-90"
                >
                  {editingScreening ? 'Сохранить' : 'Создать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default AdminScreenings;