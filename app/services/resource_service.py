from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.resource import Resource
from app.models.relationships import ResourceRole, ResourceEnterprise
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceRoleAssign
from app.core.permission_manager import get_permission_manager


class ResourceService:
    """资源服务"""
    
    @staticmethod
    def create_resource(db: Session, resource_data: ResourceCreate) -> Resource:
        """创建资源"""
        # 检查资源代码是否已存在
        if resource_data.code:
            existing_resource = db.query(Resource).filter(
                Resource.code == resource_data.code
            ).first()
            if existing_resource:
                raise ValueError("资源代码已存在")
        
        # 创建资源
        db_resource = Resource(
            name=resource_data.name,
            code=resource_data.code,
            type=resource_data.type,
            path=resource_data.path,
            act=resource_data.act,
            parent_code=resource_data.parent_code,
            status=resource_data.status
        )
        
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        
        return db_resource
    
    @staticmethod
    def get_resource_by_id(db: Session, resource_id: int) -> Optional[Resource]:
        """根据ID获取资源"""
        return db.query(Resource).filter(Resource.id == resource_id).first()
    
    @staticmethod
    def get_resource_by_code(db: Session, resource_code: str) -> Optional[Resource]:
        """根据代码获取资源"""
        return db.query(Resource).filter(Resource.code == resource_code).first()
    
    @staticmethod
    def get_resources(db: Session, enterprise_code: str = None, skip: int = 0, limit: int = 100, user_id: int = None) -> List[Resource]:
        """获取资源列表"""
        # 如果指定了企业代码，按企业过滤
        if enterprise_code:
            # 通过关联表查询企业下的资源
            resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                ResourceEnterprise.enterprise_code == enterprise_code
            ).subquery()
            query = db.query(Resource).filter(Resource.code.in_(resource_codes))
        else:
            # 如果没有指定企业代码，检查是否为超级管理员
            if user_id:
                from app.core.permission_manager import get_permission_manager
                permission_manager = get_permission_manager(db)
                if permission_manager._is_super_admin(user_id):
                    # 超级管理员可以看到所有资源
                    query = db.query(Resource)
                else:
                    # 普通用户只能看到自己企业的资源
                    user_enterprises = permission_manager.get_user_enterprises(user_id)
                    if user_enterprises:
                        resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                            ResourceEnterprise.enterprise_code.in_(user_enterprises)
                        ).subquery()
                        query = db.query(Resource).filter(Resource.code.in_(resource_codes))
                    else:
                        # 用户没有企业，返回空列表
                        return []
            else:
                # 没有用户ID，返回所有资源
                query = db.query(Resource)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_resources_by_type(db: Session, resource_type: int, enterprise_code: str = None, user_id: int = None) -> List[Resource]:
        """根据类型获取资源"""
        # 如果指定了企业代码，按企业过滤
        if enterprise_code:
            # 通过关联表查询企业下的指定类型资源
            resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                ResourceEnterprise.enterprise_code == enterprise_code
            ).subquery()
            query = db.query(Resource).filter(
                Resource.type == resource_type,
                Resource.code.in_(resource_codes)
            )
        else:
            # 如果没有指定企业代码，检查是否为超级管理员
            if user_id:
                from app.core.permission_manager import get_permission_manager
                permission_manager = get_permission_manager(db)
                if permission_manager._is_super_admin(user_id):
                    # 超级管理员可以看到所有资源
                    query = db.query(Resource).filter(Resource.type == resource_type)
                else:
                    # 普通用户只能看到自己企业的资源
                    user_enterprises = permission_manager.get_user_enterprises(user_id)
                    if user_enterprises:
                        resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                            ResourceEnterprise.enterprise_code.in_(user_enterprises)
                        ).subquery()
                        query = db.query(Resource).filter(
                            Resource.type == resource_type,
                            Resource.code.in_(resource_codes)
                        )
                    else:
                        # 用户没有企业，返回空列表
                        return []
            else:
                # 没有用户ID，返回所有资源
                query = db.query(Resource).filter(Resource.type == resource_type)
        return query.all()
    
    @staticmethod
    def update_resource(db: Session, resource_id: int, resource_data: ResourceUpdate) -> Optional[Resource]:
        """更新资源"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            return None
        
        update_data = resource_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_resource, field, value)
        
        db.commit()
        db.refresh(db_resource)
        return db_resource
    
    @staticmethod
    def delete_resource(db: Session, resource_id: int) -> bool:
        """删除资源"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            return False
        
        # 删除资源关联的权限
        db.query(ResourceRole).filter(ResourceRole.resource_code == db_resource.code).delete()
        
        # 删除资源关联的企业
        db.query(ResourceEnterprise).filter(ResourceEnterprise.resource_code == db_resource.code).delete()
        
        db.delete(db_resource)
        db.commit()
        return True
    
    @staticmethod
    def assign_resource_to_roles(db: Session, assign_data: ResourceRoleAssign) -> bool:
        """分配资源到角色"""
        permission_manager = get_permission_manager(db)
        
        # 删除现有的分配关系
        db.query(ResourceRole).filter(
            ResourceRole.resource_code == assign_data.resource_code
        ).delete()
        
        # 创建新的分配关系
        for role_code in assign_data.role_codes:
            permission_manager.add_resource_role(assign_data.resource_code, role_code)
        
        return True
    
    @staticmethod
    def get_resource_roles(db: Session, resource_code: str) -> List[ResourceRole]:
        """获取资源的角色"""
        return db.query(ResourceRole).filter(
            ResourceRole.resource_code == resource_code
        ).all()
    
    @staticmethod
    def get_role_resources(db: Session, role_code: str) -> List[ResourceRole]:
        """获取角色的资源"""
        return db.query(ResourceRole).filter(
            ResourceRole.role_code == role_code
        ).all()
    
    @staticmethod
    def get_active_resources(db: Session, enterprise_code: str = None, user_id: int = None) -> List[Resource]:
        """获取活跃资源列表"""
        # 如果指定了企业代码，按企业过滤
        if enterprise_code:
            # 通过关联表查询企业下的活跃资源
            resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                ResourceEnterprise.enterprise_code == enterprise_code
            ).subquery()
            query = db.query(Resource).filter(
                Resource.status == 0,
                Resource.code.in_(resource_codes)
            )
        else:
            # 如果没有指定企业代码，检查是否为超级管理员
            if user_id:
                from app.core.permission_manager import get_permission_manager
                permission_manager = get_permission_manager(db)
                if permission_manager._is_super_admin(user_id):
                    # 超级管理员可以看到所有资源
                    query = db.query(Resource).filter(Resource.status == 0)
                else:
                    # 普通用户只能看到自己企业的资源
                    user_enterprises = permission_manager.get_user_enterprises(user_id)
                    if user_enterprises:
                        resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                            ResourceEnterprise.enterprise_code.in_(user_enterprises)
                        ).subquery()
                        query = db.query(Resource).filter(
                            Resource.status == 0,
                            Resource.code.in_(resource_codes)
                        )
                    else:
                        # 用户没有企业，返回空列表
                        return []
            else:
                # 没有用户ID，返回所有资源
                query = db.query(Resource).filter(Resource.status == 0)
        return query.all()
    
    @staticmethod
    def get_menu_tree(db: Session, enterprise_code: str = None, user_id: int = None) -> List[dict]:
        """获取菜单树结构"""
        # 如果指定了企业代码，按企业过滤
        if enterprise_code:
            # 通过关联表查询企业下的菜单资源
            resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                ResourceEnterprise.enterprise_code == enterprise_code
            ).subquery()
            query = db.query(Resource).filter(
                Resource.type == 2,  # Menu类型
                Resource.status == 0,
                Resource.code.in_(resource_codes)
            )
        else:
            # 如果没有指定企业代码，检查是否为超级管理员
            if user_id:
                from app.core.permission_manager import get_permission_manager
                permission_manager = get_permission_manager(db)
                if permission_manager._is_super_admin(user_id):
                    # 超级管理员可以看到所有菜单
                    query = db.query(Resource).filter(
                        Resource.type == 2,  # Menu类型
                        Resource.status == 0
                    )
                else:
                    # 普通用户只能看到自己企业的菜单
                    user_enterprises = permission_manager.get_user_enterprises(user_id)
                    if user_enterprises:
                        resource_codes = db.query(ResourceEnterprise.resource_code).filter(
                            ResourceEnterprise.enterprise_code.in_(user_enterprises)
                        ).subquery()
                        query = db.query(Resource).filter(
                            Resource.type == 2,  # Menu类型
                            Resource.status == 0,
                            Resource.code.in_(resource_codes)
                        )
                    else:
                        # 用户没有企业，返回空列表
                        return []
            else:
                # 没有用户ID，返回所有菜单
                query = db.query(Resource).filter(
                    Resource.type == 2,  # Menu类型
                    Resource.status == 0
                )
        resources = query.all()
        
        # 构建树结构
        menu_dict = {}
        menu_tree = []
        
        for resource in resources:
            menu_dict[resource.code] = {
                "id": resource.id,
                "code": resource.code,
                "name": resource.name,
                "path": resource.path,
                "parent_code": resource.parent_code,
                "children": []
            }
        
        for code, menu in menu_dict.items():
            if menu["parent_code"] and menu["parent_code"] in menu_dict:
                menu_dict[menu["parent_code"]]["children"].append(menu)
            else:
                menu_tree.append(menu)
        
        return menu_tree
    
    @staticmethod
    def assign_resource_to_enterprises(db: Session, resource_code: str, enterprise_codes: List[str]) -> bool:
        """分配资源到企业"""
        # 删除现有的企业关联
        db.query(ResourceEnterprise).filter(
            ResourceEnterprise.resource_code == resource_code
        ).delete()
        
        # 创建新的企业关联
        for enterprise_code in enterprise_codes:
            resource_enterprise = ResourceEnterprise(
                resource_code=resource_code,
                enterprise_code=enterprise_code
            )
            db.add(resource_enterprise)
        
        db.commit()
        return True
    
    @staticmethod
    def get_resource_enterprises(db: Session, resource_code: str) -> List[ResourceEnterprise]:
        """获取资源关联的企业"""
        return db.query(ResourceEnterprise).filter(
            ResourceEnterprise.resource_code == resource_code
        ).all()
    
    @staticmethod
    def get_enterprise_resources(db: Session, enterprise_code: str) -> List[ResourceEnterprise]:
        """获取企业关联的资源"""
        return db.query(ResourceEnterprise).filter(
            ResourceEnterprise.enterprise_code == enterprise_code
        ).all() 