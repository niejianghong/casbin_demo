import api from './api';
import { UserLogin, UserLoginResponse, User } from '../types';

export const authService = {
  // 用户登录
  login: async (data: UserLogin): Promise<UserLoginResponse> => {
    return api.post('/auth/login', data);
  },

  // 用户注册
  register: async (data: any): Promise<User> => {
    return api.post('/auth/register', data);
  },

  // 获取当前用户信息
  getCurrentUser: async (): Promise<User> => {
    return api.get('/auth/me');
  },

  // 登出
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('enterprise_code');
  },

  // 检查是否已登录
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('token');
  },

  // 获取token
  getToken: (): string | null => {
    return localStorage.getItem('token');
  },

  // 获取用户信息
  getUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // 获取企业代码
  getEnterpriseCode: (): string | null => {
    return localStorage.getItem('enterprise_code');
  }
}; 