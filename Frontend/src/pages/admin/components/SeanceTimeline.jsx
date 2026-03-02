import React from 'react';

const SeanceTimeline = ({ halls, screenings }) => {
  // Конвертация времени в минуты с начала дня
  const timeToMinutes = (timeStr) => {
    const date = new Date(timeStr);
    return date.getHours() * 60 + date.getMinutes();
  };

  // 1 минута = 0.5 пикселя
  const MINUTE_WIDTH = 0.5;

  return (
    <div className="conf-step__seances">
      {halls.map(hall => {
        const hallScreenings = screenings.filter(s => s.hall === hall.id);
        
        return (
          <div key={hall.id} className="conf-step__seances-hall">
            <h3 className="conf-step__seances-title">{hall.name}</h3>
            <div className="conf-step__seances-timeline">
              {hallScreenings.map(screening => {
                const startMinutes = timeToMinutes(screening.start_time);
                const duration = screening.movie_details?.duration || 120;
                
                return (
                  <div
                    key={screening.id}
                    className="conf-step__seances-movie"
                    style={{
                      width: `${duration * MINUTE_WIDTH}px`,
                      left: `${startMinutes * MINUTE_WIDTH}px`,
                      backgroundColor: `hsl(${screening.id * 30 % 360}, 70%, 70%)`
                    }}
                  >
                    <p className="conf-step__seances-movie-title">
                      {screening.movie_details?.title}
                    </p>
                    <p className="conf-step__seances-movie-start">
                      {new Date(screening.start_time).toLocaleTimeString('ru-RU', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SeanceTimeline;