from typing import List, Dict, Optional, Set
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.models.resource import Resource
from app.models.relationships import UserRole, RoleEnterprise, ResourceRole, UserEnterprise, ResourceEnterprise
from sqlalchemy import and_
from app.core.redis_cache import redis_cache


class PermissionManager:
    """自定义权限管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        # 使用Redis缓存替代本地缓存
        self._super_admin_cache_ttl = 1800  # 30分钟
        self._user_permissions_cache_ttl = 1800  # 30分钟
        self._user_enterprises_cache_ttl = 1800  # 30分钟
    
    def _get_cache_key(self, user_id: int, enterprise_code: str) -> str:
        """生成缓存键"""
        return f"{user_id}_{enterprise_code}"
    
    def _is_super_admin(self, user_id: int) -> bool:
        """检查用户是否为超级管理员（优化版本）
        判定条件：
        1. user_id 是 1
        2. User表中的is_admin是1
        3. 用户所在的任意企业的角色(role_code)是admin
        """
        # 缓存键
        cache_key = f"super_admin:{user_id}"
        
        # 检查缓存
        cached_result = redis_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 条件1: user_id 是 1
        if user_id == 1:
            redis_cache.set(cache_key, True, self._super_admin_cache_ttl)
            return True
        
        # 条件2: User表中的is_admin是1
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if user and user.is_admin == 1:
                redis_cache.set(cache_key, True, self._super_admin_cache_ttl)
                return True
        except Exception:
            # 如果查询失败，继续检查其他条件
            pass
        
        # 条件3: 用户所在的任意企业的角色(role_code)是admin
        try:
            # 明确指定ON条件
            admin_role_exists = self.db.query(UserRole).join(
                Role, UserRole.role_id == Role.id
            ).filter(
                UserRole.user_id == user_id,
                Role.code == "admin"
            ).first() is not None
            
            if admin_role_exists:
                redis_cache.set(cache_key, True, self._super_admin_cache_ttl)
                return True
        except Exception:
            # 如果查询失败，返回False
            pass
        
        # 缓存结果
        redis_cache.set(cache_key, False, self._super_admin_cache_ttl)
        return False
    
    def _get_user_enterprises(self, user_id: int) -> List[str]:
        """获取用户所属的企业列表（Redis缓存版本）"""
        cache_key = f"user_enterprises:{user_id}"
        
        # 检查缓存
        cached_result = redis_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 查询数据库
        user_enterprises = self.db.query(UserEnterprise).filter(
            and_(
                UserEnterprise.user_id == user_id,
                UserEnterprise.status == 0
            )
        ).all()
        result = [ue.enterprise_code for ue in user_enterprises]
        
        # 缓存结果
        redis_cache.set(cache_key, result, self._user_enterprises_cache_ttl)
        return result
    
    def _get_user_roles(self, user_id: int, enterprise_code: str) -> List[str]:
        """获取用户在企业下的角色列表"""
        # 获取用户的所有角色
        user_roles = self.db.query(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
        
        user_role_ids = [ur.role_id for ur in user_roles]
        
        # 获取角色信息
        roles = self.db.query(Role).filter(Role.id.in_(user_role_ids)).all()
        role_codes = [role.code for role in roles]
        
        # 过滤出属于该企业的角色
        role_enterprises = self.db.query(RoleEnterprise).filter(
            and_(
                RoleEnterprise.role_code.in_(role_codes),
                RoleEnterprise.enterprise_code == enterprise_code
            )
        ).all()
        
        return [re.role_code for re in role_enterprises]
    
    def _get_role_resources(self, role_codes: List[str], enterprise_code: str) -> Set[str]:
        """获取角色对应的资源列表（限制在企业范围内）"""
        if not role_codes:
            return set()
        
        # 获取角色对应的资源，同时确保资源属于指定企业
        # 通过关联表查询企业下的资源
        enterprise_resources = self.db.query(ResourceEnterprise.resource_code).filter(
            ResourceEnterprise.enterprise_code == enterprise_code
        ).subquery()
        
        resource_roles = self.db.query(ResourceRole).filter(
            and_(
                ResourceRole.role_code.in_(role_codes),
                ResourceRole.resource_code.in_(enterprise_resources)
            )
        ).all()
        
        return {rr.resource_code for rr in resource_roles}
    
    def _get_user_permissions(self, user_id: int, enterprise_code: str) -> Set[str]:
        """获取用户在企业下的权限列表（Redis缓存版本）"""
        cache_key = f"user_permissions:{user_id}:{enterprise_code}"
        
        # 检查缓存
        cached_result = redis_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 获取用户角色
        user_roles = self._get_user_roles(user_id, enterprise_code)
        
        # 获取角色对应的资源
        permissions = self._get_role_resources(user_roles, enterprise_code)
        
        # 缓存结果
        redis_cache.set(cache_key, permissions, self._user_permissions_cache_ttl)
        
        return permissions
    
    def check_permission(self, user_id: int, enterprise_code: str, resource_code: str) -> bool:
        """检查用户是否有权限访问指定资源"""
        
        # 检查用户是否为超级管理员
        if self._is_super_admin(user_id):
            return True
        
        # 检查用户是否属于该企业
        user_enterprises = self._get_user_enterprises(user_id)
        if enterprise_code not in user_enterprises:
            return False
        
        # 获取用户权限
        user_permissions = self._get_user_permissions(user_id, enterprise_code)
        
        # 检查是否有权限
        return resource_code in user_permissions
    
    def check_user_enterprise_access(self, user_id: int, enterprise_code: str) -> bool:
        """检查用户是否可以访问指定企业"""
        # 检查用户是否为超级管理员
        if self._is_super_admin(user_id):
            return True
        
        user_enterprises = self._get_user_enterprises(user_id)
        return enterprise_code in user_enterprises
    
    def get_user_enterprises(self, user_id: int) -> List[str]:
        """获取用户所属的企业列表"""
        return self._get_user_enterprises(user_id)
    
    def get_user_roles(self, user_id: int, enterprise_code: str) -> List[str]:
        """获取用户在企业下的角色列表"""
        return self._get_user_roles(user_id, enterprise_code)
    
    def get_user_permissions(self, user_id: int, enterprise_code: str) -> List[str]:
        """获取用户在企业下的权限列表"""
        permissions = self._get_user_permissions(user_id, enterprise_code)
        return list(permissions)
    
    def add_user_role(self, user_id: int, role_id: int) -> bool:
        """为用户添加角色"""
        try:
            # 检查是否已存在
            existing = self.db.query(UserRole).filter(
                and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
            ).first()
            
            if existing:
                return True
            
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
            self.db.commit()
            
            # 清除相关缓存
            self._clear_user_cache(user_id)
            
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def remove_user_role(self, user_id: int, role_id: int) -> bool:
        """移除用户角色"""
        try:
            user_role = self.db.query(UserRole).filter(
                and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
            ).first()
            
            if not user_role:
                return False
            
            self.db.delete(user_role)
            self.db.commit()
            
            # 清除相关缓存
            self._clear_user_cache(user_id)
            
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def add_role_enterprise(self, role_code: str, enterprise_code: str) -> bool:
        """为角色添加企业"""
        try:
            # 检查是否已存在
            existing = self.db.query(RoleEnterprise).filter(
                and_(
                    RoleEnterprise.role_code == role_code,
                    RoleEnterprise.enterprise_code == enterprise_code
                )
            ).first()
            
            if existing:
                return True
            
            role_enterprise = RoleEnterprise(
                role_code=role_code,
                enterprise_code=enterprise_code
            )
            self.db.add(role_enterprise)
            self.db.commit()
            
            # 清除相关缓存
            self._clear_enterprise_cache(enterprise_code)
            
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def remove_role_enterprise(self, role_code: str, enterprise_code: str) -> bool:
        """移除角色企业关系"""
        try:
            role_enterprise = self.db.query(RoleEnterprise).filter(
                and_(
                    RoleEnterprise.role_code == role_code,
                    RoleEnterprise.enterprise_code == enterprise_code
                )
            ).first()
            
            if not role_enterprise:
                return False
            
            self.db.delete(role_enterprise)
            self.db.commit()
            
            # 清除相关缓存
            self._clear_enterprise_cache(enterprise_code)
            
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def add_resource_role(self, resource_code: str, role_code: str) -> bool:
        """为资源添加角色"""
        try:
            # 检查是否已存在
            existing = self.db.query(ResourceRole).filter(
                and_(
                    ResourceRole.resource_code == resource_code,
                    ResourceRole.role_code == role_code
                )
            ).first()
            
            if existing:
                return True
            
            resource_role = ResourceRole(
                resource_code=resource_code,
                role_code=role_code
            )
            self.db.add(resource_role)
            self.db.commit()
            
            # 清除相关缓存
            self._clear_role_cache(role_code)
            
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def remove_resource_role(self, resource_code: str, role_code: str) -> bool:
        """移除资源角色关系"""
        try:
            resource_role = self.db.query(ResourceRole).filter(
                and_(
                    ResourceRole.resource_code == resource_code,
                    ResourceRole.role_code == role_code
                )
            ).first()
            
            if not resource_role:
                return False
            
            self.db.delete(resource_role)
            self.db.commit()
            
            # 清除相关缓存
            self._clear_role_cache(role_code)
            
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def add_resource_enterprise(self, resource_code: str, enterprise_code: str) -> bool:
        """为资源添加企业关系"""
        try:
            # 检查是否已存在
            existing = self.db.query(ResourceEnterprise).filter(
                and_(
                    ResourceEnterprise.resource_code == resource_code,
                    ResourceEnterprise.enterprise_code == enterprise_code
                )
            ).first()
            
            if existing:
                return True
            
            resource_enterprise = ResourceEnterprise(
                resource_code=resource_code,
                enterprise_code=enterprise_code
            )
            self.db.add(resource_enterprise)
            self.db.commit()
            
            # 清除相关缓存
            self._clear_enterprise_cache(enterprise_code)
            
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def remove_resource_enterprise(self, resource_code: str, enterprise_code: str) -> bool:
        """移除资源企业关系"""
        try:
            resource_enterprise = self.db.query(ResourceEnterprise).filter(
                and_(
                    ResourceEnterprise.resource_code == resource_code,
                    ResourceEnterprise.enterprise_code == enterprise_code
                )
            ).first()
            
            if not resource_enterprise:
                return False
            
            self.db.delete(resource_enterprise)
            self.db.commit()
            
            # 清除相关缓存
            self._clear_enterprise_cache(enterprise_code)
            
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def get_enterprise_resources(self, enterprise_code: str) -> List[str]:
        """获取企业下的所有资源"""
        resource_enterprises = self.db.query(ResourceEnterprise).filter(
            ResourceEnterprise.enterprise_code == enterprise_code
        ).all()
        return [re.resource_code for re in resource_enterprises]
    
    def _clear_user_cache(self, user_id: int):
        """清除用户相关缓存"""
        # 清除超级管理员缓存
        redis_cache.delete(f"super_admin:{user_id}")
        # 清除用户企业缓存
        redis_cache.delete(f"user_enterprises:{user_id}")
        # 清除用户权限缓存
        redis_cache.delete_pattern(f"user_permissions:{user_id}:*")
    
    def _clear_enterprise_cache(self, enterprise_code: str):
        """清除企业相关缓存"""
        # 清除所有用户在该企业下的权限缓存
        redis_cache.delete_pattern(f"user_permissions:*:{enterprise_code}")
    
    def _clear_role_cache(self, role_code: str):
        """清除角色相关缓存"""
        # 清除所有用户权限缓存，因为角色变更会影响所有用户
        redis_cache.delete_pattern("user_permissions:*")
        # 清除所有超级管理员缓存，因为角色变更可能影响超级管理员状态
        redis_cache.delete_pattern("super_admin:*")
    
    def clear_cache(self):
        """清除所有缓存"""
        redis_cache.clear_all()


# 全局权限管理器实例
_permission_manager: Optional[PermissionManager] = None


def get_permission_manager(db: Session) -> PermissionManager:
    """获取权限管理器实例"""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager(db)
    return _permission_manager


def clear_permission_cache():
    """清除权限缓存"""
    global _permission_manager
    if _permission_manager:
        _permission_manager.clear_cache() 