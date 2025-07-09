import axios from 'axios';
import { message } from 'antd';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    console.log('请求拦截器 - Token:', token);
    console.log('请求URL:', config.url);
    console.log('请求拦截器 headers:', config.headers, config.url);
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('已添加Authorization头:', config.headers.Authorization);
    } else {
      console.log('未找到token，跳过认证');
    }
    
    return config;
  },
  (error) => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('响应成功:', response.config.url, response.data);
    return response.data;
  },
  (error) => {
    console.error('响应错误:', error.config?.url, error.response?.status, error.response?.data);
    
    if (error.response?.status === 401) {
      message.error('登录已过期，请重新登录');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('enterprise_code');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      message.error('权限不足，请检查您的权限');
    } else {
      message.error(error.response?.data?.detail || '请求失败');
    }
    return Promise.reject(error);
  }
);

export default api; 