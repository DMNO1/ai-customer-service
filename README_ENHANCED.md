# 🚀 AI智能客服系统 - 增强版

> 全栈AI客服解决方案，集成RAG检索、多模型支持、飞书推送、支付订阅等功能

## ✨ 主要特性

### 🤖 AI能力
- **RAG向量检索** - 基于ChromaDB的知识库管理
- **多模型支持** - OpenAI、Claude、智谱AI、通义千问一键切换
- **文档解析** - 支持PDF、DOCX、TXT等多种格式
- **网页抓取** - Playwright动态渲染，智能内容提取

### 🔔 通知系统
- **飞书推送** - 系统告警、日报、用户活动实时通知
- **异常监控** - 统一错误处理，支持降级容错
- **健康检查** - 多维度服务状态监控

### 💰 商业化功能
- **支付集成** - 支付宝、微信支付SDK预集成
- **订阅管理** - 灵活的套餐配置和使用限制
- **邮件通知** - 自动化邮件模板（欢迎、账单、提醒）

### 🏗️ 工程化
- **数据库迁移** - Alembic版本控制，保证数据安全
- **API设计** - RESTful接口，完整的异常处理
- **Docker化** - 容器部署支持
- **异步任务** - Celery队列支持（可选）

## 📦 项目结构

```
ai-customer-service/
├── services/              # 核心服务模块
│   ├── vector_store_service.py    # 向量数据库服务
│   ├── document_parser.py         # 文档解析服务
│   ├── web_scraper.py             # 网页抓取服务
│   ├── llm_provider.py            # 多模型LLM管理
│   ├── feishu_notifier.py         # 飞书通知服务 ✨
│   ├── payment_service.py         # 支付服务 ✨
│   └── email_service.py           # 邮件服务 ✨
├── api/                   # REST API
│   └── main.py
├── database/              # 数据库迁移
│   └── alembic/
│       ├── versions/
│       │   └── 001_initial_schema.py
│       ├── env.py
│       └── script.py.mako
├── models.py              # SQLAlchemy数据模型
├── main_service_enhanced.py   # 增强版主服务 ✨
├── main_service.py        # 原始主服务
├── scripts/
│   └── daily_report.py   # 日报生成脚本 ✨
├── tests/                # 测试文件
├── requirements.txt      # Python依赖
├── .env.example          # 环境变量示例
├── start_enhanced.bat    # Windows启动脚本 ✨
└── README_ENHANCED.md    # 本文档
```

## 🚀 快速开始

### 1. 环境准备
- Python 3.8+
- PostgreSQL 12+
- Redis (可选，用于Celery)

### 2. 安装依赖
```bash
cd business/ai-customer-service
py -m pip install -r requirements.txt
```

### 3. 配置环境变量
复制并编辑 `.env` 文件：

```bash
copy .env.example .env
```

必需配置：
```ini
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/ai_customer_service

# AI模型（至少一个）
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ZHIPU_API_KEY=...
DASHSCOPE_API_KEY=...

# 飞书通知（可选）
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_WEBHOOK_URL=...  # 或使用机器人API
FEISHU_DEFAULT_CHAT_ID=...
```

### 4. 数据库初始化
```bash
# 切换到数据库目录
cd database

# 创建迁移脚本（首次）
alembic revision --autogenerate -m "Initial schema"

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

**方式一：使用启动脚本（推荐Windows）**
```bash
start_enhanced.bat
```

**方式二：直接运行Python**
```bash
py main_service_enhanced.py
```

**方式三：使用Flask API**
```bash
set FLASK_APP=api.main.py
py -m flask run --host=0.0.0.0 --port=8000
```

## 🔌 API接口

### 健康检查
```
GET /health
```

### 知识库管理
```
POST   /knowledge/base          # 创建知识库
GET    /knowledge/bases         # 列出所有知识库
POST   /knowledge/{kb_id}/document   # 上传文档
POST   /knowledge/{kb_id}/url        # 添加网页内容
POST   /knowledge/{kb_id}/search    # 向量检索
```

### 对话服务
```
POST /chat    # 生成AI回复
```

### 管理员接口
```
POST /admin/daily-report    # 触发日报生成
GET  /admin/health         # 详细健康状况
```

完整API文档见 `api/` 目录。

## 🔔 飞书通知

增强版支持飞书自动推送：

- **系统告警** - 服务异常、组件故障实时通知
- **日报报表** - 每日运营数据自动推送
- **用户活动** - 重要用户行为提醒

配置步骤：
1. 在[飞书开放平台](https://open.feishu.cn/)创建应用
2. 获取 `APP_ID` 和 `APP_SECRET`
3. 启用机器人权限：`im:message:send_as_app`
4. 将机器人添加到目标群组，获取 `CHAT_ID`
5. 在 `.env` 中配置对应变量

## 💰 支付集成

### 支付宝
```python
from services.payment_service import PaymentService

