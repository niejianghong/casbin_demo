from sqlalchemy import Column, String, Integer
from app.models.base import BaseModel


class Enterprise(BaseModel):
    """企业模型"""
    __tablename__ = "enterprise"
    
    code = Column(String(30), unique=True, nullable=False, index=True, comment="企业代码")
    name = Column(String(50), nullable=False, comment="企业名称")
    icon = Column(String(1024), comment="企业图标")
    description = Column(String(1024), comment="企业描述")
    status = Column(Integer, default=0, comment="状态：0-正常，1-禁用") 