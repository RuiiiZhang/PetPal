# PetPal 部署配置

## 架构

```
用户请求 → Nginx(:80/443) → Frontend(Next.js:3000)
                           → Backend(FastAPI:8000)
                                → PostgreSQL:5432
                                → Redis:6379
```

## 快速部署

### 1. 准备服务器

阿里云 ECS（推荐 2核4G 以上），安装 Ubuntu 22.04。

### 2. 一键部署

```bash
cd deploy/
chmod +x deploy.sh
./deploy.sh deploy
```

脚本会自动：
- 检查并安装 Docker / Docker Compose
- 从模板创建 `.env` 配置文件
- 构建并启动所有服务
- 执行健康检查

### 3. 配置域名（可选）

```bash
# 编辑 .env，设置你的域名
vim .env

# 申请 HTTPS 证书
./deploy.sh https

# 设置自动续期
./deploy.sh renew
```

### 4. HTTPS 配置

编辑 `nginx/nginx.conf`，取消 HTTPS server 块的注释，替换 `your-domain.com`：

```bash
vim nginx/nginx.conf
# 取消 HTTPS 配置段的注释
# 重启 nginx
docker compose restart nginx
```

## 环境变量

复制 `.env.example` 为 `.env`，修改以下关键配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SITE_URL` | 站点域名 | `https://petpal.com` |
| `DB_PASSWORD` | 数据库密码 | 自动生成 |
| `CERTBOT_EMAIL` | Let's Encrypt 邮箱 | - |
| `CERTBOT_DOMAIN` | 证书域名 | - |

## 常用命令

```bash
# 查看状态
docker compose ps

# 查看日志
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx

# 重启单个服务
docker compose restart backend

# 停止所有服务
docker compose down

# 重建并重启
docker compose up -d --build

# 清理无用镜像
docker system prune -f
```

## 目录结构

```
deploy/
├── Dockerfile.backend     # 后端镜像
├── Dockerfile.frontend    # 前端镜像
├── docker-compose.yml     # 服务编排
├── nginx/
│   ├── Dockerfile         # Nginx 镜像
│   └── nginx.conf         # Nginx 配置
├── .env.example           # 环境变量模板
├── deploy.sh              # 部署脚本
└── README.md              # 本文档
```

## 阿里云安全组配置

确保开放以下端口：
- **80** - HTTP
- **443** - HTTPS
- **22** - SSH（建议限制 IP）

## 数据备份

```bash
# 备份数据库
docker exec petpal-postgres pg_dump -U petpal petpal > backup_$(date +%Y%m%d).sql

# 恢复数据库
cat backup.sql | docker exec -i petpal-postgres psql -U petpal petpal
```
