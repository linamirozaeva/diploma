import React from 'react';

const HallSelector = ({ halls, selectedHall, onSelectHall }) => {
  return (
    <div className="conf-step__selectors-box">
      {halls.map((hall) => (
        <li key={hall.id}>
          <input
            type="radio"
            className="conf-step__radio"
            name="hall-selector"
            value={hall.id}
            checked={selectedHall === hall.id}
            onChange={() => onSelectHall(hall.id)}
          />
          <span className="conf-step__selector">{hall.name}</span>
        </li>
      ))}
    </div>
  );
};

export default HallSelector;