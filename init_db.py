#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建默认的超级管理员用户和基础数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Base, User, Enterprise, Role, Resource
from app.services.user_service import UserService
from app.core.security import get_password_hash
from app.models.relationships import UserEnterprise, UserRole, RoleEnterprise, ResourceRole, ResourceEnterprise


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成")
    
    db = SessionLocal()
    try:
        # 创建默认企业
        default_enterprise = create_default_enterprise(db)
        print("✓ 默认企业创建完成")
        
        # 创建默认角色
        admin_role = create_default_roles(db)
        print("✓ 默认角色创建完成")
        
        # 创建默认资源
        create_default_resources(db)
        print("✓ 默认资源创建完成")
        
        # 创建超级管理员用户
        admin_user = create_super_admin(db)
        print("✓ 超级管理员用户创建完成")
        
        # 建立关系
        create_default_relationships(db, admin_user, admin_role, default_enterprise)
        print("✓ 默认关系创建完成")
        
        print("\n🎉 数据库初始化完成！")
        print("默认超级管理员账户:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  企业代码: default")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_default_enterprise(db: Session) -> Enterprise:
    """创建默认企业"""
    enterprise = db.query(Enterprise).filter(Enterprise.code == "default").first()
    if not enterprise:
        enterprise = Enterprise(
            name="默认企业",
            code="default",
            description="系统默认企业",
            status=0
        )
        db.add(enterprise)
        db.commit()
        db.refresh(enterprise)
    return enterprise


def create_default_roles(db: Session) -> Role:
    """创建默认角色"""
    # 创建管理员角色
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    if not admin_role:
        admin_role = Role(
            name="超级管理员",
            code="admin",
            description="系统超级管理员，拥有所有权限",
            status=0
        )
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)
    
    # 创建普通用户角色
    user_role = db.query(Role).filter(Role.code == "user").first()
    if not user_role:
        user_role = Role(
            name="普通用户",
            code="user",
            description="普通用户，基础权限",
            status=0
        )
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
    
    return admin_role


def create_default_resources(db: Session):
    """创建默认资源"""
    resources = [
        {"name": "用户管理", "code": "user", "description": "用户管理相关功能"},
        {"name": "角色管理", "code": "role", "description": "角色管理相关功能"},
        {"name": "企业管理", "code": "enterprise", "description": "企业管理相关功能"},
        {"name": "资源管理", "code": "resource", "description": "资源管理相关功能"},
        {"name": "权限管理", "code": "permission", "description": "权限管理相关功能"},
    ]
    
    for resource_data in resources:
        resource = db.query(Resource).filter(Resource.code == resource_data["code"]).first()
        if not resource:
            resource = Resource(
                name=resource_data["name"],
                code=resource_data["code"],
                description=resource_data["description"],
                status=0
            )
            db.add(resource)
    
    db.commit()


def create_super_admin(db: Session) -> User:
    """创建超级管理员用户"""
    admin_user = db.query(User).filter(User.user_name == "admin").first()
    if not admin_user:
        admin_user = User(
            user_name="admin",
            email="admin@example.com",
            password=get_password_hash("admin123"),
            nick_name="超级管理员",
            is_admin=1,
            status=0,
            third_uid="admin_default"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
    return admin_user


def create_default_relationships(db: Session, admin_user: User, admin_role: Role, default_enterprise: Enterprise):
    """创建默认关系"""
    # 用户-企业关系
    user_enterprise = db.query(UserEnterprise).filter(
        UserEnterprise.user_id == admin_user.user_id,
        UserEnterprise.enterprise_code == default_enterprise.code
    ).first()
    
    if not user_enterprise:
        user_enterprise = UserEnterprise(
            user_id=admin_user.user_id,
            enterprise_code=default_enterprise.code,
            status=0
        )
        db.add(user_enterprise)
    
    # 用户-角色关系
    user_role = db.query(UserRole).filter(
        UserRole.user_id == admin_user.user_id,
        UserRole.role_id == admin_role.id
    ).first()
    
    if not user_role:
        user_role = UserRole(
            user_id=admin_user.user_id,
            role_id=admin_role.id
        )
        db.add(user_role)
    
    # 角色-企业关系
    role_enterprise = db.query(RoleEnterprise).filter(
        RoleEnterprise.role_id == admin_role.id,
        RoleEnterprise.enterprise_code == default_enterprise.code
    ).first()
    
    if not role_enterprise:
        role_enterprise = RoleEnterprise(
            role_id=admin_role.id,
            enterprise_code=default_enterprise.code,
            status=0
        )
        db.add(role_enterprise)
    
    # 资源-企业关系（所有资源都属于默认企业）
    resources = db.query(Resource).all()
    for resource in resources:
        resource_enterprise = db.query(ResourceEnterprise).filter(
            ResourceEnterprise.resource_code == resource.code,
            ResourceEnterprise.enterprise_code == default_enterprise.code
        ).first()
        
        if not resource_enterprise:
            resource_enterprise = ResourceEnterprise(
                resource_code=resource.code,
                enterprise_code=default_enterprise.code
            )
            db.add(resource_enterprise)
    
    # 资源-角色关系（管理员拥有所有资源权限）
    for resource in resources:
        resource_role = db.query(ResourceRole).filter(
            ResourceRole.resource_code == resource.code,
            ResourceRole.role_code == admin_role.code
        ).first()
        
        if not resource_role:
            resource_role = ResourceRole(
                resource_code=resource.code,
                role_code=admin_role.code
            )
            db.add(resource_role)
    
    db.commit()


if __name__ == "__main__":
    init_database() 