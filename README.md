# AI 智能客服系统

> 为中小电商和本地服务企业打造的 SaaS 客服解决方案

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## ✨ 核心功能

- 🧠 **RAG 向量检索** - 基于 ChromaDB/Milvus 的语义搜索
- 📄 **多格式文档解析** - PDF, DOCX, PPTX, TXT, MD 自动提取
- 🌐 **网页抓取** - JS 渲染页面抓取，一键添加到知识库
- 🤖 **多模型支持** - OpenAI, Claude, 智谱, 通义千问灵活切换
- 💬 **客服 Widget** - 轻量级 React 组件，支持 iframe 嵌入
- 📊 **实时统计** - 对话数据、用户活跃度分析
- 💰 **支付订阅** - 支付宝/微信支付 + 自动开票
- 🔔 **飞书推送** - 实时通知、日报推送

## 🏗️ 技术架构

### 后端
- **框架**: FastAPI 0.110+ (异步高性能)
- **数据库**: PostgreSQL (主数据) + Redis (缓存/队列)
- **向量库**: ChromaDB (开发) / Milvus (生产)
- **任务队列**: Celery + Redis
- **LLM**: LangChain + 多供应商抽象层
- **ORM**: SQLAlchemy 2.0 + Alembic 迁移

### 前端
- **框架**: Next.js 14 + React 18
- **语言**: TypeScript 5
- **样式**: Tailwind CSS
- **UI库**: shadcn/ui + Radix UI
- **图表**: Recharts

### Widget
- React 18 独立组件包
- WebSocket 实时通信
- 支持自定义主题色

## 🚀 快速开始

### 前置要求
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+

### 1. 克隆项目
```bash
cd C:\Users\91780\.openclaw\workspace\business\ai-customer-service
```

### 2. 环境配置
```bash
# 复制后端环境变量配置
cp backend/.env.example backend/.env

# 编辑 .env 文件，填入你的 API 密钥
# - OPENAI_API_KEY (可选)
# - ANTHROPIC_API_KEY (可选)
# - FEISHU_WEBHOOK_URL (可选，通知用)
# - 数据库、Redis、支付配置
```

### 3. Docker 一键启动（推荐）
```bash
docker-compose up -d
```

### 4. 访问服务
- 前端管理后台: http://localhost:3000
- 后端 API 文档: http://localhost:8000/docs
- 向量数据库: http://localhost:8000 (Chroma 控制台)

### 5. 手动启动（开发模式）

**后端:**
```bash
cd backend
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py init_db.py  # 创建数据表
py run_api.py   # 启动 API 服务 (http://localhost:8000)
py run_worker.py  # 启动 Celery worker
```

