from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.enterprise import Enterprise
from app.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate


class EnterpriseService:
    """企业服务"""
    
    @staticmethod
    def create_enterprise(db: Session, enterprise_data: EnterpriseCreate) -> Enterprise:
        """创建企业"""
        # 检查企业代码是否已存在
        existing_enterprise = db.query(Enterprise).filter(
            Enterprise.code == enterprise_data.code
        ).first()
        if existing_enterprise:
            raise ValueError("企业代码已存在")
        
        # 创建企业
        db_enterprise = Enterprise(
            code=enterprise_data.code,
            name=enterprise_data.name,
            icon=enterprise_data.icon,
            description=enterprise_data.description,
            status=enterprise_data.status
        )
        
        db.add(db_enterprise)
        db.commit()
        db.refresh(db_enterprise)
        
        return db_enterprise
    
    @staticmethod
    def get_enterprise_by_id(db: Session, enterprise_id: int) -> Optional[Enterprise]:
        """根据ID获取企业"""
        return db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
    
    @staticmethod
    def get_enterprise_by_code(db: Session, enterprise_code: str) -> Optional[Enterprise]:
        """根据代码获取企业"""
        return db.query(Enterprise).filter(Enterprise.code == enterprise_code).first()
    
    @staticmethod
    def get_enterprises(db: Session, skip: int = 0, limit: int = 100) -> List[Enterprise]:
        """获取企业列表"""
        return db.query(Enterprise).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_enterprise(db: Session, enterprise_id: int, enterprise_data: EnterpriseUpdate) -> Optional[Enterprise]:
        """更新企业"""
        db_enterprise = db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
        if not db_enterprise:
            return None
        
        update_data = enterprise_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_enterprise, field, value)
        
        db.commit()
        db.refresh(db_enterprise)
        return db_enterprise
    
    @staticmethod
    def delete_enterprise(db: Session, enterprise_id: int) -> bool:
        """删除企业"""
        db_enterprise = db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
        if not db_enterprise:
            return False
        
        db.delete(db_enterprise)
        db.commit()
        return True
    
    @staticmethod
    def get_active_enterprises(db: Session) -> List[Enterprise]:
        """获取活跃企业列表"""
        return db.query(Enterprise).filter(Enterprise.status == 0).all() 