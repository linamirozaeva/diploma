import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    console.log('Token from localStorage:', token);
    
    if (token) {
      try {
        const response = await api.get('/auth/me/');
        console.log('User data from API:', response.data);
        
        setUser(response.data);
        setIsAuthenticated(true);
        
        const isUserAdmin = response.data?.user_type === 'admin' || response.data?.is_staff || false;
        console.log('Is user admin?', isUserAdmin);
        
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    setLoading(false);
  };

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login/', {
        username,
        password,
      });
      
      console.log('Login response:', response.data); // Проверка токенов
      
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      await checkAuth();
      return { success: true };
    } catch (error) {
      console.error('Login error:', error.response?.data);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Ошибка входа' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register/', userData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Ошибка регистрации' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
    window.location.href = '/';
  };

  const isAdmin = user?.user_type === 'admin' || user?.is_staff || false;

  console.log('AuthProvider state:', { user, isAuthenticated, isAdmin, loading }); // Общий лог

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      isAuthenticated,
      login,
      register,
      logout,
      isAdmin,
    }}>
      {children}
    </AuthContext.Provider>
  );
};