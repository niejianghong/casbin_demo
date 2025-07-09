from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.resource_service import ResourceService
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceRoleAssign
from app.schemas.base import BaseResponse, PaginatedResponse
from app.core.auth import get_current_user, check_permission
from app.models.user import User
from app.models.resource import Resource

router = APIRouter(prefix="/resources", tags=["资源管理"])


@router.get("/", response_model=PaginatedResponse)
def get_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    resource_type: int = Query(None, description="资源类型：1-API，2-Menu，3-Agent"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取资源列表"""
    if resource_type:
        resources = ResourceService.get_resources_by_type(db, resource_type)
        total = db.query(Resource).filter(Resource.type == resource_type).count()
    else:
        resources = ResourceService.get_resources(db, skip=skip, limit=limit)
        total = db.query(Resource).count()
    
    resource_list = []
    for resource in resources:
        resource_list.append(ResourceResponse(
            id=resource.id,
            name=resource.name,
            code=resource.code,
            type=resource.type,
            path=resource.path,
            act=resource.act,
            parent_code=resource.parent_code,
            status=resource.status,
            create_time=resource.create_time.isoformat(),
            update_time=resource.update_time.isoformat()
        ))
    
    return PaginatedResponse(
        data={"resources": resource_list},
        pagination={
            "page": skip // limit + 1,
            "size": limit,
            "total": total
        }
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取资源详情"""
    resource = ResourceService.get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    return ResourceResponse(
        id=resource.id,
        name=resource.name,
        code=resource.code,
        type=resource.type,
        path=resource.path,
        act=resource.act,
        parent_code=resource.parent_code,
        status=resource.status,
        create_time=resource.create_time.isoformat(),
        update_time=resource.update_time.isoformat()
    )


@router.post("/", response_model=ResourceResponse)
def create_resource(
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "create"))
):
    """创建资源"""
    try:
        resource = ResourceService.create_resource(db, resource_data)
        return ResourceResponse(
            id=resource.id,
            name=resource.name,
            code=resource.code,
            type=resource.type,
            path=resource.path,
            act=resource.act,
            parent_code=resource.parent_code,
            status=resource.status,
            create_time=resource.create_time.isoformat(),
            update_time=resource.update_time.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "update"))
):
    """更新资源"""
    resource = ResourceService.update_resource(db, resource_id, resource_data)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    return ResourceResponse(
        id=resource.id,
        name=resource.name,
        code=resource.code,
        type=resource.type,
        path=resource.path,
        act=resource.act,
        parent_code=resource.parent_code,
        status=resource.status,
        create_time=resource.create_time.isoformat(),
        update_time=resource.update_time.isoformat()
    )


@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "delete"))
):
    """删除资源"""
    success = ResourceService.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    return BaseResponse(message="资源删除成功")


@router.post("/assign-role")
def assign_resource_to_roles(
    assign_data: ResourceRoleAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "assign"))
):
    """分配资源到角色"""
    success = ResourceService.assign_resource_to_roles(db, assign_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配失败"
        )
    
    return BaseResponse(message="资源分配成功")


@router.get("/menu/tree")
def get_menu_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取菜单树结构"""
    menu_tree = ResourceService.get_menu_tree(db)
    return BaseResponse(data={"menu_tree": menu_tree})


@router.get("/active/list", response_model=List[ResourceResponse])
def get_active_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取活跃资源列表"""
    resources = ResourceService.get_active_resources(db)
    
    resource_list = []
    for resource in resources:
        resource_list.append(ResourceResponse(
            id=resource.id,
            name=resource.name,
            code=resource.code,
            type=resource.type,
            path=resource.path,
            act=resource.act,
            parent_code=resource.parent_code,
            status=resource.status,
            create_time=resource.create_time.isoformat(),
            update_time=resource.update_time.isoformat()
        ))
    
    return resource_list


@router.get("/role/{role_code}")
def get_role_resources(
    role_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取角色的资源列表"""
    from app.models.relationships import ResourceRole
    
    resource_roles = db.query(ResourceRole).filter(
        ResourceRole.role_code == role_code
    ).all()
    
    resource_list = []
    for resource_role in resource_roles:
        resource = db.query(Resource).filter(
            Resource.code == resource_role.resource_code
        ).first()
        if resource:
            resource_list.append({
                "id": resource.id,
                "name": resource.name,
                "code": resource.code,
                "type": resource.type,
                "path": resource.path,
                "act": resource.act,
                "parent_code": resource.parent_code,
                "status": resource.status
            })
    
    return BaseResponse(data={"resources": resource_list})


@router.post("/role/{role_code}/add-resources")
def add_resources_to_role(
    role_code: str,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "assign"))
):
    """为角色添加资源"""
    from app.core.permission_manager import get_permission_manager
    
    resource_codes = assign_data.get("resource_codes", [])
    
    if not resource_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少资源代码列表"
        )
    
    permission_manager = get_permission_manager(db)
    success_count = 0
    
    for resource_code in resource_codes:
        if permission_manager.add_resource_role(resource_code, role_code):
            success_count += 1
    
    return BaseResponse(message=f"成功为角色添加 {success_count} 个资源")


@router.delete("/role/{role_code}/remove-resources")
def remove_resources_from_role(
    role_code: str,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "assign"))
):
    """从角色移除资源"""
    from app.core.permission_manager import get_permission_manager
    
    resource_codes = assign_data.get("resource_codes", [])
    
    if not resource_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少资源代码列表"
        )
    
    permission_manager = get_permission_manager(db)
    success_count = 0
    
    for resource_code in resource_codes:
        if permission_manager.remove_resource_role(resource_code, role_code):
            success_count += 1
    
    return BaseResponse(message=f"成功移除 {success_count} 个资源") 