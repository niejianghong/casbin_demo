from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.resource import Resource
from app.models.relationships import ResourceRole
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
    def get_resources(db: Session, skip: int = 0, limit: int = 100) -> List[Resource]:
        """获取资源列表"""
        return db.query(Resource).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_resources_by_type(db: Session, resource_type: int) -> List[Resource]:
        """根据类型获取资源"""
        return db.query(Resource).filter(Resource.type == resource_type).all()
    
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
    def get_active_resources(db: Session) -> List[Resource]:
        """获取活跃资源列表"""
        return db.query(Resource).filter(Resource.status == 0).all()
    
    @staticmethod
    def get_menu_tree(db: Session) -> List[dict]:
        """获取菜单树结构"""
        resources = db.query(Resource).filter(
            Resource.type == 2,  # Menu类型
            Resource.status == 0
        ).all()
        
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