from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "user"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    user_name = Column(String(255), nullable=False, comment="用户名")
    email = Column(String(255), comment="邮箱")
    phone_number = Column(String(255), comment="手机号")
    password = Column(String(255), nullable=False, comment="密码")
    nick_name = Column(String(255), comment="昵称")
    is_admin = Column(Integer, nullable=False, default=0, comment="是否超级管理员：0-否，1-是")
    status = Column(Integer, nullable=False, default=0, comment="状态：0-正常，1-禁用")
    icon = Column(String(255), comment="头像")
    username = Column(Text, comment="用户名")
    nickname = Column(Text, comment="昵称")
    remark = Column(Text, comment="备注")
    dept_id = Column(Text, comment="部门ID")
    group_id = Column(Text, comment="组织ID")
    dept_name = Column(Text, comment="部门名称")
    mobile = Column(Text, comment="手机号")
    sex = Column(Text, comment="性别")
    avatar = Column(Text, comment="头像")
    login_ip = Column(Text, comment="登录IP")
    login_date = Column(Text, comment="登录时间")
    creator = Column(Text, comment="创建者")
    group_name = Column(Text, comment="组织名称")
    third_uid = Column(String(64), unique=True, nullable=False, comment="第三方用户ID")
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 