**前端:**
```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## 📦 项目结构
```
business/ai-customer-service/
├── backend/
│   ├── app/
│   │   ├── api/           # API 路由 (knowledge, chat, payment, settings)
│   │   ├── core/          # 核心模块 (config, exceptions, feishu, db)
│   │   ├── models/        # SQLAlchemy 数据模型
│   │   ├── services/      # 业务服务 (vector_store, llm, parser, scraper, chat)
│   │   └── schemas/       # Pydantic 数据验证模型
│   ├── alembic/           # 数据库迁移
│   ├── init_db.py         # 初始化脚本
│   ├── run_api.py         # 启动脚本
│   └── requirements.txt   # Python 依赖
│
├── frontend/               # Next.js 前端
│   ├── src/
│   │   ├── app/           # 页面路由
│   │   ├── components/    # React 组件
│   │   ├── lib/           # 工具函数
│   │   └── styles/        # 样式文件
│   ├── package.json
│   └── next.config.js
│
├── widget/                 # React Widget 组件包
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── index.ts
│   └── package.json
│
├── scripts/                # 定时任务脚本
│   ├── daily_report.py    # 日报生成
│   ├── billing_settlement.py  # 计费结算
│   └── data_cleanup.py    # 数据清理
│
├── docker-compose.yml      # 容器编排
└── README.md
```

## 🔧 核心 API 文档

### 知识库管理
- `POST /api/v1/knowledge/bases` - 创建知识库
- `POST /api/v1/knowledge/bases/{id}/upload` - 上传文档
- `POST /api/v1/knowledge/bases/{id}/add-url` - 添加网页
- `POST /api/v1/knowledge/bases/{id}/search` - 向量检索

### 智能对话
- `POST /api/v1/chat/completions` - 对话问答
- `POST /api/v1/chat/completions/stream` - 流式对话

### 支付订阅
- `POST /api/v1/payment/create-order` - 创建订单
- `POST /api/v1/payment/alipay/notify` - 支付宝回调
- `POST /api/v1/payment/wechat/notify` - 微信支付回调

### 系统设置
- `GET /api/v1/settings/models` - 获取模型配置
- `PUT /api/v1/settings/models` - 更新模型配置
- `GET /api/v1/settings/system` - 系统信息

完整 API 详见: http://localhost:8000/docs

## 📋 开发指南

### 添加新的 LLM 提供者

1. 在 `app/services/llm_service.py` 中创建新的 Provider 类，继承 `LLMProvider`
2. 在 `_providers` 字典中注册
3. 更新 `requirements.txt` 安装对应 SDK

### 扩展向量数据库

当前支持 ChromaDB 和 Milvus。如需添加其他向量库：
1. 在 `VectorStoreService._init_client()` 中添加初始化逻辑
2. 实现 `add_documents`, `similarity_search`, `delete_by_knowledge_base`

### 配置飞书机器人

1. 在飞书创建机器人，获取 Webhook URL
2. 填入 `.env` 文件: `FEISHU_WEBHOOK_URL=xxx`
3. 系统自动推送各类通知

### 添加定时任务

编辑 `crontab` 或系统定时器：
```bash
# 每日 9:00 发送日报
0 9 * * * cd /path/to/project && py scripts/daily_report.py

# 每月 1 号 00:00 计费结算
0 0 1 * * cd /path/to/project && py scripts/billing_settlement.py

# 每周日 2:00 数据清理
0 2 * * 0 cd /path/to/project && py scripts/data_cleanup.py
```

## 🧪 测试

```bash
cd backend
pytest tests/  # TODO: 完善测试用例
```

## 🚢 部署

### Railway / Vercel

**后端 (Railway):**
1. 连接 GitHub 仓库
2. 设置环境变量 (复制 .env.example)
3. 构建命令: `pip install -r requirements.txt`
4. 启动命令: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**前端 (Vercel):**
1. 导入 frontend 目录
2. 环境变量: `NEXT_PUBLIC_API_URL=https://your-backend.com`
3. 自动部署

### 阿里云 ECS

```bash
# 拉取代码
git clone <your-repo>
cd ai-customer-service

# 使用 Docker
docker-compose -f docker-compose.yml up -d

# 或手动安装
cd backend
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py init_db.py
py run_api.py
```

## 📊 Widget 嵌入

```html
<!-- 在你的网站中添加客服 Widget -->
<div id="customer-service-widget"></div>
<script src="https://your-cdn.com/widget/widget.js"></script>
<script>
  window.CustomerServiceWidget.init({
    apiUrl: 'https://your-backend.com/api/v1',
    knowledgeBaseId: 'your-kb-id',
    themeColor: '#3B82F6',
    title: '在线客服',
    placeholder: '请输入您的问题...'
  });
</script>
```

## 🐛 故障排查

- **API 无法调用**: 检查后端是否启动，端口 8000 是否开放
- **LLM 报错**: 检查 API 密钥配置，额度是否充足
- **向量检索无结果**: 确认已上传文档，向量库运行正常
- **飞书推送失败**: 检查 Webhook URL 是否正确

详细文档请查看 `TROUBLESHOOTING.md`

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**技术负责人**: 周田田  
**交付日期**: 2026-03-18  
**版本**: 1.0.0
