from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.user import User
from app.models.role import Role
from app.models.relationships import UserEnterprise, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserEnterpriseAssign
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.permission_manager import get_permission_manager
from datetime import timedelta
from app.core.config import settings


class UserService:
    """用户服务"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.user_name == user_data.user_name).first()
        if existing_user:
            raise ValueError("用户名已存在")
        
        # 检查third_uid是否已存在
        existing_uid = db.query(User).filter(User.third_uid == user_data.third_uid).first()
        if existing_uid:
            raise ValueError("第三方用户ID已存在")
        
        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            user_name=user_data.user_name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            password=hashed_password,
            nick_name=user_data.nick_name,
            is_admin=user_data.is_admin,
            status=user_data.status,
            icon=user_data.icon,
            third_uid=user_data.third_uid
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.user_name == username).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户"""
        db_user = db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        
        # 如果更新密码，需要哈希处理
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """删除用户"""
        db_user = db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = db.query(User).filter(User.user_name == username).first()
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    @staticmethod
    def create_access_token_for_user(user: User, enterprise_code: str) -> str:
        """为用户创建访问令牌"""
        data = {
            "user_id": user.user_id,
            "username": user.user_name,
            "is_admin": user.is_admin,
            "enterprise_code": enterprise_code
        }
        return create_access_token(data=data)
    
    @staticmethod
    def assign_users_to_enterprise(db: Session, assign_data: UserEnterpriseAssign) -> bool:
        """分配用户到企业"""
        # 删除现有的分配关系
        db.query(UserEnterprise).filter(
            UserEnterprise.enterprise_code == assign_data.enterprise_code
        ).delete()
        
        # 创建新的分配关系
        for user_id in assign_data.user_ids:
            user_enterprise = UserEnterprise(
                user_id=user_id,
                enterprise_code=assign_data.enterprise_code,
                status=assign_data.status
            )
            db.add(user_enterprise)
        
        db.commit()
        return True
    
    @staticmethod
    def get_users_by_enterprise(db: Session, enterprise_code: str) -> List[User]:
        """获取企业下的用户"""
        return db.query(User).join(UserEnterprise).filter(
            and_(
                UserEnterprise.enterprise_code == enterprise_code,
                UserEnterprise.status == 0
            )
        ).all()
    
    @staticmethod
    def assign_role_to_user(db: Session, user_id: int, role_id: int) -> bool:
        """为用户分配角色"""
        # 使用权限管理器添加用户角色
        permission_manager = get_permission_manager(db)
        return permission_manager.add_user_role(user_id, role_id)
    
    @staticmethod
    def remove_role_from_user(db: Session, user_id: int, role_id: int) -> bool:
        """移除用户角色"""
        # 使用权限管理器移除用户角色
        permission_manager = get_permission_manager(db)
        return permission_manager.remove_user_role(user_id, role_id)
    
    @staticmethod
    def get_user_roles(db: Session, user_id: int) -> List[Role]:
        """获取用户角色"""
        return db.query(Role).join(UserRole).filter(UserRole.user_id == user_id).all() 