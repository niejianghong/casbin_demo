import { apiClient } from './apiClient';

export interface Resource {
  id: number;
  name: string;
  code: string;
  type: number;  // 1-API, 2-Menu, 3-Agent
  parent_code?: string;
  path?: string;
  act?: string;
  status: number;
  create_time: string;
  update_time: string;
  children?: Resource[];
}

export interface ResourceCreate {
  name: string;
  code: string;
  type: number;  // 1-API, 2-Menu, 3-Agent
  parent_code?: string;
  path?: string;
  act?: string;
  status: number;
}

export interface ResourceUpdate {
  name?: string;
  code?: string;
  type?: number;  // 1-API, 2-Menu, 3-Agent
  parent_code?: string;
  path?: string;
  act?: string;
  status?: number;
}

export interface ResourceSearch {
  name?: string;
  code?: string;
  type?: string;
  enterprise_code?: string;
  status?: number;
}

export const resourceService = {
  // 获取资源列表
  getResources: () => {
    return apiClient.get<Resource[]>('/api/v1/resources/');
  },

  // 根据代码获取资源
  getResourceByCode: (code: string) => {
    return apiClient.get<Resource>(`/api/v1/resources/${code}`);
  },

  // 创建资源
  createResource: (data: ResourceCreate) => {
    return apiClient.post<Resource>('/api/v1/resources/', data);
  },

  // 更新资源
  updateResource: (code: string, data: ResourceUpdate) => {
    return apiClient.put<Resource>(`/api/v1/resources/${code}`, data);
  },

  // 删除资源
  deleteResource: (code: string) => {
    return apiClient.delete(`/api/v1/resources/${code}`);
  },

  // 搜索资源
  searchResources: (params: ResourceSearch) => {
    return apiClient.get<Resource[]>('/api/v1/resources/search', { params });
  },

  // 获取企业下的资源
  getResourcesByEnterprise: (enterpriseCode: string) => {
    return apiClient.get<Resource[]>(`/api/v1/resources/enterprise/${enterpriseCode}`);
  },

  // 获取资源树
  getResourceTree: (enterpriseCode?: string) => {
    const params = enterpriseCode ? { enterprise_code: enterpriseCode } : {};
    return apiClient.get<Resource[]>('/api/v1/resources/tree', { params });
  },

  // 分配资源到角色
  assignResourceToRole: (resourceCode: string, roleCode: string) => {
    return apiClient.post('/api/v1/resources/assign-role', {
      resource_code: resourceCode,
      role_code: roleCode
    });
  },

  // 移除资源角色关系
  removeResourceFromRole: (resourceCode: string, roleCode: string) => {
    return apiClient.delete('/api/v1/resources/remove-role', {
      data: {
        resource_code: resourceCode,
        role_code: roleCode
      }
    });
  },

  // 获取角色的资源
  getResourcesByRole: (roleCode: string) => {
    return apiClient.get<Resource[]>(`/api/v1/resources/role/${roleCode}`);
  }
}; 