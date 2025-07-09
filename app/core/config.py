from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:dev1234@10.65.14.5:3306/casbin_demo"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 应用配置
    APP_NAME: str = "权限管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS配置
    ALLOWED_HOSTS: list = ["*"]
    
    # Redis配置
    REDIS_URL: str = "redis://10.65.14.5:6379/1"
    

    
    class Config:
        env_file = ".env"


settings = Settings() 