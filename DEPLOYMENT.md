# AI 智能客服系统 - 部署指南

本文档提供详细的部署和运维指导。

## 目录

1. [环境要求](#环境要求)
2. [快速部署](#快速部署)
3. [Docker 部署](#docker-部署)
4. [Railway 部署](#railway-部署)
5. [手动部署](#手动部署)
6. [配置说明](#配置说明)
7. [监控与运维](#监控与运维)
8. [故障排查](#故障排查)

---

## 环境要求

### 基础环境

- **Python**: 3.9+
- **Node.js**: 18+
- **PostgreSQL**: 12+
- **Redis** (可选): 6+
- **Docker & Docker Compose** (推荐)

### 系统资源建议

| 部署规模 | CPU | 内存 | 存储 |
|---------|-----|------|------|
| 开发/测试 | 2核 | 4GB | 20GB |
| 小型生产 | 4核 | 8GB | 50GB |
| 中型生产 | 8核 | 16GB | 100GB |
| 大型生产 | 16核 | 32GB | 200GB+ |

---

## 快速部署

### 一键 Docker 部署

最简单的部署方式，适用于大多数场景：

```bash
# 克隆或复制项目到服务器
cd business/ai-customer-service

# 复制环境配置
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 一键启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## Docker 部署

### 构建镜像

```bash
# 构建后端镜像
docker build -t ai-cs-backend -f Dockerfile.backend .

# 构建前端镜像
docker build -t ai-cs-frontend -f Dockerfile.frontend .
```

### Docker Compose 配置

完整的 `docker-compose.yml` 包含：

- **PostgreSQL** 数据库
- **ChromaDB** 向量数据库
- **Redis** 缓存（可选）
- **Backend API** FastAPI 服务
- **Frontend** Next.js 应用
- **Nginx** 反向代理

---

## Railway 部署

### 准备工作

1. 安装 Railway CLI
2. 登录 Railway 账户
3. 确保项目在 Git 仓库中

### 部署步骤

```bash
# 初始化 Railway 项目
railway init

# 绑定到现有项目或创建新项目
railway link

# 设置环境变量（或通过 Dashboard 设置）
# 在 Railway Dashboard 中添加以下变量：
#   DATABASE_URL
#   REDIS_URL
#   OPENAI_API_KEY
#   SECRET_KEY
#   etc.

# 部署
railway up

# 查看状态
railway status
```

### Railway 变量配置

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
ZHIPU_API_KEY=...
DASHSCOPE_API_KEY=...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=your-secret-key
FEISHU_WEBHOOK_URL=https://...
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
```

---

## 手动部署

适用于需要自定义配置或私有化部署的场景。

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib redis-server nginx

# CentOS/RHEL
sudo yum install -y python3 python3-pip nodejs npm postgresql-server redis nginx
```

### 2. 配置数据库

```bash
# 创建数据库
sudo -u postgres createdb ai_customer_service
sudo -u postgres createuser -P ai_cs_user  # 设置密码

# 授予权限
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_customer_service TO ai_cs_user;"

# 运行迁移
cd business/ai-customer-service
py -m venv venv
venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
alembic upgrade head
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

关键配置项：

```env
# 数据库
DATABASE_URL=postgresql://username:password@localhost:5432/ai_customer_service

# Redis (可选)
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=sk-...

# Claude (可选)
ANTHROPIC_API_KEY=sk-...

# 智谱 AI (可选)
ZHIPU_API_KEY=...

# 阿里云通义 (可选)
DASHSCOPE_API_KEY=...

# 应用密钥
SECRET_KEY=your-random-secret-key-here

# 飞书通知 (可选)
FEISHU_WEBHOOK_URL=https://open.feishu.cn/bot/...

# 邮件服务 (可选)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. 启动后端服务

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
alembic upgrade head

# 启动服务 (开发)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 启动服务 (生产)
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 5. 构建前端

```bash
cd frontend
npm install
npm run build

# 设置环境变量
echo "NEXT_PUBLIC_API_URL=https://api.your-domain.com" > .env.local
echo "NEXT_PUBLIC_APP_NAME=AI 智能客服" >> .env.local

npm start  # 生产模式
```

### 6. 配置 Nginx

```nginx
# /etc/nginx/sites-available/ai-customer-service
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/.next;
        try_files $uri $uri.html $uri/ @frontend;
    }

    location @frontend {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持 (如果使用)
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

启用并重启 Nginx：

```bash
sudo ln -s /etc/nginx/sites-available/ai-customer-service /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

### 7. SSL/TLS 配置

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## 配置说明

### 应用配置

| 环境变量 | 说明 | 必需 | 默认值 |
|---------|------|-----|--------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | ✅ | - |
| `OPENAI_API_KEY` | OpenAI API Key | ✅ | - |
| `SECRET_KEY` | JWT 和加密密钥 | ✅ | - |
| `REDIS_URL` | Redis 连接字符串 | ❌ | - |
| `ANTHROPIC_API_KEY` | Claude API Key | ❌ | - |
| `ZHIPU_API_KEY` | 智谱 AI API Key | ❌ | - |
| `DASHSCOPE_API_KEY` | 通义千问 API Key | ❌ | - |
| `FEISHU_WEBHOOK_URL` | 飞书通知 Webhook | ❌ | - |
| `SMTP_SERVER` | 邮件服务器地址 | ❌ | - |
| `SMTP_PORT` | 邮件服务器端口 | ❌ | 587 |
| `SMTP_USERNAME` | 邮件用户名 | ❌ | - |
| `SMTP_PASSWORD` | 邮件密码/应用专用密码 | ❌ | - |

### 数据库配置

系统支持 PostgreSQL 作为主数据库，使用 SQLAlchemy ORM。

```bash
# 查看数据库连接状态
psql -h localhost -U ai_cs_user -d ai_customer_service

# 查看表结构
\dt
```

---

## 监控与运维

### 健康检查

```bash
# 后端健康检查
curl https://api.your-domain.com/health

# 预期响应
{
  "status": "healthy",
  "services": {
    "database": "up",
    "redis": "up",
    "chromadb": "up"
  },
  "uptime": 12345.67,
  "version": "1.0.0"
}
```

### 日志查看

```bash
# Docker 部署
docker-compose logs -f backend
docker-compose logs -f frontend

# 系统部署
journalctl -u ai-cs-backend -f
tail -f /var/log/nginx/access.log
```

### 性能监控

建议使用以下工具：

- **Prometheus + Grafana** - 指标收集和可视化
- **Sentry** - 错误追踪
- **LogRocket** / **Datadog RUM** - 用户体验监控

---

## 故障排查

### 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 500 错误 | 数据库连接失败 | 检查 `DATABASE_URL` 配置和数据库状态 |
| 502 Bad Gateway | 后端服务未启动 | `systemctl status ai-cs-backend` |
| 无法导入模块 | 依赖缺失 | `pip install -r requirements.txt` |
| 向量检索慢 | ChromaDB 未优化 | 增加向量维度或调整索引参数 |
| 飞书通知失败 | Webhook URL 错误 | 检查飞书机器人配置和 URL |
| 邮件发送失败 | SMTP 配置错误 | 验证 SMTP 服务器、端口、密码 |
| CSS 样式丢失 | 前端未构建 | `npm run build` |
| 无法登录 | Secret Key 不匹配 | 检查 `SECRET_KEY` 配置 |

### 调试步骤

1. **检查服务状态**
```bash
systemctl status ai-cs-backend
docker-compose ps
```

2. **查看日志**
```bash
journalctl -u ai-cs-backend -n 100 --no-pager
docker-compose logs --tail=100 backend
```

3. **测试 API**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.your-domain.com/health
```

4. **检查数据库连接**
```bash
psql $DATABASE_URL -c "SELECT 1"
```

5. **验证环境变量**
```bash
printenv | grep -E "(OPENAI|DATABASE|SECRET)"
```

---

## 备份与恢复

### 数据库备份

```bash
# 自动备份脚本
#!/bin/bash
BACKUP_DIR="/backups/ai-cs"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > $BACKUP_DIR/db_backup_$DATE.sql

# 保留最近7天
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

### 恢复备份

```bash
# 停止应用
docker-compose down

# 恢复数据库
psql $DATABASE_URL < db_backup_20260320.sql

# 重启应用
docker-compose up -d
```

---

## 更新升级

### 版本升级流程

1. 备份数据库和配置文件
2. 拉取最新代码
3. 运行数据库迁移
4. 重启服务
5. 验证功能

```bash
git pull origin main
cd business/ai-customer-service
pip install -r requirements.txt --upgrade
alembic upgrade head
docker-compose restart
```

---

## 安全加固

- [ ] 使用强密码和密钥
- [ ] 定期轮换 API 密钥
- [ ] 启用 HTTPS (SSL/TLS)
- [ ] 配置防火墙规则
- [ ] 禁用不必要的端口
- [ ] 定期更新依赖包
- [ ] 启用数据库连接加密
- [ ] 实施速率限制
- [ ] 配置审计日志

---

## 支持

- 文档: `README.md`, `README_ENHANCED.md`
- API 参考: `api/` 目录
- 问题反馈: GitHub Issues

---

*最后更新: 2026-03-20*
