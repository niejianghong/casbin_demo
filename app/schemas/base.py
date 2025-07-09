from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BaseSchema(BaseModel):
    """基础模式"""
    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseModel):
    """基础响应模式"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    size: int = 10
    total: Optional[int] = None


class PaginatedResponse(BaseResponse):
    """分页响应"""
    data: Optional[dict] = None
    pagination: Optional[PaginationParams] = None 