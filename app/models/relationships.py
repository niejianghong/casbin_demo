from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class UserEnterprise(Base):
    """用户企业关系模型"""
    __tablename__ = "user_enterprise"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    enterprise_code = Column(String(255), nullable=False, comment="企业代码")
    status = Column(Integer, nullable=False, default=0, comment="状态：0-正常，1-禁用")
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UserOrganization(Base):
    """用户组织关系模型"""
    __tablename__ = "user_organization"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    user_group_id = Column(BigInteger, nullable=False, comment="用户组ID")
    third_uid = Column(String(64), nullable=False, comment="第三方用户ID")


class UserRole(Base):
    """用户角色关系模型"""
    __tablename__ = "user_role"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    role_id = Column(Integer, nullable=False, comment="角色ID")
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class RoleEnterprise(Base):
    """角色企业关系模型"""
    __tablename__ = "role_enterprise"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    role_code = Column(String(255), nullable=False, comment="角色代码")
    enterprise_code = Column(String(255), nullable=False, comment="企业代码")
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ResourceRole(Base):
    """资源角色关系模型"""
    __tablename__ = "resource_role"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    resource_code = Column(String(255), nullable=False, comment="资源代码")
    role_code = Column(String(255), nullable=False, comment="角色代码")
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ResourceEnterprise(Base):
    """资源企业关系模型"""
    __tablename__ = "resource_enterprise"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    resource_code = Column(String(255), nullable=False, comment="资源代码")
    enterprise_code = Column(String(30), nullable=False, comment="企业代码")
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 