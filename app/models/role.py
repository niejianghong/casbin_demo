from sqlalchemy import Column, String, Integer
from app.models.base import BaseModel


class Role(BaseModel):
    """角色模型"""
    __tablename__ = "role"
    
    name = Column(String(255), unique=True, nullable=False, comment="角色名称")
    description = Column(String(255), comment="角色描述")
    code = Column(String(255), nullable=False, comment="角色代码")
    status = Column(Integer, default=0, comment="状态：0-正常，1-禁用") 