import { describe, it, expect, vi } from 'vitest';
import api from '../services/api';

describe('API Service', () => {
  it('should be defined', () => {
    expect(api).toBeDefined();
  });

  it('should have interceptors', () => {
    expect(api.interceptors).toBeDefined();
    expect(api.interceptors.request).toBeDefined();
    expect(api.interceptors.response).toBeDefined();
  });

  it('should have default headers', () => {
    expect(api.defaults.headers).toBeDefined();
    expect(api.defaults.headers['Content-Type']).toBe('application/json');
  });
});