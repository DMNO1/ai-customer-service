/**
 * AI Customer Service Chat Widget - Embed Script
 * 
 * Usage:
 * <script src="https://your-domain.com/widget/embed.js" 
 *         data-api-endpoint="https://api.your-domain.com"
 *         data-api-key="your-api-key"
 *         data-agent-id="your-agent-id"
 *         data-primary-color="#3B82F6"
 *         data-position="right"
 *         data-welcome-message="你好！有什么可以帮助您的吗？">
 * </script>
 */

(function() {
  'use strict';

  // Get configuration from script tag
  const script = document.currentScript;
  const config = {
    apiEndpoint: script.getAttribute('data-api-endpoint') || '',
    apiKey: script.getAttribute('data-api-key') || '',
    agentId: script.getAttribute('data-agent-id') || '',
    primaryColor: script.getAttribute('data-primary-color') || '#3B82F6',
    position: script.getAttribute('data-position') || 'right',
    welcomeMessage: script.getAttribute('data-welcome-message') || '你好！有什么可以帮助您的吗？'
  };

  // Validate required config
  if (!config.apiEndpoint || !config.apiKey || !config.agentId) {
    console.error('AI Chat Widget: Missing required configuration (api-endpoint, api-key, agent-id)');
    return;
  }

  // Create widget container
  const container = document.createElement('div');
  container.id = 'ai-chat-widget-container';
  document.body.appendChild(container);

  // Widget state
  let isOpen = false;
  let messages = [];
  let isLoading = false;

  // Create styles
  const styles = document.createElement('style');
  styles.textContent = `
    #ai-chat-widget-container {
      position: fixed;
      bottom: 20px;
      ${config.position}: 20px;
      z-index: 9999;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .ai-chat-window {
      width: 380px;
      height: 600px;
      background: white;
      border-radius: 16px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
      display: none;
      flex-direction: column;
      overflow: hidden;
      margin-bottom: 16px;
      animation: slideIn 0.3s ease-out;
    }

    .ai-chat-window.open {
      display: flex;
    }

    .ai-chat-header {
      background: ${config.primaryColor};
      padding: 16px 20px;
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .ai-chat-status {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .ai-chat-status-dot {
      width: 10px;
      height: 10px;
      background: #10B981;
      border-radius: 50%;
    }

    .ai-chat-title {
      font-weight: 600;
      font-size: 16px;
    }

    .ai-chat-close {
      background: none;
      border: none;
      color: white;
      cursor: pointer;
      font-size: 20px;
      padding: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .ai-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      background: #F9FAFB;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .ai-chat-message {
      max-width: 80%;
      padding: 12px 16px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.5;
      word-wrap: break-word;
    }

    .ai-chat-message.user {
      align-self: flex-end;
      background: ${config.primaryColor};
      color: white;
      border-radius: 16px 16px 4px 16px;
    }

    .ai-chat-message.assistant {
      align-self: flex-start;
      background: white;
      color: #1F2937;
      border-radius: 16px 16px 16px 4px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    .ai-chat-loading {
      align-self: flex-start;
      padding: 12px 16px;
      background: white;
      border-radius: 16px 16px 16px 4px;
      display: flex;
      gap: 4px;
    }

    .ai-chat-loading-dot {
      width: 8px;
      height: 8px;
      background: #D1D5DB;
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;
    }

    .ai-chat-loading-dot:nth-child(1) { animation-delay: 0s; }
    .ai-chat-loading-dot:nth-child(2) { animation-delay: 0.16s; }
    .ai-chat-loading-dot:nth-child(3) { animation-delay: 0.32s; }

    .ai-chat-input-container {
      padding: 16px 20px;
      background: white;
      border-top: 1px solid #E5E7EB;
      display: flex;
      gap: 12px;
    }

    .ai-chat-input {
      flex: 1;
      padding: 10px 16px;
      border: 1px solid #E5E7EB;
      border-radius: 24px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }

    .ai-chat-input:focus {
      border-color: ${config.primaryColor};
    }

    .ai-chat-send {
      padding: 10px 20px;
      background: ${config.primaryColor};
      color: white;
      border: none;
      border-radius: 24px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: opacity 0.2s;
    }

    .ai-chat-send:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .ai-chat-toggle {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: ${config.primaryColor};
      color: white;
      border: none;
      cursor: pointer;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .ai-chat-toggle:hover {
      transform: scale(1.05);
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15);
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }

    @media (max-width: 480px) {
      .ai-chat-window {
        width: calc(100vw - 40px);
        height: calc(100vh - 100px);
        position: fixed;
        bottom: 90px;
        ${config.position}: 20px;
      }
    }
  `;
  document.head.appendChild(styles);

  // Create widget HTML
  function createWidget() {
    container.innerHTML = `
      <div class="ai-chat-window" id="ai-chat-window">
        <div class="ai-chat-header">
          <div class="ai-chat-status">
            <div class="ai-chat-status-dot"></div>
            <span class="ai-chat-title">AI 客服</span>
          </div>
          <button class="ai-chat-close" id="ai-chat-close">×</button>
        </div>
        <div class="ai-chat-messages" id="ai-chat-messages"></div>
        <div class="ai-chat-input-container">
          <input type="text" class="ai-chat-input" id="ai-chat-input" placeholder="输入您的问题...">
          <button class="ai-chat-send" id="ai-chat-send">发送</button>
        </div>
      </div>
      <button class="ai-chat-toggle" id="ai-chat-toggle">💬</button>
    `;

    // Add event listeners
    document.getElementById('ai-chat-toggle').addEventListener('click', toggleChat);
    document.getElementById('ai-chat-close').addEventListener('click', toggleChat);
    document.getElementById('ai-chat-send').addEventListener('click', sendMessage);
    document.getElementById('ai-chat-input').addEventListener('keypress', function(e) {
      if (e.key === 'Enter') sendMessage();
    });
  }

  // Toggle chat window
  function toggleChat() {
    isOpen = !isOpen;
    const window = document.getElementById('ai-chat-window');
    const toggle = document.getElementById('ai-chat-toggle');
    
    if (isOpen) {
      window.classList.add('open');
      toggle.textContent = '✕';
      if (messages.length === 0) {
        addMessage('assistant', config.welcomeMessage);
      }
    } else {
      window.classList.remove('open');
      toggle.textContent = '💬';
    }
  }

  // Add message to chat
  function addMessage(role, content) {
    const message = { id: Date.now().toString(), role, content, timestamp: new Date() };
    messages.push(message);
    renderMessages();
  }

  // Render all messages
  function renderMessages() {
    const messagesContainer = document.getElementById('ai-chat-messages');
    if (!messagesContainer) return;

    messagesContainer.innerHTML = messages.map(msg => `
      <div class="ai-chat-message ${msg.role}">
        ${escapeHtml(msg.content)}
      </div>
    `).join('');

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Send message
  async function sendMessage() {
    const input = document.getElementById('ai-chat-input');
    const content = input.value.trim();
    
    if (!content || isLoading) return;

    input.value = '';
    addMessage('user', content);
    isLoading = true;
    renderLoading();

    try {
      const response = await fetch(`${config.apiEndpoint}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${config.apiKey}`
        },
        body: JSON.stringify({
          agent_id: config.agentId,
          message: content,
          conversation_history: messages.filter(m => m.role !== 'system').map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      addMessage('assistant', data.response || '抱歉，我暂时无法回答您的问题。');
    } catch (error) {
      console.error('Chat error:', error);
      addMessage('assistant', '抱歉，服务暂时不可用，请稍后再试。');
    } finally {
      isLoading = false;
      renderMessages();
    }
  }

  // Render loading indicator
  function renderLoading() {
    const messagesContainer = document.getElementById('ai-chat-messages');
    if (!messagesContainer) return;

    const loadingHtml = `
      <div class="ai-chat-loading">
        <div class="ai-chat-loading-dot"></div>
        <div class="ai-chat-loading-dot"></div>
        <div class="ai-chat-loading-dot"></div>
      </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', loadingHtml);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Initialize widget
  createWidget();
})();
