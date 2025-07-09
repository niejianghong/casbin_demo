from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleEnterpriseAssign
from app.schemas.base import BaseResponse, PaginatedResponse
from app.core.auth import get_current_user, check_permission
from app.models.user import User
from app.models.role import Role

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.get("/", response_model=PaginatedResponse)
def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "read"))
):
    """获取角色列表"""
    roles = RoleService.get_roles(db, skip=skip, limit=limit)
    total = db.query(Role).count()
    
    role_list = []
    for role in roles:
        role_list.append(RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            code=role.code,
            status=role.status,
            create_time=role.create_time.isoformat(),
            update_time=role.update_time.isoformat()
        ))
    
    return PaginatedResponse(
        data={"roles": role_list},
        pagination={
            "page": skip // limit + 1,
            "size": limit,
            "total": total
        }
    )


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "read"))
):
    """获取角色详情"""
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        code=role.code,
        status=role.status,
        create_time=role.create_time.isoformat(),
        update_time=role.update_time.isoformat()
    )


@router.post("/", response_model=RoleResponse)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "create"))
):
    """创建角色"""
    try:
        role = RoleService.create_role(db, role_data)
        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            code=role.code,
            status=role.status,
            create_time=role.create_time.isoformat(),
            update_time=role.update_time.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "update"))
):
    """更新角色"""
    role = RoleService.update_role(db, role_id, role_data)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        code=role.code,
        status=role.status,
        create_time=role.create_time.isoformat(),
        update_time=role.update_time.isoformat()
    )


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "delete"))
):
    """删除角色"""
    success = RoleService.delete_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return BaseResponse(message="角色删除成功")


@router.post("/assign-enterprise")
def assign_role_to_enterprises(
    assign_data: RoleEnterpriseAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "assign"))
):
    """分配角色到企业"""
    success = RoleService.assign_role_to_enterprises(db, assign_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配失败"
        )
    
    return BaseResponse(message="角色分配成功")


@router.get("/enterprise/{enterprise_code}", response_model=List[RoleResponse])
def get_roles_by_enterprise(
    enterprise_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "read"))
):
    """获取企业下的角色"""
    roles = RoleService.get_roles_by_enterprise(db, enterprise_code)
    
    role_list = []
    for role in roles:
        role_list.append(RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            code=role.code,
            status=role.status,
            create_time=role.create_time.isoformat(),
            update_time=role.update_time.isoformat()
        ))
    
    return role_list


@router.post("/{role_id}/assign-users")
def assign_users_to_role(
    role_id: int,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "assign"))
):
    """为角色分配用户"""
    user_ids = assign_data.get("user_ids", [])
    
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少用户ID列表"
        )
    
    permission_manager = get_permission_manager(db)
    success_count = 0
    
    for user_id in user_ids:
        if permission_manager.add_user_role(user_id, role_id):
            success_count += 1
    
    if success_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配失败"
        )
    
    return BaseResponse(message=f"成功为 {success_count} 个用户分配角色")


@router.delete("/{role_id}/remove-users")
def remove_users_from_role(
    role_id: int,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "assign"))
):
    """移除角色的用户"""
    user_ids = assign_data.get("user_ids", [])
    
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少用户ID列表"
        )
    
    permission_manager = get_permission_manager(db)
    success_count = 0
    
    for user_id in user_ids:
        if permission_manager.remove_user_role(user_id, role_id):
            success_count += 1
    
    return BaseResponse(message=f"成功移除 {success_count} 个用户")


@router.get("/{role_id}/users")
def get_role_users(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "read"))
):
    """获取角色的用户列表"""
    user_roles = RoleService.get_role_users(db, role_id)
    
    user_list = []
    for user_role in user_roles:
        user = db.query(User).filter(User.user_id == user_role.user_id).first()
        if user:
            user_list.append({
                "user_id": user.user_id,
                "user_name": user.user_name,
                "email": user.email,
                "nick_name": user.nick_name,
                "status": user.status
            })
    
    return BaseResponse(data={"users": user_list})


@router.get("/active/list", response_model=List[RoleResponse])
def get_active_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("role", "read"))
):
    """获取活跃角色列表"""
    roles = RoleService.get_active_roles(db)
    
    role_list = []
    for role in roles:
        role_list.append(RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            code=role.code,
            status=role.status,
            create_time=role.create_time.isoformat(),
            update_time=role.update_time.isoformat()
        ))
    
    return role_list 