/**
 * AI Customer Service Widget
 * 前端客服浮窗组件。
 */

class AICustomerServiceWidget {
    constructor(config = {}) {
        this.apiUrl = config.apiUrl || 'http://localhost:5000/api';
        this.widgetId = config.widgetId || 'ai-cs-widget';
        this.init();
    }

    init() {
        this.createWidget();
        this.bindEvents();
    }

    createWidget() {
        // 创建浮窗容器
        const widgetContainer = document.createElement('div');
        widgetContainer.id = this.widgetId;
        widgetContainer.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 400px;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            background: white;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;

        // 创建头部
        const header = document.createElement('div');
        header.textContent = 'AI 客服助手';
        header.style.cssText = `
            padding: 12px 16px;
            background: #4F46E5;
            color: white;
            font-weight: 600;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        `;

        // 创建聊天区域
        const chatArea = document.createElement('div');
        chatArea.id = `${this.widgetId}-chat`;
        chatArea.style.cssText = `
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            background: #f9fafb;
        `;

        // 创建输入区域
        const inputArea = document.createElement('div');
        inputArea.style.cssText = `
            display: flex;
            padding: 8px;
            border-top: 1px solid #e5e7eb;
        `;

        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = '请输入您的问题...';
        input.style.cssText = `
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            outline: none;
        `;

        const sendButton = document.createElement('button');
        sendButton.textContent = '发送';
        sendButton.style.cssText = `
            margin-left: 8px;
            padding: 8px 16px;
            background: #4F46E5;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        `;

        inputArea.appendChild(input);
        inputArea.appendChild(sendButton);

        widgetContainer.appendChild(header);
        widgetContainer.appendChild(chatArea);
        widgetContainer.appendChild(inputArea);

        document.body.appendChild(widgetContainer);

        this.input = input;
        this.sendButton = sendButton;
        this.chatArea = chatArea;
    }

    bindEvents() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;

        this.addMessageToChat(message, 'user');
        this.input.value = '';

        try {
            const response = await fetch(`${this.apiUrl}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: message }),
            });

            const data = await response.json();
            if (data.success) {
                this.addMessageToChat(data.answer, 'ai');
            } else {
                this.addMessageToChat('抱歉，我遇到了一些问题。请稍后再试。', 'ai');
            }
        } catch (error) {
            console.error('Error:', error);
            this.addMessageToChat('网络连接出现问题，请检查后重试。', 'ai');
        }
    }

    addMessageToChat(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.style.cssText = `
            margin-bottom: 12px;
            padding: 8px 12px;
            border-radius: 12px;
            max-width: 80%;
            word-wrap: break-word;
        `;

        if (sender === 'user') {
            messageElement.style.cssText += `
                background: #4F46E5;
                color: white;
                margin-left: auto;
            `;
        } else {
            messageElement.style.cssText += `
                background: #e5e7eb;
                color: #1f2937;
            `;
        }

        messageElement.textContent = text;
        this.chatArea.appendChild(messageElement);
        this.chatArea.scrollTop = this.chatArea.scrollHeight;
    }
}

// 自动初始化（如果页面上有配置）
if (window.aiCustomerServiceConfig) {
    new AICustomerServiceWidget(window.aiCustomerServiceConfig);
}

// 导出供手动初始化使用
window.AICustomerServiceWidget = AICustomerServiceWidget;