import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../../services/api';
import AccordionSection from './components/AccordionSection';

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
        message: 'Ошибка загрузки фильмов',
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
    
    console.log('Submitting form data:', formData);
    
    const formDataToSend = new FormData();
    Object.keys(formData).forEach(key => {
      if (formData[key] !== null && formData[key] !== '') {
        formDataToSend.append(key, formData[key]);
        console.log(`Appending ${key}:`, formData[key]);
      }
    });
    
    // Явно добавляем is_active = true
    formDataToSend.append('is_active', 'true');
    console.log('Appending is_active: true');
  
    try {
      if (editingMovie) {
        console.log('Updating movie with ID:', editingMovie.id);
        const response = await api.put(`/movies/${editingMovie.id}/`, formDataToSend, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        console.log('Update response:', response.data);
        setNotification({ message: 'Фильм обновлен', type: 'success' });
      } else {
        console.log('Creating new movie');
        const response = await api.post('/movies/', formDataToSend, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        console.log('Create response:', response.data);
        setNotification({ message: 'Фильм создан', type: 'success' });
      }
      fetchMovies();
      setShowModal(false);
      resetForm();
    } catch (error) {
      console.error('Error saving movie:', error);
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      console.error('Error response headers:', error.response?.headers);
      
      let errorMessage = 'Ошибка сохранения';
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          errorMessage = Object.entries(error.response.data)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n');
        } else {
          errorMessage = error.response.data;
        }
      }
      
      setNotification({
        message: errorMessage,
        type: 'error'
      });
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Удалить фильм?')) {
      try {
        await api.delete(`/movies/${id}/`);
        setNotification({ message: 'Фильм удален', type: 'success' });
        fetchMovies();
      } catch (error) {
        setNotification({ message: 'Ошибка удаления', type: 'error' });
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
    return <div className="text-center py-20">Загрузка...</div>;
  }

  return (
    <>
      <AccordionSection title="Управление фильмами" sectionNumber={1}>
        <div className="flex justify-end mb-4">
          <button
            onClick={() => setShowModal(true)}
            className="conf-step__button conf-step__button-accent"
          >
            + Добавить фильм
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {movies.map(movie => (
            <div key={movie.id} className="bg-white p-4 rounded shadow flex gap-4">
              <img
                src={movie.poster_url || '/src/assets/poster_admin.jpg'}
                alt={movie.title}
                className="w-20 h-28 object-cover rounded"
              />
              <div className="flex-grow">
                <h3 className="font-bold text-lg">{movie.title}</h3>
                <p className="text-sm text-gray-600">{movie.duration} мин | {movie.age_rating}</p>
                <p className="text-sm text-gray-500 mt-2 line-clamp-2">{movie.description}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(movie)}
                  className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                  title="Редактировать"
                >
                  ✏️
                </button>
                <button
                  onClick={() => handleDelete(movie.id)}
                  className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                  title="Удалить"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      </AccordionSection>

      {/* Модальное окно */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingMovie ? 'Редактировать фильм' : 'Новый фильм'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {posterPreview && (
                <div className="text-center">
                  <img src={posterPreview} alt="Preview" className="h-32 mx-auto" />
                </div>
              )}

              <div>
                <label className="block mb-1">Название *</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded"
                  required
                />
              </div>

              <div>
                <label className="block mb-1">Описание</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="3"
                  className="w-full p-2 border rounded"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block mb-1">Длительность (мин) *</label>
                  <input
                    type="number"
                    name="duration"
                    value={formData.duration}
                    onChange={handleInputChange}
                    className="w-full p-2 border rounded"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-1">Дата выхода</label>
                  <input
                    type="date"
                    name="release_date"
                    value={formData.release_date}
                    onChange={handleInputChange}
                    className="w-full p-2 border rounded"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block mb-1">Страна</label>
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleInputChange}
                    className="w-full p-2 border rounded"
                  />
                </div>
                <div>
                  <label className="block mb-1">Режиссер</label>
                  <input
                    type="text"
                    name="director"
                    value={formData.director}
                    onChange={handleInputChange}
                    className="w-full p-2 border rounded"
                  />
                </div>
              </div>

              <div>
                <label className="block mb-1">В ролях</label>
                <input
                  type="text"
                  name="cast"
                  value={formData.cast}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded"
                  placeholder="Актер 1, Актер 2, ..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block mb-1">Возрастной рейтинг</label>
                  <select
                    name="age_rating"
                    value={formData.age_rating}
                    onChange={handleInputChange}
                    className="w-full p-2 border rounded"
                  >
                    <option value="0+">0+</option>
                    <option value="6+">6+</option>
                    <option value="12+">12+</option>
                    <option value="16+">16+</option>
                    <option value="18+">18+</option>
                  </select>
                </div>
                <div>
                  <label className="block mb-1">Трейлер</label>
                  <input
                    type="url"
                    name="trailer_url"
                    value={formData.trailer_url}
                    onChange={handleInputChange}
                    className="w-full p-2 border rounded"
                    placeholder="https://youtube.com/..."
                  />
                </div>
              </div>

              <div>
                <label className="block mb-1">Постер</label>
                <input
                  type="file"
                  name="poster"
                  onChange={handleInputChange}
                  accept="image/*"
                  className="w-full p-2 border rounded"
                />
              </div>

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-opacity-90"
                >
                  {editingMovie ? 'Сохранить' : 'Создать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default AdminMovies;