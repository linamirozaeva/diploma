import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const HomePage = () => {
  const [movies, setMovies] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(true);
  const [screeningsByMovie, setScreeningsByMovie] = useState({});

  useEffect(() => {
    fetchMovies();
  }, []);

  useEffect(() => {
    if (movies.length > 0) {
      fetchScreeningsForDate(selectedDate);
    }
  }, [movies, selectedDate]);

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

  const fetchScreeningsForDate = async (date) => {
    try {
      const response = await api.get(`/screenings/?date=${date}`);
      const screenings = response.data;
      
      const grouped = {};
      screenings.forEach(screening => {
        const movieId = screening.movie;
        if (!grouped[movieId]) {
          grouped[movieId] = [];
        }
        grouped[movieId].push(screening);
      });
      
      setScreeningsByMovie(grouped);
    } catch (error) {
      console.error('Error fetching screenings:', error);
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

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Загрузка...</p>
        </div>
      </main>
    );
  }

  return (
    <main>
      {/* Навигация по дням - sticky */}
      <nav className="page-nav" style={{ position: 'sticky', top: '2px', zIndex: 10 }}>
        {dates.map((date) => (
          <a
            key={date.fullDate}
            href="#"
            onClick={(e) => {
              e.preventDefault();
              setSelectedDate(date.fullDate);
            }}
            className={`page-nav__day ${
              date.isToday ? 'page-nav__day_today' : ''
            } ${
              selectedDate === date.fullDate ? 'page-nav__day_chosen' : ''
            } ${date.isWeekend ? 'page-nav__day_weekend' : ''}`}
          >
            <span className="page-nav__day-week">
              {date.isToday ? '' : date.day}
            </span>
            <span className="page-nav__day-number">{date.number}</span>
          </a>
        ))}
        <a href="#" className="page-nav__day page-nav__day_next"></a>
      </nav>

      {/* Список фильмов */}
      <div className="container mx-auto px-4 py-8">
        {movies.length === 0 ? (
          <div className="text-center py-12 bg-white bg-opacity-95 rounded-lg">
            <p className="text-xl text-gray-600 mb-4">Фильмы не найдены</p>
            <p className="text-gray-500">Добавьте фильмы в админ-панели</p>
          </div>
        ) : (
          movies.map((movie) => {
            const movieScreenings = screeningsByMovie[movie.id] || [];
            
            const screeningsByHall = {};
            movieScreenings.forEach(screening => {
              const hallName = screening.hall_details?.name || 'Зал';
              if (!screeningsByHall[hallName]) {
                screeningsByHall[hallName] = [];
              }
              screeningsByHall[hallName].push(screening);
            });

            return (
              <section key={movie.id} className="movie">
                <div className="movie__info">
                  {/* Постер с красным уголком */}
                  <div className="movie__poster">
                    <img
                      className="movie__poster-image"
                      src={movie.poster_url || '/src/assets/poster1_client.jpg'}
                      alt={movie.title}
                      onError={(e) => {
                        e.target.src = '/src/assets/poster1_client.jpg';
                      }}
                    />
                  </div>
                  
                  {/* Информация о фильме */}
                  <div className="movie__description">
                    <h2 className="movie__title">{movie.title}</h2>
                    <p className="movie__synopsis">{movie.description || 'Описание отсутствует'}</p>
                    <p className="movie__data">
                      <span className="movie__data-duration">{movie.duration} минут</span>
                      <span className="movie__data-origin">{movie.country || 'Не указано'}</span>
                    </p>
                  </div>
                </div>
                
                {/* Сеансы по залам */}
                {Object.keys(screeningsByHall).length > 0 ? (
                  Object.entries(screeningsByHall).map(([hallName, screenings]) => (
                    <div key={hallName} className="movie-seances__hall">
                      <h3 className="movie-seances__hall-title">{hallName}</h3>
                      <ul className="movie-seances__list">
                        {screenings.map((screening) => (
                          <li key={screening.id} className="movie-seances__time-block">
                            <Link
                              to={`/hall/${screening.id}`}
                              className="movie-seances__time"
                            >
                              {formatTime(screening.start_time)}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))
                ) : (
                  <div className="movie-seances__hall">
                    <p className="text-gray-500 text-center py-4">
                      Нет сеансов на выбранную дату
                    </p>
                  </div>
                )}
              </section>
            );
          })
        )}
      </div>
    </main>
  );
};

export default HomePage;