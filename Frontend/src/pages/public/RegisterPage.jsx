import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
    phone: '',
  });
  const [errors, setErrors] = useState({});
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Очищаем ошибку для этого поля
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: null
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Базовая валидация
    if (formData.password !== formData.password2) {
      setErrors({ password2: 'Пароли не совпадают' });
      return;
    }

    const result = await register(formData);
    
    if (result.success) {
      // После успешной регистрации перенаправляем на страницу входа
      navigate('/login', { 
        state: { message: 'Регистрация успешна! Теперь вы можете войти.' }
      });
    } else {
      setErrors(result.error || {});
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-cover bg-center py-12"
         style={{backgroundImage: 'url(/src/assets/background.jpg)'}}>
      <div className="bg-white bg-opacity-95 p-8 rounded-lg w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black uppercase text-secondary">
            Идём<span className="font-thin">в</span>кино
          </h1>
          <p className="text-sm tracking-widest text-gray-600 mt-2">Регистрация</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Имя пользователя */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Имя пользователя *
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
                errors.username ? 'border-red-500' : 'border-gray-300'
              }`}
              required
            />
            {errors.username && (
              <p className="text-red-500 text-xs mt-1">{errors.username}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
                errors.email ? 'border-red-500' : 'border-gray-300'
              }`}
              required
            />
            {errors.email && (
              <p className="text-red-500 text-xs mt-1">{errors.email}</p>
            )}
          </div>

          {/* Имя и фамилия */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Имя
              </label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Фамилия
              </label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Телефон */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Телефон
            </label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+7 (999) 123-45-67"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Пароль */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Пароль *
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
                errors.password ? 'border-red-500' : 'border-gray-300'
              }`}
              required
            />
            {errors.password && (
              <p className="text-red-500 text-xs mt-1">{errors.password}</p>
            )}
          </div>

          {/* Подтверждение пароля */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Подтверждение пароля *
            </label>
            <input
              type="password"
              name="password2"
              value={formData.password2}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
                errors.password2 ? 'border-red-500' : 'border-gray-300'
              }`}
              required
            />
            {errors.password2 && (
              <p className="text-red-500 text-xs mt-1">{errors.password2}</p>
            )}
          </div>

          {/* Общая ошибка */}
          {errors.non_field_errors && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {errors.non_field_errors}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-primary text-white py-3 px-4 rounded-md hover:bg-opacity-90 transition text-lg font-semibold mt-6"
          >
            Зарегистрироваться
          </button>
        </form>

        <p className="mt-6 text-center text-gray-600">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="text-primary hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;