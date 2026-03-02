import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../../services/api';
import AccordionSection from './components/AccordionSection';
import HallSelector from './components/HallSelector';
import SeatGrid from './components/SeatGrid';

const AdminHalls = () => {
  const [halls, setHalls] = useState([]);
  const [selectedHall, setSelectedHall] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hallConfig, setHallConfig] = useState({
    rows: 10,
    seatsPerRow: 8,
    seats: []
  });
  const { setNotification } = useOutletContext();

  useEffect(() => {
    fetchHalls();
  }, []);

  const fetchHalls = async () => {
    try {
      const response = await api.get('/cinemas/halls/');
      console.log('Fetched halls:', response.data);
      setHalls(response.data);
      if (response.data.length > 0) {
        setSelectedHall(response.data[0].id);
        fetchHallSeats(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching halls:', error);
      setNotification({
        message: 'Ошибка загрузки залов',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchHallSeats = async (hallId) => {
    try {
      const response = await api.get(`/cinemas/halls/${hallId}/seats/`);
      console.log('Fetched seats:', response.data);
      
      const seatsData = Array.isArray(response.data) ? response.data : 
                       (response.data.seats ? response.data.seats : []);
      
      setHallConfig(prev => ({
        ...prev,
        seats: seatsData
      }));
    } catch (error) {
      console.error('Error fetching seats:', error);
      setHallConfig(prev => ({
        ...prev,
        seats: []
      }));
    }
  };

  const handleHallChange = (hallId) => {
    setSelectedHall(hallId);
    fetchHallSeats(hallId);
  };

  const handleSeatClick = async (seat) => {
    try {
      let newType = '';
      
      if (seat.seat_type === 'standard') {
        newType = 'vip';
      } else if (seat.seat_type === 'vip') {
        newType = 'disabled';
      } else if (seat.seat_type === 'disabled') {
        newType = 'standard';
      } else {
        newType = 'standard';
      }
  
      console.log(`Changing seat ${seat.id} from ${seat.seat_type} to ${newType}`);
      console.log('Selected hall:', selectedHall);
  
      if (!selectedHall) {
        setNotification({
          message: 'Не выбран зал',
          type: 'error'
        });
        return;
      }
  
      const url = `/cinemas/halls/${selectedHall}/update_seat_type/`;
      console.log('Sending request to:', url);
      console.log('Request data:', {
        seat_id: seat.id,
        seat_type: newType
      });
  
      const response = await api.post(url, {
        seat_id: seat.id,
        seat_type: newType
      });
  
      console.log('Update response:', response.data);
  
      setHallConfig(prev => {
        const updatedSeats = prev.seats.map(s => 
          s.id === seat.id ? { ...s, seat_type: newType } : s
        );
        
        return {
          ...prev,
          seats: updatedSeats
        };
      });
  
      const typeText = newType === 'standard' ? 'обычное' : 
                       newType === 'vip' ? 'VIP' : 'заблокированное';
      
      setNotification({
        message: `Место изменено на ${typeText}`,
        type: 'success'
      });
  
    } catch (error) {
      console.error('Error updating seat:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Error URL:', error.config?.url);
      
      const errorMessage = error.response?.data?.error || 
                           error.response?.data?.detail || 
                           'Ошибка обновления места';
      
      setNotification({
        message: errorMessage,
        type: 'error'
      });
    }
  };

  const handleDeleteHall = async (hallId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот зал?')) {
      try {
        await api.delete(`/cinemas/halls/${hallId}/`);
        setHalls(halls.filter(h => h.id !== hallId));
        setNotification({
          message: 'Зал удален',
          type: 'success'
        });
      } catch (error) {
        console.error('Error deleting hall:', error);
        setNotification({
          message: 'Ошибка удаления зала',
          type: 'error'
        });
      }
    }
  };

  const handleCreateHall = async () => {
    const name = prompt('Введите название нового зала:');
    if (!name) return;

    try {
      const response = await api.post('/cinemas/halls/', {
        name,
        rows: 10,
        seats_per_row: 8
      });
      
      setHalls([...halls, response.data]);
      setSelectedHall(response.data.id);
      
      const seats = [];
      for (let row = 1; row <= 10; row++) {
        for (let seat = 1; seat <= 8; seat++) {
          seats.push({
            id: `temp-${row}-${seat}`,
            row,
            number: seat,
            seat_type: 'standard',
            is_active: true
          });
        }
      }
      
      setHallConfig({
        rows: 10,
        seatsPerRow: 8,
        seats
      });
      
      setNotification({
        message: 'Зал создан',
        type: 'success'
      });
    } catch (error) {
      console.error('Error creating hall:', error);
      setNotification({
        message: 'Ошибка создания зала',
        type: 'error'
      });
    }
  };

  const handleSaveConfig = async () => {
    try {
      if (!selectedHall) {
        setNotification({
          message: 'Не выбран зал',
          type: 'error'
        });
        return;
      }
  
      console.log('Saving config for hall:', selectedHall);
      console.log('Config:', {
        rows: hallConfig.rows,
        seats_per_row: hallConfig.seatsPerRow
      });
  
      const response = await api.post(`/cinemas/halls/${selectedHall}/configure/`, {
        rows: hallConfig.rows,
        seats_per_row: hallConfig.seatsPerRow
      });
  
      console.log('Save response:', response.data);
      
      await fetchHallSeats(selectedHall);
      
      setNotification({
        message: 'Конфигурация зала сохранена',
        type: 'success'
      });
    } catch (error) {
      console.error('Error saving hall config:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      setNotification({
        message: error.response?.data?.error || 'Ошибка сохранения конфигурации',
        type: 'error'
      });
    }
  };

  const seatsByRow = () => {
    if (!Array.isArray(hallConfig.seats) || hallConfig.seats.length === 0) {
      return {};
    }
    
    return hallConfig.seats.reduce((acc, seat) => {
      if (!acc[seat.row]) acc[seat.row] = [];
      acc[seat.row].push(seat);
      return acc;
    }, {});
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="admin-halls-page">
      {/* Секция 1: Управление залами */}
      <AccordionSection title="Управление залами" sectionNumber={1}>
        <p className="conf-step__paragraph">Доступные залы:</p>
        <ul className="conf-step__list">
          {halls.length > 0 ? halls.map(hall => (
            <li key={hall.id} className="flex items-center justify-between">
              <span>{hall.name}</span>
              <button 
                className="conf-step__button conf-step__button-trash"
                onClick={() => handleDeleteHall(hall.id)}
                title="Удалить зал"
              />
            </li>
          )) : (
            <li className="text-gray-500">Нет доступных залов</li>
          )}
        </ul>
        <button 
          className="conf-step__button conf-step__button-accent"
          onClick={handleCreateHall}
        >
          Создать зал
        </button>
      </AccordionSection>

      {/* Секция 2: Конфигурация залов */}
      <AccordionSection title="Конфигурация залов" sectionNumber={2}>
        <p className="conf-step__paragraph">Выберите зал для конфигурации:</p>
        <HallSelector
          halls={halls}
          selectedHall={selectedHall}
          onSelectHall={handleHallChange}
        />
        
        <p className="conf-step__paragraph">
          Укажите количество рядов и максимальное количество кресел в ряду:
        </p>
        <div className="conf-step__legend">
          <label className="conf-step__label">
            Рядов, шт
            <input 
              type="number" 
              className="conf-step__input" 
              placeholder="10" 
              min="1"
              max="20"
              value={hallConfig.rows}
              onChange={(e) => setHallConfig({...hallConfig, rows: parseInt(e.target.value) || 10})}
            />
          </label>
          <span className="multiplier">x</span>
          <label className="conf-step__label">
            Мест, шт
            <input 
              type="number" 
              className="conf-step__input" 
              placeholder="8" 
              min="1"
              max="30"
              value={hallConfig.seatsPerRow}
              onChange={(e) => setHallConfig({...hallConfig, seatsPerRow: parseInt(e.target.value) || 8})}
            />
          </label>
        </div>
        
        <p className="conf-step__paragraph">
          Теперь вы можете указать типы кресел на схеме зала:
        </p>
        <div className="conf-step__legend flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <span className="conf-step__chair conf-step__chair_standart"></span>
            <span>— обычные кресла (клик для смены)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="conf-step__chair conf-step__chair_vip"></span>
            <span>— VIP кресла</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="conf-step__chair conf-step__chair_disabled"></span>
            <span>— заблокированные</span>
          </div>
        </div>
        <p className="conf-step__hint text-sm text-gray-600 mt-2">
          💡 Чтобы изменить вид кресла, нажмите по нему левой кнопкой мыши. 
          Тип меняется по циклу: обычное → VIP → заблокированное → обычное
        </p>

        {/* Схема зала */}
        {selectedHall && halls.length > 0 && (
          <div className="mt-6">
            <SeatGrid
              seatsByRow={seatsByRow()}
              onSeatClick={handleSeatClick}
            />
          </div>
        )}

        <fieldset className="conf-step__buttons text-center mt-6">
          <button className="conf-step__button conf-step__button-regular">Отмена</button>
          <button 
            onClick={handleSaveConfig}
            className="conf-step__button conf-step__button-accent"
          >
            Сохранить
          </button>
        </fieldset>
      </AccordionSection>
    </div>
  );
};

export default AdminHalls;