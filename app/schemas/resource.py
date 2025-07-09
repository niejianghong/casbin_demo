from typing import Optional, List
from pydantic import BaseModel
from app.schemas.base import BaseSchema


class ResourceBase(BaseSchema):
    """资源基础模式"""
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[int] = None  # 1-API, 2-Menu, 3-Agent
    path: Optional[str] = None
    act: Optional[str] = None
    parent_code: Optional[str] = None
    status: int = 0


class ResourceCreate(ResourceBase):
    """创建资源模式"""
    pass


class ResourceUpdate(BaseSchema):
    """更新资源模式"""
    name: Optional[str] = None
    type: Optional[int] = None
    path: Optional[str] = None
    act: Optional[str] = None
    parent_code: Optional[str] = None
    status: Optional[int] = None


class ResourceResponse(ResourceBase):
    """资源响应模式"""
    id: int
    create_time: str
    update_time: str


class ResourceRoleAssign(BaseModel):
    """资源角色分配模式"""
    resource_code: str
    role_codes: List[str] 