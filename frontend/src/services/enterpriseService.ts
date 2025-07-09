import { apiClient } from './apiClient';

export interface Enterprise {
  id: number;
  code: string;
  name: string;
  description?: string;
  status: number;
  create_time: string;
  update_time: string;
}

export interface EnterpriseCreate {
  code: string;
  name: string;
  description?: string;
  status: number;
}

export interface EnterpriseUpdate {
  code?: string;
  name?: string;
  description?: string;
  status?: number;
}

export const enterpriseService = {
  // 获取企业列表
  getEnterprises: () => {
    return apiClient.get<Enterprise[]>('/api/v1/enterprises/');
  },

  // 根据ID获取企业
  getEnterpriseById: (id: number) => {
    return apiClient.get<Enterprise>(`/api/v1/enterprises/${id}`);
  },

  // 创建企业
  createEnterprise: (data: EnterpriseCreate) => {
    return apiClient.post<Enterprise>('/api/v1/enterprises/', data);
  },

  // 更新企业
  updateEnterprise: (id: number, data: EnterpriseUpdate) => {
    return apiClient.put<Enterprise>(`/api/v1/enterprises/${id}`, data);
  },

  // 删除企业
  deleteEnterprise: (id: number) => {
    return apiClient.delete(`/api/v1/enterprises/${id}`);
  },

  // 获取活跃企业列表
  getActiveEnterprises: () => {
    return apiClient.get<Enterprise[]>('/api/v1/enterprises/active/list');
  },

  // 搜索企业
  searchEnterprises: (params: any) => {
    return apiClient.get<Enterprise[]>('/api/v1/enterprises/search', { params });
  }
}; 