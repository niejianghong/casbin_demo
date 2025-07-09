import api from './api';
import { Resource, PaginatedResponse, MenuItem } from '../types';

export const resourceService = {
  // 获取资源列表
  getResources: async (page: number = 1, size: number = 100, resourceType?: number): Promise<PaginatedResponse<{ resources: Resource[] }>> => {
    const params: any = { skip: (page - 1) * size, limit: size };
    if (resourceType) {
      params.resource_type = resourceType;
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

  // 获取菜单树
  getMenuTree: async (): Promise<{ menu_tree: MenuItem[] }> => {
    return api.get('/v1/resources/menu/tree');
  },

  // 获取活跃资源列表
  getActiveResources: async (): Promise<Resource[]> => {
    return api.get('/v1/resources/active/list');
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