import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Header = () => {
  const { isAuthenticated, user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    console.log('Header - Auth state detailed:', { 
      isAuthenticated, 
      user, 
      isAdmin,
      userType: user?.user_type,
      isStaff: user?.is_staff
    });
  }, [isAuthenticated, user, isAdmin]);

  // Закрытие дропдауна при клике вне его
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  console.log('Auth state:', { user, isAdmin, isAuthenticated });

  return (
    <header className="page-header py-4 px-8">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white no-underline">
          <h1 className="text-4xl font-black uppercase m-0">
            Идём<span className="font-thin">в</span>кино
          </h1>
        </Link>
        
        <nav className="flex gap-6 items-center">
          <Link to="/" className="text-white hover:text-primary transition">
            Расписание
          </Link>
          <Link to="/" className="text-white hover:text-primary transition">
            Фильмы
          </Link>
          
          {isAuthenticated ? (
            <div className="relative" ref={dropdownRef}>
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="text-white hover:text-primary transition flex items-center gap-1"
              >
                {user?.username}
                <svg 
                  className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {/* Дропдаун с высоким z-index */}
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                  {/* Ссылка на админ-панель - видна только администраторам */}
                  {isAdmin && (
                    <Link 
                      to="/admin" 
                      className="block px-4 py-2 text-gray-800 hover:bg-gray-100 transition"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Админ панель
                    </Link>
                  )}
                  <Link 
                    to="/my-tickets" 
                    className="block px-4 py-2 text-gray-800 hover:bg-gray-100 transition"
                    onClick={() => setIsDropdownOpen(false)}
                  >
                    Мои билеты
                  </Link>
                  <button 
                    onClick={() => {
                      logout();
                      setIsDropdownOpen(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-gray-800 hover:bg-gray-100 transition"
                  >
                    Выйти
                  </button>
                </div>
              )}
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