from typing import Optional
from app.schemas.base import BaseSchema


class EnterpriseBase(BaseSchema):
    """企业基础模式"""
    code: str
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    status: int = 0


class EnterpriseCreate(EnterpriseBase):
    """创建企业模式"""
    pass


class EnterpriseUpdate(BaseSchema):
    """更新企业模式"""
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class EnterpriseResponse(EnterpriseBase):
    """企业响应模式"""
    id: int
    create_time: str
    update_time: str 