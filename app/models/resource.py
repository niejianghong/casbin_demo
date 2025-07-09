from sqlalchemy import Column, String, Integer
from app.models.base import BaseModel


class Resource(BaseModel):
    """资源模型"""
    __tablename__ = "resource"
    
    name = Column(String(255), comment="资源名称")
    code = Column(String(255), comment="资源代码")
    type = Column(Integer, comment="资源类型：1-API，2-Menu，3-Agent")
    path = Column(String(255), comment="资源路径")
    act = Column(String(255), comment="操作")
    parent_code = Column(String(255), comment="父级资源代码")
    status = Column(Integer, default=0, comment="状态：0-正常，1-禁用") 