payment = PaymentService()
order = payment.create_order(
    user_id="user123",
    plan_id="pro",
    amount=299.00,
    payment_method="alipay"
)
# order.payment_url 用于重定向支付
```

### 微信支付
类似配置，需要：
- 商户号 (mch_id)
- APIv3密钥 (apiv3_key)
- 证书序列号 (cert_serial_no)
- 私钥文件路径 (private_key_path)

## 📧 邮件服务

内置邮件模板系统，支持：
- 欢迎邮件
- 账户验证
- 订阅确认
- 发票/收据
- 续费提醒

创建自定义模板：
```html
<!-- email_templates/custom_template.html -->
<h1>Hello {{ name }}!</h1>
<p>Your order {{ order_id }} is confirmed.</p>
```

```python
service.send_template_email(
    to_email="user@example.com",
    template_name="custom_template",
    context={"name": "John", "order_id": "ORD001"}
)
```

## 📊 运行日常任务

### 每日报表（Cron Job）
```bash
py scripts/daily_report.py
```

建议通过Cron定时执行：
- Linux: `0 9 * * * cd /path && py scripts/daily_report.py`
- Windows: 使用任务计划程序
- OpenClaw: 使用 `openclaw cron add` 命令

## 🧪 测试

运行集成测试：
```bash
py test_system.py
```

运行简单验证：
```bash
py simplified_test.py
```

## 🔧 故障排除

### 问题：向量数据库无法初始化
**解决**: 确保ChromaDB依赖已安装，`chroma_db`目录可写

### 问题：LLM调用失败
**解决**: 检查API密钥是否有效，网络可达

### 问题：飞书通知不发送
**解决**: 
- 检查 `FEISHU_*` 环境变量是否完整
- 确认机器人已在目标群组中
- 查看日志中的错误详情

### 问题：数据库迁移失败
**解决**:
```bash
# 确保PostgreSQL正在运行
py -c "import sqlalchemy; print('SQLAlchemy OK')"

# 手动创建数据库
createdb ai_customer_service
```

## 📈 性能优化建议

1. **向量检索** - 使用Milvus/Pinecone替代ChromaDB（生产）
2. **缓存层** - 添加Redis缓存高频查询结果
3. **异步任务** - 使用Celery处理文档解析等耗时任务
4. **CDN** - 静态资源通过CDN分发
5. **监控** - 集成Prometheus + Grafana

## 🛡️ 安全注意事项

- 所有API密钥存储在环境变量，不要提交到版本控制
- 启用HTTPS（生产环境）
- 定期更新依赖以修复安全漏洞
- 使用防火墙限制数据库访问
- 实施API限流和用户认证

## 📝 开发规范

### 代码风格
- 遵循PEP 8
- 使用类型提示
- 编写docstring文档

### 提交信息
使用约定式提交：
- `feat:` 新功能
- `fix:` 问题修复
- `docs:` 文档变更
- `refactor:` 重构
- `test:` 测试相关

## 📄 许可证

本项目专为AI智能客服系统设计，商业使用需遵守相关API服务条款。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**构建时间**: 2026-03-18  
**版本**: Enhanced v1.0  
**维护团队**: AI Customer Service Dev Team