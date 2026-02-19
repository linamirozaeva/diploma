import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../../services/api';

const AdminHalls = () => {
  const [halls, setHalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingHall, setEditingHall] = useState(null);
  const { setNotification } = useOutletContext();
  
  const [formData, setFormData] = useState({
    name: '',
    rows: 10,
    seats_per_row: 12,
    description: '',
  });

  useEffect(() => {
    fetchHalls();
  }, []);

  const fetchHalls = async () => {
    try {
      const response = await api.get('/cinemas/halls/');
      setHalls(response.data);
    } catch (error) {
      setNotification({
        message: 'Ошибка загрузки залов: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingHall) {
        await api.put(`/cinemas/halls/${editingHall.id}/`, formData);
        setNotification({ message: 'Зал успешно обновлен!', type: 'success' });
      } else {
        await api.post('/cinemas/halls/', formData);
        setNotification({ message: 'Зал успешно создан!', type: 'success' });
      }
      fetchHalls();
      setShowModal(false);
      resetForm();
    } catch (error) {
      setNotification({
        message: 'Ошибка сохранения: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Вы уверены, что хотите удалить этот зал?')) {
      try {
        await api.delete(`/cinemas/halls/${id}/`);
        setNotification({ message: 'Зал успешно удален!', type: 'success' });
        fetchHalls();
      } catch (error) {
        setNotification({
          message: 'Ошибка удаления: ' + (error.response?.data?.detail || error.message),
          type: 'error'
        });
      }
    }
  };

  const handleEdit = (hall) => {
    setEditingHall(hall);
    setFormData({
      name: hall.name,
      rows: hall.rows,
      seats_per_row: hall.seats_per_row,
      description: hall.description || '',
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setEditingHall(null);
    setFormData({
      name: '',
      rows: 10,
      seats_per_row: 12,
      description: '',
    });
  };

  const getSeatGrid = (hall) => {
    const seats = [];
    for (let row = 1; row <= hall.rows; row++) {
      const rowSeats = [];
      for (let seat = 1; seat <= hall.seats_per_row; seat++) {
        rowSeats.push(
          <div
            key={`${row}-${seat}`}
            className="w-6 h-6 bg-white border border-gray-300 rounded-sm inline-block mr-1 mb-1 hover:bg-gray-100 transition"
            title={`Ряд ${row}, Место ${seat}`}
          />
        );
      }
      seats.push(
        <div key={row} className="flex justify-center mb-1">
          {rowSeats}
        </div>
      );
    }
    return seats;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold">Управление залами</h2>
        <button
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
          className="bg-primary text-white px-4 py-2 rounded hover:bg-opacity-90 transition flex items-center gap-2"
        >
          <span>➕</span> Добавить зал
        </button>
      </div>

      {/* Список залов */}
      <div className="grid grid-cols-1 gap-6">
        {halls.map(hall => (
          <div key={hall.id} className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-2xl font-bold">{hall.name}</h3>
                <p className="text-gray-600">
                  Рядов: {hall.rows} | Мест в ряду: {hall.seats_per_row} | Всего мест: {hall.total_seats}
                </p>
                {hall.description && (
                  <p className="text-gray-500 mt-2">{hall.description}</p>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(hall)}
                  className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                  title="Редактировать"
                >
                  ✏️
                </button>
                <button
                  onClick={() => handleDelete(hall.id)}
                  className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition"
                  title="Удалить"
                >
                  🗑️
                </button>
              </div>
            </div>

            {/* Схема зала */}
            <div className="mt-4 p-4 bg-gray-100 rounded-lg overflow-x-auto">
              <div className="text-center mb-4">
                <div className="inline-block px-8 py-2 bg-gray-300 rounded-t-lg text-sm font-semibold">
                  ЭКРАН
                </div>
              </div>
              <div className="flex flex-col items-center">
                {getSeatGrid(hall)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Модальное окно */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-2xl font-bold mb-4">
              {editingHall ? 'Редактировать зал' : 'Новый зал'}
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название зала *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                  placeholder="Например: Зал 1"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Рядов *
                  </label>
                  <input
                    type="number"
                    name="rows"
                    value={formData.rows}
                    onChange={handleInputChange}
                    min="1"
                    max="20"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Мест в ряду *
                  </label>
                  <input
                    type="number"
                    name="seats_per_row"
                    value={formData.seats_per_row}
                    onChange={handleInputChange}
                    min="1"
                    max="30"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Описание
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Дополнительная информация о зале"
                />
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-opacity-90 transition"
                >
                  {editingHall ? 'Сохранить' : 'Создать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminHalls;