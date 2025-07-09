import api from './api';
import { User, PaginatedResponse } from '../types';

export const userService = {
  // 获取用户列表
  getUsers: async (page: number = 1, size: number = 100): Promise<PaginatedResponse<{ users: User[] }>> => {
    return api.get('/v1/users/', { params: { skip: (page - 1) * size, limit: size } });
  },

  // 获取用户详情
  getUser: async (userId: number): Promise<User> => {
    return api.get(`/v1/users/${userId}`);
  },

  // 创建用户
  createUser: async (data: any): Promise<User> => {
    return api.post('/v1/users', data);
  },

  // 更新用户
  updateUser: async (userId: number, data: any): Promise<User> => {
    return api.put(`/v1/users/${userId}`, data);
  },

  // 删除用户
  deleteUser: async (userId: number): Promise<any> => {
    return api.delete(`/v1/users/${userId}`);
  },

  // 分配用户到企业
  assignUsersToEnterprise: async (data: { user_ids: number[], enterprise_code: string, status: number }): Promise<any> => {
    return api.post('/v1/users/assign-enterprise', data);
  },

  // 获取企业下的用户
  getUsersByEnterprise: async (enterpriseCode: string): Promise<User[]> => {
    return api.get(`/v1/users/enterprise/${enterpriseCode}`);
  },

  // 为用户分配角色
  assignRoleToUser: async (data: { user_id: number, role_id: number }): Promise<any> => {
    return api.post('/v1/users/assign-role', data);
  },

  // 移除用户角色
  removeRoleFromUser: async (data: { user_id: number, role_id: number }): Promise<any> => {
    return api.delete('/v1/users/remove-role', { data });
  },

  // 获取用户的角色列表
  getUserRoles: async (userId: number): Promise<any> => {
    return api.get(`/v1/users/${userId}/roles`);
  }
}; 