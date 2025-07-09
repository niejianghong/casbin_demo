from sqlalchemy import Column, BigInteger, String, Integer
from app.models.base import BaseModel


class Organization(BaseModel):
    """组织模型"""
    __tablename__ = "organization"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="组织ID")
    user_group_id = Column(BigInteger, unique=True, nullable=False, comment="用户组ID")
    user_group_name = Column(String(255), nullable=False, comment="用户组名称")
    user_group_level = Column(Integer, comment="用户组级别")
    parent_user_group_id = Column(BigInteger, comment="父级用户组ID") 