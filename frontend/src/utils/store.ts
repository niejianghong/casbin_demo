import { create } from 'zustand';
import { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  enterpriseCode: string | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  setEnterpriseCode: (code: string) => void;
  logout: () => void;
}

// 从localStorage读取初始状态
const getInitialState = () => {
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  const enterpriseCode = localStorage.getItem('enterprise_code');
  
  let user = null;
  if (userStr) {
    try {
      user = JSON.parse(userStr);
    } catch (e) {
      console.error('Failed to parse user from localStorage:', e);
    }
  }
  
  return {
    user,
    token,
    enterpriseCode,
    isAuthenticated: !!token
  };
};

export const useAuthStore = create<AuthState>((set) => ({
  ...getInitialState(),
  setUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user));
    set({ user, isAuthenticated: true });
  },
  setToken: (token) => {
    localStorage.setItem('token', token);
    set({ token, isAuthenticated: true });
  },
  setEnterpriseCode: (enterpriseCode) => {
    localStorage.setItem('enterprise_code', enterpriseCode);
    set({ enterpriseCode });
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('enterprise_code');
    set({ user: null, token: null, enterpriseCode: null, isAuthenticated: false });
  },
})); 