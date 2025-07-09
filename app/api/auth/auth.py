from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserLogin, UserLoginResponse, UserCreate, UserResponse
from app.schemas.base import BaseResponse
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=UserLoginResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 验证用户
    user = UserService.authenticate_user(db, user_data.user_name, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户状态
    if user.status != 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 检查用户是否属于指定企业
    if user.user_name != "admin" and user.is_admin != 1:
        from app.models.relationships import UserEnterprise
        user_enterprise = db.query(UserEnterprise).filter(
            UserEnterprise.user_id == user.user_id,
            UserEnterprise.enterprise_code == user_data.enterprise_code,
            UserEnterprise.status == 0
        ).first()
        
        if not user_enterprise:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户不属于该企业"
            )
    
    # 创建访问令牌
    access_token = UserService.create_access_token_for_user(user, user_data.enterprise_code)
    
    return UserLoginResponse(
        access_token=access_token,
        user=UserResponse(
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
        ),
        enterprise_code=user_data.enterprise_code
    )


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
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


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        nick_name=current_user.nick_name,
        is_admin=current_user.is_admin,
        status=current_user.status,
        icon=current_user.icon,
        third_uid=current_user.third_uid,
        create_time=current_user.create_time.isoformat(),
        update_time=current_user.update_time.isoformat()
    ) 