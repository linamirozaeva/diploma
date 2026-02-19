import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const HomePage = () => {
  const [movies, setMovies] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMovies();
  }, []);

  const fetchMovies = async () => {
    try {
      const response = await api.get('/movies/');
      setMovies(response.data);
    } catch (error) {
      console.error('Error fetching movies:', error);
    } finally {
      setLoading(false);
    }
  };

  const daysOfWeek = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  const dates = [];
  for (let i = 0; i < 7; i++) {
    const date = new Date();
    date.setDate(date.getDate() + i);
    dates.push({
      day: daysOfWeek[date.getDay() === 0 ? 6 : date.getDay() - 1],
      number: date.getDate(),
      fullDate: date.toISOString().split('T')[0],
      isToday: i === 0,
      isWeekend: date.getDay() === 0 || date.getDay() === 6,
    });
  }

  if (loading) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="text-center text-2xl">Загрузка...</div>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      {/* Навигация по дням */}
      <nav className="flex gap-1 mb-8 overflow-x-auto">
        {dates.map((date) => (
          <button
            key={date.fullDate}
            onClick={() => setSelectedDate(date.fullDate)}
            className={`flex-1 min-w-[80px] p-4 text-center rounded transition ${
              selectedDate === date.fullDate
                ? 'bg-white scale-110 font-bold shadow-lg'
                : 'bg-white bg-opacity-90 hover:bg-opacity-100'
            } ${date.isWeekend ? 'text-red-600' : ''}`}
          >
            <span className="block">
              {date.isToday ? 'Сегодня' : date.day}
              {!date.isToday && <span className="text-xs">,</span>}
            </span>
            <span className="block text-sm">
              {!date.isToday && date.number}
            </span>
          </button>
        ))}
      </nav>

      {/* Список фильмов */}
      <div className="space-y-8">
        {movies.map((movie) => (
          <section key={movie.id} className="bg-white bg-opacity-95 p-6 rounded-lg">
            <div className="flex gap-6">
              {/* Постер */}
              <div className="relative w-40 h-56 flex-shrink-0">
                <img
                  src={movie.poster_url || '/src/assets/no-poster.jpg'}
                  alt={movie.title}
                  className="absolute top-0 left-0 w-full h-full object-cover rounded"
                />
              </div>
              
              {/* Информация о фильме */}
              <div className="flex-grow">
                <h2 className="text-2xl font-bold mb-3">{movie.title}</h2>
                <p className="text-gray-700 mb-4 line-clamp-3">{movie.description}</p>
                <p className="text-gray-600">
                  <span className="mr-6">{movie.duration} минут</span>
                  <span>{movie.country || 'Не указано'}</span>
                </p>
                
                {/* Сеансы по залам */}
                <div className="mt-4">
                  <h3 className="font-bold text-lg mb-2">Зал 1</h3>
                  <div className="flex flex-wrap gap-2">
                    {[1, 2, 3, 4].map((time) => (
                      <Link
                        key={time}
                        to={`/hall/${time}`}
                        className="px-4 py-2 bg-white text-gray-800 rounded shadow hover:shadow-md transition"
                      >
                        {10 + time}:00
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </section>
        ))}
      </div>
    </main>
  );
};

export default HomePage;