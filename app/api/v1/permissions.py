from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.permission_manager import get_permission_manager
from app.schemas.base import BaseResponse
from app.core.auth import get_current_user, check_permission
from app.models.user import User

router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.get("/check/{resource_code}")
def check_user_permission(
    resource_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("permission", "read"))
):
    """检查用户是否有权限访问指定资源"""
    # 从token中获取企业代码
    from app.core.auth import security
    from app.core.security import verify_token
    
    token = security.credentials
    payload = verify_token(token)
    enterprise_code = payload.get("enterprise_code")
    
    if not enterprise_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少企业代码"
        )
    
    permission_manager = get_permission_manager(db)
    has_permission = permission_manager.check_permission(
        current_user.user_id, 
        enterprise_code, 
        resource_code
    )
    
    return BaseResponse(
        data={
            "has_permission": has_permission,
            "user_id": current_user.user_id,
            "enterprise_code": enterprise_code,
            "resource_code": resource_code
        }
    )


@router.get("/user/enterprises")
def get_user_enterprises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户所属的企业列表"""
    permission_manager = get_permission_manager(db)
    enterprises = permission_manager.get_user_enterprises(current_user.user_id)
    
    return BaseResponse(data={"enterprises": enterprises})


@router.get("/user/roles")
def get_user_roles(
    enterprise_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("permission", "read"))
):
    """获取用户在企业下的角色列表"""
    permission_manager = get_permission_manager(db)
    roles = permission_manager.get_user_roles(current_user.user_id, enterprise_code)
    
    return BaseResponse(data={"roles": roles})


@router.get("/user/permissions")
def get_user_permissions(
    enterprise_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("permission", "read"))
):
    """获取用户在企业下的权限列表"""
    permission_manager = get_permission_manager(db)
    permissions = permission_manager.get_user_permissions(current_user.user_id, enterprise_code)
    
    return BaseResponse(data={"permissions": permissions})


@router.post("/clear-cache")
def clear_permission_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("permission", "admin"))
):
    """清除权限缓存（仅超级管理员）"""
    if current_user.is_admin != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以清除缓存"
        )
    
    permission_manager = get_permission_manager(db)
    permission_manager.clear_cache()
    
    return BaseResponse(message="权限缓存已清除") 