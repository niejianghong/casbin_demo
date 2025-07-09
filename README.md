# Casbin权限管理系统

基于Casbin的集团级用户权限管理系统，支持多企业、多角色、多资源的权限控制。

## 功能特性

- 🔐 基于Casbin的RBAC权限控制
- 🏢 多企业支持，企业间资源隔离
- 👥 用户、角色、资源、组织管理
- 🔑 JWT认证和授权
- 📱 响应式Web界面
- 🚀 FastAPI + React技术栈

## 系统架构

### 后端技术栈
- **Python 3.11+**
- **FastAPI** - 现代、快速的Web框架
- **SQLAlchemy** - ORM框架
- **Casbin** - 权限控制引擎
- **MySQL** - 数据库
- **JWT** - 身份认证
- **Poetry** - 依赖管理

### 前端技术栈
- **React 18** - 用户界面库
- **TypeScript** - 类型安全
- **Ant Design** - UI组件库
- **Vite** - 构建工具
- **Zustand** - 状态管理
- **Axios** - HTTP客户端

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 16+
- MySQL 8.0+

### 后端启动

1. 安装依赖
```bash
cd /path/to/project
poetry install
```

2. 配置数据库
```bash
# 修改 app/core/config.py 中的数据库连接信息
DATABASE_URL = "mysql+pymysql://username:password@host:port/database"
```

3. 启动服务
```bash
poetry run python main.py
```

服务将在 http://localhost:8000 启动

### 前端启动

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

前端将在 http://localhost:3000 启动

## 数据库设计

### 核心表结构

- `enterprise` - 企业表
- `user` - 用户表
- `role` - 角色表
- `resource` - 资源表
- `organization` - 组织表
- `user_enterprise` - 用户企业关系表
- `user_role` - 用户角色关系表
- `role_enterprise` - 角色企业关系表
- `resource_role` - 资源角色关系表
- `user_organization` - 用户组织关系表

### 权限控制流程

1. 用户登录时指定企业
2. 验证用户是否属于该企业
3. 获取用户在该企业下的角色
4. 通过Casbin检查角色对资源的权限
5. 返回权限验证结果

## API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能模块

### 用户管理
- 用户创建、编辑、删除
- 用户企业分配
- 用户角色分配
- 用户状态管理

### 企业管理
- 企业创建、编辑、删除
- 企业状态管理
- 企业信息配置

### 角色管理
- 角色创建、编辑、删除
- 角色企业分配
- 角色权限配置

### 资源管理
- 资源创建、编辑、删除
- 资源类型管理（API、Menu、Agent）
- 资源角色分配
- 菜单树结构

### 权限控制
- 基于Casbin的RBAC权限模型
- 企业维度权限隔离
- 角色维度权限控制
- 资源访问权限验证

## 开发指南

### 代码结构
```
casbin_demo/
├── app/                    # 后端应用
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   └── schemas/           # 数据模式
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── pages/         # 页面
│   │   ├── services/      # API服务
│   │   ├── types/         # 类型定义
│   │   └── utils/         # 工具函数
│   └── public/            # 静态资源
└── main.py               # 应用入口
```

### 开发规范
- 使用Black进行代码格式化
- 使用isort进行导入排序
- 使用flake8进行代码检查
- 遵循PEP 8编码规范

## 部署

### 生产环境部署
1. 配置生产环境变量
2. 使用Gunicorn启动后端服务
3. 构建前端静态文件
4. 配置Nginx反向代理

### Docker部署
```bash
# 构建镜像
docker build -t casbin-demo .

# 运行容器
docker run -d -p 8000:8000 casbin-demo
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请通过以下方式联系：
- 邮箱: your.email@example.com
- GitHub: https://github.com/your-username/casbin-demo 