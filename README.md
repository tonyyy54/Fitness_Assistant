# Fitness Assistant

Fitness Assistant 是一个健康管理应用。当前仓库包含基于 FastAPI、PostgreSQL、SQLAlchemy 和 Docker Compose 构建的后端基础工程。

## 当前功能

- FastAPI 应用与 Swagger API 文档
- PostgreSQL 数据库
- SQLAlchemy 数据访问层
- Alembic 数据库迁移
- 用户基础数据模型
- API 与数据库健康检查
- pytest 自动化测试
- Ruff 代码检查与格式化

## 技术栈

- Python 3.12
- FastAPI 0.139
- PostgreSQL 17
- SQLAlchemy 2
- Psycopg 3
- Alembic
- Docker Compose
- pytest
- Ruff

## 项目结构

```text
fitness-projet/
├── backend/
│   ├── alembic/              # 数据库迁移环境和版本文件
│   ├── app/
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   ├── routers/          # API 路由
│   │   ├── schemas/          # 请求和响应数据结构
│   │   ├── services/         # 业务逻辑
│   │   ├── config.py         # 环境变量配置
│   │   ├── database.py       # 数据库连接与 Session
│   │   ├── dependencies.py   # FastAPI 公共依赖
│   │   └── main.py           # FastAPI 应用入口
│   ├── tests/                # 自动化测试
│   ├── .env.example          # 环境变量模板
│   ├── alembic.ini           # Alembic 配置
│   ├── Dockerfile
│   ├── pyproject.toml        # pytest 与 Ruff 配置
│   ├── requirements.txt      # 运行依赖
│   └── requirements-dev.txt  # 开发与测试依赖
├── docker-compose.yml
└── README.md
```

## 环境要求

开始前请安装并启动：

- Docker Desktop
- Git

确认 Docker Engine 正常：

```bash
docker info --format '{{.ServerVersion}}'
```

## 首次启动

克隆仓库并进入项目目录：

```bash
git clone https://github.com/tonyyy54/Fitness_Assistant.git
cd Fitness_Assistant
```

根据模板创建本地环境变量文件：

```bash
cp backend/.env.example backend/.env
```

`backend/.env` 包含本地数据库密码，已被 Git 忽略，请勿提交。

构建并启动 API 与 PostgreSQL：

```bash
docker compose up --build -d
```

检查服务状态：

```bash
docker compose ps
```

正常情况下应看到：

- `fitness-api`：运行中
- `fitness-db`：运行中且状态为 `healthy`

## 数据库迁移

首次启动后，将数据库升级到最新迁移版本：

```bash
docker compose exec api alembic upgrade head
```

检查当前迁移版本：

```bash
docker compose exec api alembic current
```

检查 SQLAlchemy 模型与数据库结构是否一致：

```bash
docker compose exec api alembic check
```

创建新迁移时使用：

```bash
docker compose exec api alembic revision --autogenerate -m "describe schema change"
```

生成迁移后必须先检查 `backend/alembic/versions/` 中的文件，再执行 `alembic upgrade head`。

## API 地址

服务启动后可以访问：

- API 健康检查：http://localhost:8000/health
- 数据库健康检查：http://localhost:8000/health/database
- Swagger API 文档：http://localhost:8000/docs
- OpenAPI JSON：http://localhost:8000/openapi.json

快速验证：

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/database
```

## 自动化测试

运行全部测试：

```bash
docker compose exec api pytest -v
```

当前测试包括：

- API 进程健康检查
- API 到 PostgreSQL 的连接检查

## 代码检查与格式化

检查 Python 代码：

```bash
docker compose exec api ruff check app tests alembic/env.py
```

自动修复安全的检查问题：

```bash
docker compose exec api ruff check app tests alembic/env.py --fix
```

格式化代码：

```bash
docker compose exec api ruff format app tests alembic/env.py
```

只检查格式而不修改文件：

```bash
docker compose exec api ruff format --check app tests alembic/env.py
```

提交代码前建议依次运行：

```bash
docker compose exec api ruff check app tests alembic/env.py
docker compose exec api ruff format --check app tests alembic/env.py
docker compose exec api pytest -v
docker compose exec api alembic check
```

## 查看日志

查看 API 日志：

```bash
docker compose logs -f api
```

查看 PostgreSQL 日志：

```bash
docker compose logs -f db
```

按 `Control + C` 退出日志查看，不会停止容器。

## 停止与重新启动

停止服务并保留数据库数据：

```bash
docker compose down
```

重新启动：

```bash
docker compose up -d
```

只有在确定要删除本地数据库数据时，才执行：

```bash
docker compose down -v
```

`-v` 会永久删除本项目的 PostgreSQL 数据卷。

## 开发状态

后端基础工程已经完成。下一阶段计划实现：

1. 用户注册
2. 用户登录与 JWT 身份认证
3. 用户身体信息采集
4. BMI、BMR、TDEE 与减脂计划计算
5. React Native 移动端

## 安全说明

- 不要提交 `backend/.env`。
- 不要在代码或日志中输出密码、JWT 或数据库凭据。
- 用户密码只能保存安全哈希，不能保存明文。
- 当前项目用于健康管理开发学习，不提供医疗诊断。
