from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.resource_service import ResourceService
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceRoleAssign, ResourceEnterpriseAssign
from app.schemas.base import BaseResponse, PaginatedResponse
from app.core.auth import get_current_user, check_permission
from app.models.user import User
from app.models.resource import Resource
from app.models.relationships import ResourceEnterprise

router = APIRouter(prefix="/resources", tags=["资源管理"])


@router.get("/", response_model=PaginatedResponse)
def get_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    resource_type: int = Query(None, description="资源类型：1-API，2-Menu，3-Agent"),
    enterprise_code: str = Query(None, description="企业代码"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取资源列表"""
    # 如果没有指定企业代码，使用当前用户的第一个企业
    if not enterprise_code and current_user.is_admin != 1:
        from app.core.permission_manager import get_permission_manager
        permission_manager = get_permission_manager(db)
        user_enterprises = permission_manager.get_user_enterprises(current_user.user_id)
        if user_enterprises:
            enterprise_code = user_enterprises[0]

    if current_user.is_admin == 1:
        enterprise_code = None
    
    if resource_type:
        resources = ResourceService.get_resources_by_type(db, resource_type, enterprise_code, user_id=current_user.user_id)
        # 计算总数
        if enterprise_code:
            resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                ResourceEnterprise.enterprise_code == enterprise_code
            ).subquery()
            total = db.query(Resource).filter(
                Resource.type == resource_type,
                Resource.code.in_(resource_codes)
            ).count()
        else:
            # 超级管理员或没有企业限制时
            total = db.query(Resource).filter(Resource.type == resource_type).count()
    else:
        resources = ResourceService.get_resources(db, enterprise_code, skip=skip, limit=limit, user_id=current_user.user_id)
        # 计算总数
        if enterprise_code:
            resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                ResourceEnterprise.enterprise_code == enterprise_code
            ).subquery()
            total = db.query(Resource).filter(Resource.code.in_(resource_codes)).count()
        else:
            # 超级管理员或没有企业限制时
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


@router.post("/assign-enterprise")
def assign_resource_to_enterprises(
    assign_data: ResourceEnterpriseAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "assign"))
):
    """分配资源到企业"""
    success = ResourceService.assign_resource_to_enterprises(db, assign_data.resource_code, assign_data.enterprise_codes)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配失败"
        )
    
    return BaseResponse(message="资源企业分配成功")


@router.get("/{resource_code}/enterprises")
def get_resource_enterprises(
    resource_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取资源关联的企业"""
    enterprises = ResourceService.get_resource_enterprises(db, resource_code)
    enterprise_list = []
    for enterprise in enterprises:
        enterprise_list.append({
            "enterprise_code": enterprise.enterprise_code,
            "create_time": enterprise.create_time.isoformat()
        })
    
    return BaseResponse(data={"enterprises": enterprise_list})


@router.get("/enterprise/{enterprise_code}")
def get_enterprise_resources(
    enterprise_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取企业关联的资源"""
    resources = ResourceService.get_enterprise_resources(db, enterprise_code)
    resource_list = []
    for resource_rel in resources:
        resource = ResourceService.get_resource_by_code(db, resource_rel.resource_code)
        if resource:
            resource_list.append({
                "resource_code": resource_rel.resource_code,
                "resource_name": resource.name,
                "resource_type": resource.type,
                "create_time": resource_rel.create_time.isoformat()
            })
    
    return BaseResponse(data={"resources": resource_list})


@router.get("/menu/tree")
def get_menu_tree(
    enterprise_code: str = Query(None, description="企业代码"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取菜单树结构"""
    # 如果没有指定企业代码，使用当前用户的第一个企业
    if not enterprise_code:
        from app.core.permission_manager import get_permission_manager
        permission_manager = get_permission_manager(db)
        user_enterprises = permission_manager.get_user_enterprises(current_user.user_id)
        if user_enterprises:
            enterprise_code = user_enterprises[0]
    
    menu_tree = ResourceService.get_menu_tree(db, enterprise_code, user_id=current_user.user_id)
    return BaseResponse(data={"menu_tree": menu_tree})


@router.get("/active/list", response_model=List[ResourceResponse])
def get_active_resources(
    enterprise_code: str = Query(None, description="企业代码"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "read"))
):
    """获取活跃资源列表"""
    # 如果没有指定企业代码，使用当前用户的第一个企业
    if not enterprise_code:
        from app.core.permission_manager import get_permission_manager
        permission_manager = get_permission_manager(db)
        user_enterprises = permission_manager.get_user_enterprises(current_user.user_id)
        if user_enterprises:
            enterprise_code = user_enterprises[0]
    
    resources = ResourceService.get_active_resources(db, enterprise_code, user_id=current_user.user_id)
    
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
    """获取角色的资源"""
    resource_roles = ResourceService.get_role_resources(db, role_code)
    
    resource_list = []
    for resource_role in resource_roles:
        resource = ResourceService.get_resource_by_code(db, resource_role.resource_code)
        if resource:
            resource_list.append({
                "resource_code": resource_role.resource_code,
                "resource_name": resource.name,
                "resource_type": resource.type,
                "assign_time": resource_role.create_time.isoformat()
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
    resource_codes = assign_data.get("resource_codes", [])
    
    for resource_code in resource_codes:
        assign_data_obj = ResourceRoleAssign(
            resource_code=resource_code,
            role_codes=[role_code]
        )
        ResourceService.assign_resource_to_roles(db, assign_data_obj)
    
    return BaseResponse(message="资源添加成功")


@router.delete("/role/{role_code}/remove-resources")
def remove_resources_from_role(
    role_code: str,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("resource", "assign"))
):
    """从角色移除资源"""
    resource_codes = assign_data.get("resource_codes", [])
    
    for resource_code in resource_codes:
        # 获取当前资源的角色分配
        current_roles = ResourceService.get_resource_roles(db, resource_code)
        current_role_codes = [rr.role_code for rr in current_roles]
        
        # 移除指定角色
        if role_code in current_role_codes:
            current_role_codes.remove(role_code)
            
            # 重新分配角色
            assign_data_obj = ResourceRoleAssign(
                resource_code=resource_code,
                role_codes=current_role_codes
            )
            ResourceService.assign_resource_to_roles(db, assign_data_obj)
    
    return BaseResponse(message="资源移除成功") 