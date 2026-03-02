import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from '../components/layout/Header';
import Notification from '../components/ui/Notification';

// Мокаем useAuth
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { username: 'testuser' },
    isAdmin: true,
    logout: vi.fn()
  })
}));

describe('Header Component', () => {
  it('renders logo correctly', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/Идём/i)).toBeInTheDocument();
  });

  it('shows username when authenticated', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
    
    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  it('shows admin link for admin users', async () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
    
    const userButton = screen.getByText('testuser');
    fireEvent.click(userButton);
    
    expect(await screen.findByText(/Админ панель/i)).toBeInTheDocument();
  });
});

describe('Notification Component', () => {
  it('renders success message', () => {
    const onClose = vi.fn();
    render(
      <Notification 
        message="Успех!" 
        type="success" 
        onClose={onClose} 
      />
    );
    
    expect(screen.getByText('Успех!')).toBeInTheDocument();
  });

  it('renders error message', () => {
    const onClose = vi.fn();
    render(
      <Notification 
        message="Ошибка!" 
        type="error" 
        onClose={onClose} 
      />
    );
    
    expect(screen.getByText('Ошибка!')).toBeInTheDocument();
  });
});