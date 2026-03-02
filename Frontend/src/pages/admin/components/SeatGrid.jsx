import React from 'react';

const SeatGrid = ({ seatsByRow, onSeatClick }) => {
  const rows = seatsByRow && typeof seatsByRow === 'object' 
    ? Object.keys(seatsByRow).sort((a, b) => parseInt(a) - parseInt(b))
    : [];

  const getSeatClass = (seat) => {
    if (!seat) return 'conf-step__chair';
    if (seat.seat_type === 'disabled') return 'conf-step__chair conf-step__chair_disabled';
    if (seat.seat_type === 'vip') return 'conf-step__chair conf-step__chair_vip';
    return 'conf-step__chair conf-step__chair_standart';
  };

  const getSeatTitle = (seat) => {
    if (!seat) return '';
    const typeText = seat.seat_type === 'vip' ? 'VIP' : 
                     seat.seat_type === 'disabled' ? 'заблокировано' : 'обычное';
    return `Ряд ${seat.row}, Место ${seat.number} - ${typeText}`;
  };

  if (!seatsByRow || Object.keys(seatsByRow).length === 0) {
    return (
      <div className="conf-step__hall">
        <div className="conf-step__hall-wrapper text-center py-8 text-gray-500">
          Нет данных о местах. Создайте зал или выберите другой.
        </div>
      </div>
    );
  }

  return (
    <div className="conf-step__hall">
      <div className="conf-step__hall-wrapper">
        {rows.map(rowNum => (
          <div key={rowNum} className="conf-step__row">
            {Array.isArray(seatsByRow[rowNum]) && seatsByRow[rowNum]
              .sort((a, b) => a.number - b.number)
              .map(seat => (
                <span
                  key={seat.id}
                  className={getSeatClass(seat)}
                  onClick={() => onSeatClick && onSeatClick(seat)}
                  title={getSeatTitle(seat)}
                />
              ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SeatGrid;