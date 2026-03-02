import React from 'react';

const MovieGrid = ({ movies }) => {
  const colors = [
    '#caff85', '#85ff89', '#85ffd3', '#85e2ff', 
    '#8599ff', '#ba85ff', '#ff85fb', '#ff85b1', '#ffa285'
  ];

  return (
    <div className="conf-step__movies">
      {movies.map((movie, index) => (
        <div 
          key={movie.id} 
          className="conf-step__movie"
          style={{ backgroundColor: colors[index % colors.length] }}
        >
          <img 
            className="conf-step__movie-poster" 
            src={movie.poster_url || '/src/assets/poster_admin.jpg'} 
            alt={movie.title}
          />
          <h3 className="conf-step__movie-title">{movie.title}</h3>
          <p className="conf-step__movie-duration">{movie.duration} минут</p>
        </div>
      ))}
    </div>
  );
};

export default MovieGrid;