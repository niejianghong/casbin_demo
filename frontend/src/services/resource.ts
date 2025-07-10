import api from './api';
import { Resource, PaginatedResponse, MenuItem } from '../types';

export const resourceService = {
  // 获取资源列表
  getResources: async (page: number = 1, size: number = 100, resourceType?: number, enterpriseCode?: string): Promise<PaginatedResponse<{ resources: Resource[] }>> => {
    const params: any = { skip: (page - 1) * size, limit: size };
    if (resourceType) {
      params.resource_type = resourceType;
    }
    if (enterpriseCode) {
      params.enterprise_code = enterpriseCode;
    }
    return api.get('/v1/resources/', { params });
  },

  // 获取资源详情
  getResource: async (resourceId: number): Promise<Resource> => {
    return api.get(`/v1/resources/${resourceId}`);
  },

  // 创建资源
  createResource: async (data: any): Promise<Resource> => {
    return api.post('/v1/resources', data);
  },

  // 更新资源
  updateResource: async (resourceId: number, data: any): Promise<Resource> => {
    return api.put(`/v1/resources/${resourceId}`, data);
  },

  // 删除资源
  deleteResource: async (resourceId: number): Promise<any> => {
    return api.delete(`/v1/resources/${resourceId}`);
  },

  // 分配资源到角色
  assignResourceToRoles: async (data: { resource_code: string, role_codes: string[] }): Promise<any> => {
    return api.post('/v1/resources/assign-role', data);
  },

  // 分配资源到企业
  assignResourceToEnterprises: async (data: { resource_code: string, enterprise_codes: string[] }): Promise<any> => {
    return api.post('/v1/resources/assign-enterprise', data);
  },

  // 获取资源的企业列表
  getResourceEnterprises: async (resourceCode: string): Promise<any> => {
    return api.get(`/v1/resources/${resourceCode}/enterprises`);
  },

  // 获取企业的资源列表
  getEnterpriseResources: async (enterpriseCode: string): Promise<any> => {
    return api.get(`/v1/resources/enterprise/${enterpriseCode}`);
  },

  // 获取菜单树
  getMenuTree: async (enterpriseCode?: string): Promise<{ menu_tree: MenuItem[] }> => {
    const params: any = {};
    if (enterpriseCode) params.enterprise_code = enterpriseCode;
    return api.get('/v1/resources/menu/tree', { params });
  },

  // 获取活跃资源列表
  getActiveResources: async (enterpriseCode?: string): Promise<Resource[]> => {
    const params: any = {};
    if (enterpriseCode) params.enterprise_code = enterpriseCode;
    return api.get('/v1/resources/active/list', { params });
  },

  // 获取角色的资源列表
  getRoleResources: async (roleCode: string): Promise<any> => {
    return api.get(`/v1/resources/role/${roleCode}`);
  },

  // 为角色添加资源
  addResourcesToRole: async (roleCode: string, data: { resource_codes: string[] }): Promise<any> => {
    return api.post(`/v1/resources/role/${roleCode}/add-resources`, data);
  },

  // 从角色移除资源
  removeResourcesFromRole: async (roleCode: string, data: { resource_codes: string[] }): Promise<any> => {
    return api.delete(`/v1/resources/role/${roleCode}/remove-resources`, { data });
  }
}; 