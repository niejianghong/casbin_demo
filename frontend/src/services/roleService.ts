import { apiClient } from './apiClient';

export interface Role {
  id: number;
  name: string;
  code: string;
  description: string;
  status: number;
  enterprise_code: string;
  create_time: string;
  update_time: string;
}

export interface RoleCreate {
  name: string;
  code: string;
  description?: string;
  status: number;
  enterprise_code: string;
}

export interface RoleUpdate {
  name?: string;
  code?: string;
  description?: string;
  status?: number;
  enterprise_code?: string;
}

export interface RoleSearch {
  name?: string;
  code?: string;
  enterprise_code?: string;
  status?: number;
}

export const roleService = {
  // 获取角色列表
  getRoles: () => {
    return apiClient.get<Role[]>('/api/v1/roles/');
  },

  // 根据ID获取角色
  getRoleById: (id: number) => {
    return apiClient.get<Role>(`/api/v1/roles/${id}`);
  },

  // 创建角色
  createRole: (data: RoleCreate) => {
    return apiClient.post<Role>('/api/v1/roles/', data);
  },

  // 更新角色
  updateRole: (id: number, data: RoleUpdate) => {
    return apiClient.put<Role>(`/api/v1/roles/${id}`, data);
  },

  // 删除角色
  deleteRole: (id: number) => {
    return apiClient.delete(`/api/v1/roles/${id}`);
  },

  // 搜索角色
  searchRoles: (params: RoleSearch) => {
    return apiClient.get<Role[]>('/api/v1/roles/search', { params });
  },

  // 获取企业下的角色
  getRolesByEnterprise: (enterpriseCode: string) => {
    return apiClient.get<Role[]>(`/api/v1/roles/enterprise/${enterpriseCode}`);
  },

  // 分配角色到企业
  assignRoleToEnterprise: (roleCode: string, enterpriseCode: string) => {
    return apiClient.post('/api/v1/roles/assign-enterprise', {
      role_code: roleCode,
      enterprise_code: enterpriseCode
    });
  },

  // 移除角色企业关系
  removeRoleFromEnterprise: (roleCode: string, enterpriseCode: string) => {
    return apiClient.delete('/api/v1/roles/remove-enterprise', {
      data: {
        role_code: roleCode,
        enterprise_code: enterpriseCode
      }
    });
  }
}; 