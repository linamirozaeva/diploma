import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Header = () => {
  const { isAuthenticated, user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="page-header py-4 px-8">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white no-underline">
          <h1 className="text-4xl font-black uppercase m-0">
            Идём<span className="font-thin">в</span>кино
          </h1>
        </Link>
        
        <nav className="flex gap-6">
          <Link to="/" className="text-white hover:text-primary transition">
            Расписание
          </Link>
          <Link to="/movies" className="text-white hover:text-primary transition">
            Фильмы
          </Link>
          
          {isAuthenticated ? (
            <div className="relative group">
              <button className="text-white hover:text-primary transition">
                {user?.username}
              </button>
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg hidden group-hover:block">
                {isAdmin && (
                  <Link 
                    to="/admin" 
                    className="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                  >
                    Админ панель
                  </Link>
                )}
                <Link 
                  to="/my-tickets" 
                  className="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                >
                  Мои билеты
                </Link>
                <button 
                  onClick={logout}
                  className="block w-full text-left px-4 py-2 text-gray-800 hover:bg-gray-100"
                >
                  Выйти
                </button>
              </div>
            </div>
          ) : (
            <button 
              onClick={() => navigate('/login')}
              className="text-white hover:text-primary transition"
            >
              Войти
            </button>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;