from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.enterprise_service import EnterpriseService
from app.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate, EnterpriseResponse
from app.schemas.base import BaseResponse, PaginatedResponse
from app.core.auth import get_current_user, check_permission
from app.models.user import User
from app.models.enterprise import Enterprise

router = APIRouter(prefix="/enterprises", tags=["企业管理"])


@router.get("/", response_model=PaginatedResponse)
def get_enterprises(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "read"))
):
    """获取企业列表"""
    enterprises = EnterpriseService.get_enterprises(db, skip=skip, limit=limit)
    total = db.query(Enterprise).count()
    
    enterprise_list = []
    for enterprise in enterprises:
        enterprise_list.append(EnterpriseResponse(
            id=enterprise.id,
            code=enterprise.code,
            name=enterprise.name,
            icon=enterprise.icon,
            description=enterprise.description,
            status=enterprise.status,
            create_time=enterprise.create_time.isoformat(),
            update_time=enterprise.update_time.isoformat()
        ))
    
    return PaginatedResponse(
        data={"enterprises": enterprise_list},
        pagination={
            "page": skip // limit + 1,
            "size": limit,
            "total": total
        }
    )


@router.get("/{enterprise_id}", response_model=EnterpriseResponse)
def get_enterprise(
    enterprise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "read"))
):
    """获取企业详情"""
    enterprise = EnterpriseService.get_enterprise_by_id(db, enterprise_id)
    if not enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="企业不存在"
        )
    
    return EnterpriseResponse(
        id=enterprise.id,
        code=enterprise.code,
        name=enterprise.name,
        icon=enterprise.icon,
        description=enterprise.description,
        status=enterprise.status,
        create_time=enterprise.create_time.isoformat(),
        update_time=enterprise.update_time.isoformat()
    )


@router.post("/", response_model=EnterpriseResponse)
def create_enterprise(
    enterprise_data: EnterpriseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "create"))
):
    """创建企业"""
    try:
        enterprise = EnterpriseService.create_enterprise(db, enterprise_data)
        return EnterpriseResponse(
            id=enterprise.id,
            code=enterprise.code,
            name=enterprise.name,
            icon=enterprise.icon,
            description=enterprise.description,
            status=enterprise.status,
            create_time=enterprise.create_time.isoformat(),
            update_time=enterprise.update_time.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{enterprise_id}", response_model=EnterpriseResponse)
def update_enterprise(
    enterprise_id: int,
    enterprise_data: EnterpriseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "update"))
):
    """更新企业"""
    enterprise = EnterpriseService.update_enterprise(db, enterprise_id, enterprise_data)
    if not enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="企业不存在"
        )
    
    return EnterpriseResponse(
        id=enterprise.id,
        code=enterprise.code,
        name=enterprise.name,
        icon=enterprise.icon,
        description=enterprise.description,
        status=enterprise.status,
        create_time=enterprise.create_time.isoformat(),
        update_time=enterprise.update_time.isoformat()
    )


@router.delete("/{enterprise_id}")
def delete_enterprise(
    enterprise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "delete"))
):
    """删除企业"""
    success = EnterpriseService.delete_enterprise(db, enterprise_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="企业不存在"
        )
    
    return BaseResponse(message="企业删除成功")


@router.get("/active/list", response_model=List[EnterpriseResponse])
def get_active_enterprises(
    db: Session = Depends(get_db)
):
    """获取活跃企业列表"""
    enterprises = EnterpriseService.get_active_enterprises(db)
    
    enterprise_list = []
    for enterprise in enterprises:
        enterprise_list.append(EnterpriseResponse(
            id=enterprise.id,
            code=enterprise.code,
            name=enterprise.name,
            icon=enterprise.icon,
            description=enterprise.description,
            status=enterprise.status,
            create_time=enterprise.create_time.isoformat(),
            update_time=enterprise.update_time.isoformat()
        ))
    
    return enterprise_list


@router.get("/{enterprise_code}/users")
def get_enterprise_users(
    enterprise_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "read"))
):
    """获取企业下的用户"""
    from app.services.user_service import UserService
    users = UserService.get_users_by_enterprise(db, enterprise_code)
    
    user_list = []
    for user in users:
        user_list.append({
            "user_id": user.user_id,
            "user_name": user.user_name,
            "email": user.email,
            "nick_name": user.nick_name,
            "status": user.status
        })
    
    return BaseResponse(data={"users": user_list})


@router.post("/{enterprise_code}/add-users")
def add_users_to_enterprise(
    enterprise_code: str,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "assign"))
):
    """为企业添加用户"""
    from app.services.user_service import UserService
    from app.schemas.user import UserEnterpriseAssign
    
    user_ids = assign_data.get("user_ids", [])
    status = assign_data.get("status", 0)
    
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少用户ID列表"
        )
    
    # 创建分配数据
    assign_request = UserEnterpriseAssign(
        user_ids=user_ids,
        enterprise_code=enterprise_code,
        status=status
    )
    
    success = UserService.assign_users_to_enterprise(db, assign_request)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="添加用户失败"
        )
    
    return BaseResponse(message=f"成功为企业添加 {len(user_ids)} 个用户")


@router.delete("/{enterprise_code}/remove-users")
def remove_users_from_enterprise(
    enterprise_code: str,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "assign"))
):
    """从企业移除用户"""
    from app.models.relationships import UserEnterprise
    from sqlalchemy import and_
    
    user_ids = assign_data.get("user_ids", [])
    
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少用户ID列表"
        )
    
    # 删除用户企业关系
    deleted_count = db.query(UserEnterprise).filter(
        and_(
            UserEnterprise.enterprise_code == enterprise_code,
            UserEnterprise.user_id.in_(user_ids)
        )
    ).delete()
    
    db.commit()
    
    return BaseResponse(message=f"成功移除 {deleted_count} 个用户")


@router.get("/{enterprise_code}/roles")
def get_enterprise_roles(
    enterprise_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "read"))
):
    """获取企业的角色列表"""
    from app.services.role_service import RoleService
    roles = RoleService.get_roles_by_enterprise(db, enterprise_code)
    
    role_list = []
    for role in roles:
        role_list.append({
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "status": role.status
        })
    
    return BaseResponse(data={"roles": role_list})


@router.post("/{enterprise_code}/add-roles")
def add_roles_to_enterprise(
    enterprise_code: str,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "assign"))
):
    """为企业添加角色"""
    from app.core.permission_manager import get_permission_manager
    
    role_codes = assign_data.get("role_codes", [])
    
    if not role_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少角色代码列表"
        )
    
    permission_manager = get_permission_manager(db)
    success_count = 0
    
    for role_code in role_codes:
        if permission_manager.add_role_enterprise(role_code, enterprise_code):
            success_count += 1
    
    return BaseResponse(message=f"成功为企业添加 {success_count} 个角色")


@router.delete("/{enterprise_code}/remove-roles")
def remove_roles_from_enterprise(
    enterprise_code: str,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("enterprise", "assign"))
):
    """从企业移除角色"""
    from app.core.permission_manager import get_permission_manager
    
    role_codes = assign_data.get("role_codes", [])
    
    if not role_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少角色代码列表"
        )
    
    permission_manager = get_permission_manager(db)
    success_count = 0
    
    for role_code in role_codes:
        if permission_manager.remove_role_enterprise(role_code, enterprise_code):
            success_count += 1
    
    return BaseResponse(message=f"成功移除 {success_count} 个角色") 