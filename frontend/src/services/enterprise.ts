import api from './api';
import { Enterprise, PaginatedResponse } from '../types';

export const enterpriseService = {
  // 获取企业列表
  getEnterprises: async (page: number = 1, size: number = 10): Promise<PaginatedResponse<{ enterprises: Enterprise[] }>> => {
    return api.get('/v1/enterprises', { params: { skip: (page - 1) * size, limit: size } });
  },

  // 获取企业详情
  getEnterprise: async (enterpriseId: number): Promise<Enterprise> => {
    return api.get(`/v1/enterprises/${enterpriseId}`);
  },

  // 创建企业
  createEnterprise: async (data: any): Promise<Enterprise> => {
    return api.post('/v1/enterprises', data);
  },

  // 更新企业
  updateEnterprise: async (enterpriseId: number, data: any): Promise<Enterprise> => {
    return api.put(`/v1/enterprises/${enterpriseId}`, data);
  },

  // 删除企业
  deleteEnterprise: async (enterpriseId: number): Promise<any> => {
    return api.delete(`/v1/enterprises/${enterpriseId}`);
  },

  // 获取活跃企业列表
  getActiveEnterprises: async (): Promise<Enterprise[]> => {
    return api.get('/v1/enterprises/active/list');
  },

  // 获取企业下的用户
  getEnterpriseUsers: async (enterpriseCode: string): Promise<any> => {
    return api.get(`/v1/enterprises/${enterpriseCode}/users`);
  },

  // 为企业添加用户
  addUsersToEnterprise: async (enterpriseCode: string, data: { user_ids: number[], status: number }): Promise<any> => {
    return api.post(`/v1/enterprises/${enterpriseCode}/add-users`, data);
  },

  // 从企业移除用户
  removeUsersFromEnterprise: async (enterpriseCode: string, data: { user_ids: number[] }): Promise<any> => {
    return api.delete(`/v1/enterprises/${enterpriseCode}/remove-users`, { data });
  },

  // 获取企业的角色列表
  getEnterpriseRoles: async (enterpriseCode: string): Promise<any> => {
    return api.get(`/v1/enterprises/${enterpriseCode}/roles`);
  },

  // 为企业添加角色
  addRolesToEnterprise: async (enterpriseCode: string, data: { role_codes: string[] }): Promise<any> => {
    return api.post(`/v1/enterprises/${enterpriseCode}/add-roles`, data);
  },

  // 从企业移除角色
  removeRolesFromEnterprise: async (enterpriseCode: string, data: { role_codes: string[] }): Promise<any> => {
    return api.delete(`/v1/enterprises/${enterpriseCode}/remove-roles`, { data });
  }
}; 