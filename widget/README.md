# AI 客服组件 (Chat Widget)

可嵌入任何网站的智能客服聊天组件，基于 React 开发和原生 JavaScript 版本。

## 功能特性

- 🎨 **高度可定制**: 支持自定义主题色、位置、欢迎语
- 📱 **响应式设计**: 移动端自适应全屏
- ⚡ **实时对话**: 与 AI 客服系统无缝对接
- 🛡️ **安全可靠**: 支持 API Key 认证，防止未授权访问
- 🌐 **即插即用**: 单文件嵌入，无需额外依赖

## 快速开始

### 方式一：React 组件 (适用于 Next.js/React 项目)

```tsx
import { ChatWidget } from './widget/ChatWidget';

function App() {
  return (
    <div>
      {/* 你的应用内容 */}
      <ChatWidget
        apiEndpoint="https://api.your-domain.com"
        apiKey="your-api-key"
        agentId="your-agent-id"
        theme={{
          primaryColor: '#3B82F6',
          position: 'right',
          welcomeMessage: '你好！有什么可以帮助您的吗？'
        }}
      />
    </div>
  );
}
```

### 方式二：原生 JavaScript (适用于任何网站)

在你的 HTML 页面中添加：

```html
<script src="https://your-domain.com/widget/embed.js"
        data-api-endpoint="https://api.your-domain.com"
        data-api-key="your-api-key"
        data-agent-id="your-agent-id"
        data-primary-color="#3B82F6"
        data-position="right"
        data-welcome-message="你好！有什么可以帮助您的吗？">
</script>
```

## 配置参数

| 参数 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| `api-endpoint` | API 服务器地址 | ✅ | - |
| `api-key` | API 认证密钥 | ✅ | - |
| `agent-id` | 客服 Agent ID | ✅ | - |
| `primary-color` | 主题颜色 (HEX) | ❌ | `#3B82F6` |
| `position` | 悬浮按钮位置 (`left`/`right`) | ❌ | `right` |
| `welcome-message` | 欢迎语 | ❌ | `你好！有什么可以帮助您的吗？` |

## API 接口要求

后端需要实现以下接口：

### POST /chat

**请求体**:
```json
{
  "agent_id": "string",
  "message": "用户问题",
  "conversation_history": [
    { "role": "user", "content": "历史消息1" },
    { "role": "assistant", "content": "历史回复1" }
  ]
}
```

**响应体**:
```json
{
  "response": "AI 回复内容"
}
```

## 文件结构

```
widget/
├── ChatWidget.tsx    # React 组件
├── embed.js         # 原生 JS 嵌入脚本
├── index.ts         # ES6 导出入口
└── README.md        # 使用文档
```

## 开发

### 本地测试

1. 启动后端 API 服务
2. 修改 `embed.js` 中的 `config.apiEndpoint` 为本地地址
3. 在浏览器中打开测试页面

### 构建 React 组件

```bash
# 编译 TypeScript
tsc

# 或使用 Next.js 构建
next build
```

## 样式定制

可以通过自定义 CSS 覆盖样式：

```css
.ai-chat-window {
  border-radius: 20px !important;
}

.ai-chat-message.user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}
```

## 安全建议

1. 在生产环境中使用 HTTPS
2. 限制 API Key 的权限范围
3. 实现消息频率限制
4. 添加内容审核机制
5. 定期轮换 API 密钥

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 组件不显示 | 检查控制台是否有 JavaScript 错误 |
| 无法发送消息 | 验证 API 端点是否可访问 |
| 样式错乱 | 检查是否有 CSS 冲突 |
| 跨域错误 | 后端需要配置 CORS 允许来源 |

## 更新日志

### v1.0.0 (2026-03-20)
- ✨ 首次发布
- ✅ 支持 React 和原生 JS 两种方式
- ✅ 移动端适配
- ✅ 多种配置选项

## License

MIT License - 可免费用于商业项目
