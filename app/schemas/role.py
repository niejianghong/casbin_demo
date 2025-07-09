from typing import Optional, List
from pydantic import BaseModel
from app.schemas.base import BaseSchema


class RoleBase(BaseSchema):
    """角色基础模式"""
    name: str
    description: Optional[str] = None
    code: str
    status: int = 0


class RoleCreate(RoleBase):
    """创建角色模式"""
    pass


class RoleUpdate(BaseSchema):
    """更新角色模式"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class RoleResponse(RoleBase):
    """角色响应模式"""
    id: int
    create_time: str
    update_time: str


class RoleEnterpriseAssign(BaseModel):
    """角色企业分配模式"""
    role_code: str
    enterprise_codes: List[str] 