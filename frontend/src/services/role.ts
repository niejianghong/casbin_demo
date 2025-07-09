import api from './api';
import { Role, PaginatedResponse } from '../types';

export const roleService = {
  // 获取角色列表
  getRoles: async (page: number = 1, size: number = 10): Promise<PaginatedResponse<{ roles: Role[] }>> => {
    return api.get('/v1/roles', { params: { skip: (page - 1) * size, limit: size } });
  },

  // 获取角色详情
  getRole: async (roleId: number): Promise<Role> => {
    return api.get(`/v1/roles/${roleId}`);
  },

  // 创建角色
  createRole: async (data: any): Promise<Role> => {
    return api.post('/v1/roles', data);
  },

  // 更新角色
  updateRole: async (roleId: number, data: any): Promise<Role> => {
    return api.put(`/v1/roles/${roleId}`, data);
  },

  // 删除角色
  deleteRole: async (roleId: number): Promise<any> => {
    return api.delete(`/v1/roles/${roleId}`);
  },

  // 分配角色到企业
  assignRoleToEnterprises: async (data: { role_code: string, enterprise_codes: string[] }): Promise<any> => {
    return api.post('/v1/roles/assign-enterprise', data);
  },

  // 获取企业下的角色
  getRolesByEnterprise: async (enterpriseCode: string): Promise<Role[]> => {
    return api.get(`/v1/roles/enterprise/${enterpriseCode}`);
  },

  // 获取活跃角色列表
  getActiveRoles: async (): Promise<Role[]> => {
    return api.get('/v1/roles/active/list');
  },

  // 为角色分配用户
  assignUsersToRole: async (roleId: number, data: { user_ids: number[] }): Promise<any> => {
    return api.post(`/v1/roles/${roleId}/assign-users`, data);
  },

  // 移除角色的用户
  removeUsersFromRole: async (roleId: number, data: { user_ids: number[] }): Promise<any> => {
    return api.delete(`/v1/roles/${roleId}/remove-users`, { data });
  },

  // 获取角色的用户列表
  getRoleUsers: async (roleId: number): Promise<any> => {
    return api.get(`/v1/roles/${roleId}/users`);
  }
}; 