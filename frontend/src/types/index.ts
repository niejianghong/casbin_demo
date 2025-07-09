// 用户相关类型
export interface User {
  user_id: number;
  user_name: string;
  email?: string;
  phone_number?: string;
  nick_name?: string;
  is_admin: number;
  status: number;
  icon?: string;
  third_uid: string;
  create_time: string;
  update_time: string;
}

export interface UserLogin {
  user_name: string;
  password: string;
  enterprise_code: string;
}

export interface UserLoginResponse {
  access_token: string;
  token_type: string;
  user: User;
  enterprise_code: string;
}

// 企业相关类型
export interface Enterprise {
  id: number;
  code: string;
  name: string;
  icon?: string;
  description?: string;
  status: number;
  create_time: string;
  update_time: string;
}

// 角色相关类型
export interface Role {
  id: number;
  name: string;
  description?: string;
  code: string;
  status: number;
  create_time: string;
  update_time: string;
}

// 资源相关类型
export interface Resource {
  id: number;
  name?: string;
  code?: string;
  type?: number; // 1-API, 2-Menu, 3-Agent
  path?: string;
  act?: string;
  parent_code?: string;
  status: number;
  create_time: string;
  update_time: string;
}

// 菜单树类型
export interface MenuItem {
  id: number;
  code: string;
  name: string;
  path?: string;
  parent_code?: string;
  children: MenuItem[];
}

// 分页相关类型
export interface PaginationParams {
  page: number;
  size: number;
  total?: number;
}

export interface PaginatedResponse<T> {
  code: number;
  message: string;
  data: T;
  pagination: PaginationParams;
}

// 基础响应类型
export interface BaseResponse {
  code: number;
  message: string;
  data?: any;
} 