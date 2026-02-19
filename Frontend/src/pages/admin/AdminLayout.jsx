import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Notification from '../../components/ui/Notification';

const AdminLayout = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [notification, setNotification] = useState(null);

  const menuItems = [
    { path: '/admin', label: 'Дашборд', icon: '📊' },
    { path: '/admin/halls', label: 'Залы', icon: '🎬' },
    { path: '/admin/movies', label: 'Фильмы', icon: '📽️' },
    { path: '/admin/screenings', label: 'Сеансы', icon: '⏰' },
    { path: '/admin/bookings', label: 'Бронирования', icon: '🎫' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Уведомления */}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}

      {/* Верхняя панель */}
      <header className="bg-secondary text-white shadow-lg">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold">Администраторррская</h1>
              <span className="text-sm opacity-75">{user?.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 transition"
            >
              Выйти
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Боковое меню */}
        <aside className="w-64 bg-white shadow-lg min-h-screen">
          <nav className="p-4">
            {menuItems.map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-lg mb-2 transition ${
                    isActive
                      ? 'bg-primary text-white'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`
                }
                end={item.path === '/admin'}
              >
                <span className="text-xl">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Основной контент */}
        <main className="flex-1 p-8">
          <Outlet context={{ setNotification }} />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;