import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from '../pages/public/HomePage';
import LoginPage from '../pages/public/LoginPage';

// Мокаем API
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ 
      data: [
        { 
          id: 1, 
          title: 'Тестовый фильм', 
          duration: 120,
          description: 'Описание',
          poster_url: null,
          country: 'Россия'
        }
      ] 
    })
  }
}));

// Мокаем useAuth
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: false,
    login: vi.fn(),
    register: vi.fn()
  })
}));

describe('HomePage', () => {
  it('renders loading state initially', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/Загрузка/i)).toBeInTheDocument();
  });

  it('renders movies after loading', async () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Тестовый фильм')).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});

describe('LoginPage', () => {
  it('renders login form', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    const usernameInput = document.querySelector('input[type="text"]');
    const passwordInput = document.querySelector('input[type="password"]');
    const submitButton = screen.getByRole('button', { name: /Войти/i });
    
    expect(usernameInput).toBeInTheDocument();
    expect(passwordInput).toBeInTheDocument();
    expect(submitButton).toBeInTheDocument();
  });

  it('has link to register page', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/Зарегистрироваться/i)).toBeInTheDocument();
  });
});