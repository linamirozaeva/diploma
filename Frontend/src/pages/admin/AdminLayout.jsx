import React, { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Notification from '../../components/ui/Notification';

const AdminLayout = () => {
  const { user, logout } = useAuth();
  const [notification, setNotification] = useState(null);

  return (
    <div className="admin-layout">
      {/* Уведомления */}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}

      <header className="page-header">
        <h1 className="page-header__title">Идём<span>в</span>кино</h1>
        <span className="page-header__subtitle">Администраторррская</span>
        <div className="admin-user absolute top-4 right-4 flex items-center gap-4">
          <span className="text-white">{user?.username}</span>
          <button 
            onClick={logout}
            className="conf-step__button conf-step__button-regular"
          >
            Выйти
          </button>
        </div>
      </header>

      <nav className="admin-nav flex gap-2 px-8 py-4 bg-white bg-opacity-95">
        <NavLink 
          to="/admin" 
          end
          className={({ isActive }) => 
            `px-4 py-2 rounded transition ${
              isActive 
                ? 'bg-primary text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`
          }
        >
          Дашборд
        </NavLink>
        <NavLink 
          to="/admin/halls" 
          className={({ isActive }) => 
            `px-4 py-2 rounded transition ${
              isActive 
                ? 'bg-primary text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`
          }
        >
          Залы
        </NavLink>
        <NavLink 
          to="/admin/movies" 
          className={({ isActive }) => 
            `px-4 py-2 rounded transition ${
              isActive 
                ? 'bg-primary text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`
          }
        >
          Фильмы
        </NavLink>
        <NavLink 
          to="/admin/screenings" 
          className={({ isActive }) => 
            `px-4 py-2 rounded transition ${
              isActive 
                ? 'bg-primary text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`
          }
        >
          Сеансы
        </NavLink>
        <NavLink 
          to="/admin/bookings" 
          className={({ isActive }) => 
            `px-4 py-2 rounded transition ${
              isActive 
                ? 'bg-primary text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`
          }
        >
          Бронирования
        </NavLink>
      </nav>

      {/* Передаем setNotification через контекст Outlet */}
      <main className="conf-steps">
        <Outlet context={{ setNotification }} />
      </main>
    </div>
  );
};

export default AdminLayout;