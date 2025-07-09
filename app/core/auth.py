from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.relationships import UserEnterprise
from app.core.permission_manager import get_permission_manager
from typing import Optional

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_enterprise_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> tuple[User, str]:
    """获取当前企业用户"""
    # 从token中获取企业代码
    token = security.credentials
    payload = verify_token(token)
    enterprise_code = payload.get("enterprise_code")
    
    if not enterprise_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少企业代码"
        )
    
    # 使用权限管理器检查用户是否属于该企业
    permission_manager = get_permission_manager(db)
    if not permission_manager.check_user_enterprise_access(current_user.user_id, enterprise_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户不属于该企业"
        )
    
    return current_user, enterprise_code


def check_permission(resource: str, action: str = "*"):
    """检查权限装饰器"""
    def permission_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # 超级管理员拥有所有权限
        permission_manager = get_permission_manager(db)
        if permission_manager._is_super_admin(current_user.user_id):
            return current_user
        
        # 从token中获取企业代码
        token = credentials.credentials
        payload = verify_token(token)
        enterprise_code = payload.get("enterprise_code")
        
        if not enterprise_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少企业代码"
            )
        
        # 使用权限管理器检查权限

        if not permission_manager.check_permission(current_user.user_id, enterprise_code, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        return current_user
    
    return permission_checker


def check_enterprise_permission(resource: str, action: str = "*"):
    """检查企业权限装饰器"""
    def permission_checker(
        current_user_enterprise: tuple[User, str] = Depends(get_current_enterprise_user),
        db: Session = Depends(get_db)
    ):
        current_user, enterprise_code = current_user_enterprise
        
        # 超级管理员拥有所有权限
        if current_user.is_admin == 1:
            return current_user, enterprise_code
        
        # 使用权限管理器检查权限
        permission_manager = get_permission_manager(db)
        if not permission_manager.check_permission(current_user.user_id, enterprise_code, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        return current_user, enterprise_code
    
    return permission_checker 