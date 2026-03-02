import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/AuthContext';

// Мокаем api
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { user: null } })
  }
}));

// Тестовый компонент для использования хука
const TestComponent = () => {
  const auth = useAuth();
  return (
    <div>
      <div data-testid="auth-status">{auth.isAuthenticated ? 'true' : 'false'}</div>
      <div data-testid="user">{auth.user ? auth.user.username : 'null'}</div>
    </div>
  );
};

describe('AuthContext', () => {
  it('provides initial auth state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('false');
    expect(screen.getByTestId('user')).toHaveTextContent('null');
  });
});