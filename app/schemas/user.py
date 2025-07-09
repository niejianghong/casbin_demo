from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    """用户基础模式"""
    user_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    nick_name: Optional[str] = None
    is_admin: int = 0
    status: int = 0
    icon: Optional[str] = None
    third_uid: str


class UserCreate(UserBase):
    """创建用户模式"""
    password: str


class UserUpdate(BaseModel):
    """更新用户模式"""
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    nick_name: Optional[str] = None
    password: Optional[str] = None
    status: Optional[int] = None
    icon: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模式"""
    user_id: int
    create_time: str
    update_time: str


class UserLogin(BaseModel):
    """用户登录模式"""
    user_name: str
    password: str
    enterprise_code: str


class UserLoginResponse(BaseModel):
    """用户登录响应模式"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    enterprise_code: str


class UserEnterpriseAssign(BaseModel):
    """用户企业分配模式"""
    user_ids: List[int]
    enterprise_code: str
    status: int = 0 