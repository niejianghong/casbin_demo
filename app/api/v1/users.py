from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.permission_manager import get_permission_manager
from app.models.role import Role
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserEnterpriseAssign
from app.schemas.base import BaseResponse, PaginatedResponse
from app.core.auth import get_current_user, check_permission
from app.models.user import User

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/", response_model=PaginatedResponse)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "read"))
):
    """获取用户列表"""
    users = UserService.get_users(db, skip=skip, limit=limit)
    total = db.query(User).count()
    
    user_list = []
    for user in users:
        user_list.append(UserResponse(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            nick_name=user.nick_name,
            is_admin=user.is_admin,
            status=user.status,
            icon=user.icon,
            third_uid=user.third_uid,
            create_time=user.create_time.isoformat(),
            update_time=user.update_time.isoformat()
        ))
    
    return PaginatedResponse(
        data={"users": user_list},
        pagination={
            "page": skip // limit + 1,
            "size": limit,
            "total": total
        }
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "read"))
):
    """获取用户详情"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        phone_number=user.phone_number,
        nick_name=user.nick_name,
        is_admin=user.is_admin,
        status=user.status,
        icon=user.icon,
        third_uid=user.third_uid,
        create_time=user.create_time.isoformat(),
        update_time=user.update_time.isoformat()
    )


@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "create"))
):
    """创建用户"""
    try:
        user = UserService.create_user(db, user_data)
        return UserResponse(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            nick_name=user.nick_name,
            is_admin=user.is_admin,
            status=user.status,
            icon=user.icon,
            third_uid=user.third_uid,
            create_time=user.create_time.isoformat(),
            update_time=user.update_time.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "update"))
):
    """更新用户"""
    user = UserService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        phone_number=user.phone_number,
        nick_name=user.nick_name,
        is_admin=user.is_admin,
        status=user.status,
        icon=user.icon,
        third_uid=user.third_uid,
        create_time=user.create_time.isoformat(),
        update_time=user.update_time.isoformat()
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "delete"))
):
    """删除用户"""
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return BaseResponse(message="用户删除成功")


@router.post("/assign-enterprise")
def assign_users_to_enterprise(
    assign_data: UserEnterpriseAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "assign"))
):
    """分配用户到企业"""
    success = UserService.assign_users_to_enterprise(db, assign_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配失败"
        )
    
    return BaseResponse(message="用户分配成功")


@router.get("/enterprise/{enterprise_code}", response_model=List[UserResponse])
def get_users_by_enterprise(
    enterprise_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "read"))
):
    """获取企业下的用户"""
    users = UserService.get_users_by_enterprise(db, enterprise_code)
    
    user_list = []
    for user in users:
        user_list.append(UserResponse(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            nick_name=user.nick_name,
            is_admin=user.is_admin,
            status=user.status,
            icon=user.icon,
            third_uid=user.third_uid,
            create_time=user.create_time.isoformat(),
            update_time=user.update_time.isoformat()
        ))
    
    return user_list


@router.post("/assign-role")
def assign_role_to_user(
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "assign"))
):
    """为用户分配角色"""
    user_id = assign_data.get("user_id")
    role_id = assign_data.get("role_id")
    
    if not user_id or not role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少用户ID或角色ID"
        )
    
    success = UserService.assign_role_to_user(db, user_id, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配失败"
        )
    
    return BaseResponse(message="角色分配成功")


@router.delete("/remove-role")
def remove_role_from_user(
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "assign"))
):
    """移除用户角色"""
    user_id = assign_data.get("user_id")
    role_id = assign_data.get("role_id")
    
    if not user_id or not role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少用户ID或角色ID"
        )
    
    permission_manager = get_permission_manager(db)
    success = permission_manager.remove_user_role(user_id, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="移除失败"
        )
    
    return BaseResponse(message="角色移除成功")


@router.get("/{user_id}/roles")
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("user", "read"))
):
    """获取用户的角色列表"""
    permission_manager = get_permission_manager(db)
    roles = RoleService.get_role_users(db, user_id)
    
    role_list = []
    for user_role in roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            role_list.append({
                "id": role.id,
                "name": role.name,
                "code": role.code,
                "description": role.description,
                "status": role.status
            })
    
    return BaseResponse(data={"roles": role_list}) 