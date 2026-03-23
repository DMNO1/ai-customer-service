import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  MessageCircle, 
  X, 
  Send, 
  Minimize2, 
  Maximize2,
  Bot,
  User,
  Loader2,
  Sparkles
} from 'lucide-react';

// 类型定义
interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
}

interface WidgetConfig {
  apiKey: string;
  apiUrl: string;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  primaryColor?: string;
  welcomeMessage?: string;
  botName?: string;
  botAvatar?: string;
  showPoweredBy?: boolean;
}

interface ChatWidgetProps {
  config: WidgetConfig;
}

// 默认配置
const defaultConfig: Partial<WidgetConfig> = {
  position: 'bottom-right',
  primaryColor: '#4F46E5',
  welcomeMessage: '您好！我是AI客服助手，有什么可以帮助您的吗？',
  botName: 'AI助手',
  showPoweredBy: true,
};

// 生成唯一ID
const generateId = () => Math.random().toString(36).substring(2, 9);

export const ChatWidget: React.FC<ChatWidgetProps> = ({ config: userConfig }) => {
  const config = { ...defaultConfig, ...userConfig };
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 初始化欢迎消息
  useEffect(() => {
    if (messages.length === 0 && config.welcomeMessage) {
      setMessages([
        {
          id: generateId(),
          content: config.welcomeMessage,
          role: 'assistant',
          timestamp: new Date(),
        },
      ]);
    }
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 打开时聚焦输入框
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, isMinimized]);

  // 位置样式
  const positionStyles = {
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
  };

  // 发送消息
  const sendMessage = useCallback(async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      content: trimmedInput,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // 添加加载中的消息
    const loadingMessage: Message = {
      id: generateId(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isLoading: true,
    };
    setMessages((prev) => [...prev, loadingMessage]);

    try {
      const response = await fetch(`${config.apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${config.apiKey}`,
        },
        body: JSON.stringify({
          message: trimmedInput,
          session_id: 'widget_session',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 替换加载消息为实际回复
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMessage.id
            ? {
                id: generateId(),
                content: data.response || data.answer || '抱歉，我暂时无法回答这个问题。',
                role: 'assistant',
                timestamp: new Date(),
              }
            : msg
        )
      );
    } catch (error) {
      console.error('Chat error:', error);
      setIsConnected(false);
      
      // 替换加载消息为错误提示
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMessage.id
            ? {
                id: generateId(),
                content: '抱歉，服务暂时不可用，请稍后再试。',
                role: 'assistant',
                timestamp: new Date(),
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, isLoading, config.apiUrl, config.apiKey]);

  // 处理键盘事件
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 渲染消息气泡
  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user';
    
    return (
      <div
        key={message.id}
        className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
      >
        {!isUser && (
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center mr-2 flex-shrink-0"
            style={{ backgroundColor: `${config.primaryColor}20` }}
          >
            <Bot size={16} style={{ color: config.primaryColor }} />
          </div>
        )}
        
        <div
          className={`max-w-[70%] px-4 py-2 rounded-2xl ${
            isUser
              ? 'text-white rounded-br-none'
              : 'bg-gray-100 text-gray-800 rounded-bl-none'
          }`}
          style={isUser ? { backgroundColor: config.primaryColor } : {}}
        >
          {message.isLoading ? (
            <div className="flex items-center gap-2">
              <Loader2 size={16} className="animate-spin" />
              <span className="text-sm">思考中...</span>
            </div>
          ) : (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          )}
          <span className="text-xs opacity-50 mt-1 block">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {isUser && (
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center ml-2 flex-shrink-0">
            <User size={16} className="text-gray-600" />
          </div>
        )}
      </div>
    );
  };

  // 如果最小化，只显示悬浮按钮
  if (isMinimized) {
    return (
      <div className={`fixed ${positionStyles[config.position!]} z-50`}>
        <button
          onClick={() => setIsMinimized(false)}
          className="w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-110"
          style={{ backgroundColor: config.primaryColor }}
        >
          <Maximize2 size={24} className="text-white" />
        </button>
      </div>
    );
  }

  return (
    <div className={`fixed ${positionStyles[config.position!]} z-50`}>
      {!isOpen ? (
        // 悬浮按钮
        <button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-110 group"
          style={{ backgroundColor: config.primaryColor }}
        >
          <MessageCircle size={28} className="text-white" />
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full animate-pulse" />
        </button>
      ) : (
        // 聊天窗口
        <div className="w-96 h-[500px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-gray-200">
          {/* 头部 */}
          <div
            className="px-4 py-3 flex items-center justify-between"
            style={{ backgroundColor: config.primaryColor }}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <Sparkles size={20} className="text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold">{config.botName}</h3>
                <div className="flex items-center gap-1">
                  <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
                  <span className="text-white/80 text-xs">
                    {isConnected ? '在线' : '离线'}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setIsMinimized(true)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <Minimize2 size={18} className="text-white" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X size={18} className="text-white" />
              </button>
            </div>
          </div>

          {/* 消息区域 */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <Bot size={48} className="mb-4 opacity-50" />
                <p>开始对话吧</p>
              </div>
            ) : (
              <>
                {messages.map(renderMessage)}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* 输入区域 */}
          <div className="p-4 bg-white border-t border-gray-200">
            <div className="flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入您的问题..."
                disabled={isLoading}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
              />
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ 
                  backgroundColor: inputValue.trim() && !isLoading ? config.primaryColor : '#E5E7EB'
                }}
              >
                <Send size={20} className={inputValue.trim() && !isLoading ? 'text-white' : 'text-gray-400'} />
              </button>
            </div>
            
            {config.showPoweredBy && (
              <div className="text-center mt-2">
                <span className="text-xs text-gray-400">
                  Powered by AI Customer Service
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// 独立初始化函数（用于非React环境）
export const initWidget = (config: WidgetConfig) => {
  const container = document.createElement('div');
  container.id = 'ai-chat-widget-root';
  document.body.appendChild(container);

  // 注入样式
  const style = document.createElement('style');
  style.textContent = `
    #ai-chat-widget-root {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
  `;
  document.head.appendChild(style);

  // 这里应该使用ReactDOM.render，但在纯JS环境中需要打包后的版本
  console.log('Widget initialized with config:', config);
};

export default ChatWidget;
