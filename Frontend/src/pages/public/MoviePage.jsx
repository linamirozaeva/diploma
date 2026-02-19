import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../services/api';

const MoviePage = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [screenings, setScreenings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMovieData();
  }, [id]);

  const fetchMovieData = async () => {
    try {
      // Получаем информацию о фильме
      const movieResponse = await api.get(`/movies/${id}/`);
      setMovie(movieResponse.data);
      
      // Получаем сеансы для этого фильма
      const screeningsResponse = await api.get(`/screenings/?movie=${id}&future_only=true`);
      setScreenings(screeningsResponse.data);
    } catch (error) {
      console.error('Error fetching movie:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const groupScreeningsByHall = () => {
    const grouped = {};
    screenings.forEach(screening => {
      const hallName = screening.hall_details?.name || 'Зал';
      if (!grouped[hallName]) {
        grouped[hallName] = [];
      }
      grouped[hallName].push(screening);
    });
    return grouped;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-2xl">Загрузка...</div>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="text-center py-20">
        <h2 className="text-3xl mb-4">Фильм не найден</h2>
        <Link to="/" className="text-primary hover:underline">
          Вернуться на главную
        </Link>
      </div>
    );
  }

  const groupedScreenings = groupScreeningsByHall();

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="bg-white bg-opacity-95 rounded-lg p-8">
        {/* Кнопка назад */}
        <Link to="/" className="inline-flex items-center text-gray-600 hover:text-primary mb-6">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Назад к расписанию
        </Link>

        <div className="flex flex-col md:flex-row gap-8">
          {/* Постер фильма */}
          <div className="md:w-1/3">
            {/* ====================================================
                КАРТИНКА: Постер фильма (детальная страница)
                Файл: /media/posters/{movie.id}.jpg (из бэкенда)
                Заглушка: /src/assets/no-poster.jpg
                Размер: 300x450 пикселей (увеличенный для детальной страницы)
                ==================================================== */}
            <img
              src={movie.poster_url || '/src/assets/no-poster.jpg'}
              alt={movie.title}
              className="w-full rounded-lg shadow-lg"
            />
          </div>

          {/* Информация о фильме */}
          <div className="md:w-2/3">
            <h1 className="text-4xl font-bold mb-4">{movie.title}</h1>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-gray-600">Длительность</p>
                <p className="font-semibold">{movie.duration} минут</p>
              </div>
              <div>
                <p className="text-gray-600">Страна</p>
                <p className="font-semibold">{movie.country || 'Не указано'}</p>
              </div>
              <div>
                <p className="text-gray-600">Режиссер</p>
                <p className="font-semibold">{movie.director || 'Не указано'}</p>
              </div>
              <div>
                <p className="text-gray-600">Возрастной рейтинг</p>
                <p className="font-semibold">{movie.age_rating || '12+'}</p>
              </div>
            </div>

            <div className="mb-6">
              <h3 className="text-xl font-bold mb-2">О фильме</h3>
              <p className="text-gray-700 leading-relaxed">{movie.description}</p>
            </div>

            {movie.cast && (
              <div className="mb-6">
                <h3 className="text-xl font-bold mb-2">В ролях</h3>
                <p className="text-gray-700">{movie.cast}</p>
              </div>
            )}

            {/* Трейлер (если есть) */}
            {movie.trailer_url && (
              <div className="mb-6">
                <h3 className="text-xl font-bold mb-2">Трейлер</h3>
                <a
                  href={movie.trailer_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  Смотреть на YouTube
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Сеансы */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Сеансы</h2>
          
          {Object.keys(groupedScreenings).length === 0 ? (
            <p className="text-gray-600">Нет предстоящих сеансов</p>
          ) : (
            Object.entries(groupedScreenings).map(([hallName, hallScreenings]) => (
              <div key={hallName} className="mb-8">
                <h3 className="text-xl font-bold mb-4">{hallName}</h3>
                <div className="flex flex-wrap gap-4">
                  {hallScreenings.map(screening => (
                    <Link
                      key={screening.id}
                      to={`/hall/${screening.id}`}
                      className="bg-white border-2 border-primary rounded-lg p-4 hover:shadow-lg transition"
                    >
                      <div className="text-lg font-semibold">
                        {new Date(screening.start_time).toLocaleTimeString('ru-RU', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                      <div className="text-sm text-gray-600">
                        от {screening.price_standard} ₽
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </main>
  );
};

export default MoviePage;