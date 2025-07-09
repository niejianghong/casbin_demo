from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.permission_manager import get_permission_manager
from app.core.security import verify_token
from app.models.user import User
from app.schemas.base import BaseResponse

router = APIRouter(prefix="/debug", tags=["调试"])


@router.get("/permission-status")
def get_permission_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取权限状态调试信息"""
    from app.core.auth import security
    
    # 获取token信息
    token = security.credentials
    payload = verify_token(token)
    enterprise_code = payload.get("enterprise_code")
    
    # 获取权限管理器
    permission_manager = get_permission_manager(db)
    
    # 检查超级管理员状态
    is_super_admin = permission_manager._is_super_admin(current_user.user_id)
    
    # 获取用户企业列表
    user_enterprises = permission_manager.get_user_enterprises(current_user.user_id)
    
    # 获取用户角色
    user_roles = permission_manager.get_user_roles(current_user.user_id, enterprise_code) if enterprise_code else []
    
    # 获取用户权限
    user_permissions = permission_manager.get_user_permissions(current_user.user_id, enterprise_code) if enterprise_code else []
    
    # 检查特定资源权限
    resource_permission = permission_manager.check_permission(current_user.user_id, enterprise_code, "resource") if enterprise_code else False
    
    return BaseResponse(data={
        "user_id": current_user.user_id,
        "user_name": current_user.user_name,
        "is_admin": current_user.is_admin,
        "enterprise_code": enterprise_code,
        "is_super_admin": is_super_admin,
        "user_enterprises": user_enterprises,
        "user_roles": user_roles,
        "user_permissions": list(user_permissions),
        "resource_permission": resource_permission,
        "token_payload": payload
    })


@router.get("/clear-cache")
def clear_permission_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """清除权限缓存"""
    permission_manager = get_permission_manager(db)
    permission_manager.clear_cache()
    return BaseResponse(message="权限缓存已清除") 