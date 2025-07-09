from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.role import Role
from app.models.relationships import RoleEnterprise, UserRole
from app.schemas.role import RoleCreate, RoleUpdate, RoleEnterpriseAssign
from app.core.permission_manager import get_permission_manager
from sqlalchemy.orm import aliased


class RoleService:
    """角色服务"""
    
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        """创建角色"""
        # 检查角色名称是否已存在
        existing_role = db.query(Role).filter(Role.name == role_data.name).first()
        if existing_role:
            raise ValueError("角色名称已存在")
        
        # 检查角色代码是否已存在
        existing_code = db.query(Role).filter(Role.code == role_data.code).first()
        if existing_code:
            raise ValueError("角色代码已存在")
        
        # 创建角色
        db_role = Role(
            name=role_data.name,
            description=role_data.description,
            code=role_data.code,
            status=role_data.status
        )
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        
        return db_role
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def get_role_by_code(db: Session, role_code: str) -> Optional[Role]:
        """根据代码获取角色"""
        return db.query(Role).filter(Role.code == role_code).first()
    
    @staticmethod
    def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取角色列表"""
        return db.query(Role).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_role(db: Session, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            return None
        
        update_data = role_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """删除角色"""
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            return False
        
        db.delete(db_role)
        db.commit()
        return True
    
    @staticmethod
    def assign_role_to_enterprises(db: Session, assign_data: RoleEnterpriseAssign) -> bool:
        """分配角色到企业"""
        permission_manager = get_permission_manager(db)
        
        # 删除现有的分配关系
        db.query(RoleEnterprise).filter(
            RoleEnterprise.role_code == assign_data.role_code
        ).delete()
        
        # 创建新的分配关系
        for enterprise_code in assign_data.enterprise_codes:
            permission_manager.add_role_enterprise(assign_data.role_code, enterprise_code)
        
        return True
    
    @staticmethod
    def get_roles_by_enterprise(db: Session, enterprise_code: str) -> List[Role]:
        """获取企业下的角色"""
        return db.query(Role).join(RoleEnterprise, Role.code == RoleEnterprise.role_code).filter(
            RoleEnterprise.enterprise_code == enterprise_code
        ).all()
    
    @staticmethod
    def get_role_users(db: Session, role_id: int) -> List:
        """获取角色的用户"""
        return db.query(UserRole).filter(UserRole.role_id == role_id).all()
    
    @staticmethod
    def get_active_roles(db: Session) -> List[Role]:
        """获取活跃角色列表"""
        return db.query(Role).filter(Role.status == 0).all() 