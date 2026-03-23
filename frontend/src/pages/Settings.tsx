import { useState } from 'react'
import { 
  KeyIcon, 
  BellIcon, 
  DatabaseIcon,
  ServerIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface SettingsState {
  openaiKey: string
  anthropicKey: string
  vectorStore: 'qdrant' | 'pinecone' | 'milvus'
  modelProvider: 'openai' | 'anthropic'
  feishuWebhook: string
  emailNotifications: boolean
  slackNotifications: boolean
}

export default function Settings() {
  const [settings, setSettings] = useState<SettingsState>({
    openaiKey: '',
    anthropicKey: '',
    vectorStore: 'qdrant',
    modelProvider: 'openai',
    feishuWebhook: '',
    emailNotifications: true,
    slackNotifications: false,
  })

  const [activeTab, setActiveTab] = useState<'general' | 'ai' | 'notifications' | 'security'>('general')

  const handleSave = () => {
    // 这里应该调用API保存设置
    toast.success('设置已保存')
  }

  const tabs = [
    { id: 'general', name: '常规', icon: ServerIcon },
    { id: 'ai', name: 'AI配置', icon: KeyIcon },
    { id: 'notifications', name: '通知', icon: BellIcon },
    { id: 'security', name: '安全', icon: ShieldCheckIcon },
  ]

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">设置</h1>
        <p className="mt-1 text-sm text-gray-500">
          配置AI客服系统的各项参数
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* 左侧导航 */}
        <div className="lg:w-64 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* 右侧内容 */}
        <div className="flex-1">
          <div className="card">
            {/* 常规设置 */}
            {activeTab === 'general' && (
              <>
                <div className="card-header">
                  <h3 className="text-base font-semibold leading-6 text-gray-900">
                    常规设置
                  </h3>
                </div>
                <div className="card-body space-y-6">
                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      向量数据库
                    </label>
                    <select
                      value={settings.vectorStore}
                      onChange={(e) => setSettings({ ...settings, vectorStore: e.target.value as any })}
                      className="mt-2 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                    >
                      <option value="qdrant">Qdrant</option>
                      <option value="pinecone">Pinecone</option>
                      <option value="milvus">Milvus</option>
                    </select>
                    <p className="mt-1 text-sm text-gray-500">
                      选择用于存储知识库向量的数据库
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      数据库连接字符串
                    </label>
                    <input
                      type="text"
                      className="input mt-2"
                      placeholder="postgresql://user:pass@localhost:5432/db"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      Redis连接
                    </label>
                    <input
                      type="text"
                      className="input mt-2"
                      placeholder="redis://localhost:6379"
                    />
                  </div>
                </div>
              </>
            )}

            {/* AI配置 */}
            {activeTab === 'ai' && (
              <>
                <div className="card-header">
                  <h3 className="text-base font-semibold leading-6 text-gray-900">
                    AI模型配置
                  </h3>
                </div>
                <div className="card-body space-y-6">
                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      AI模型提供商
                    </label>
                    <select
                      value={settings.modelProvider}
                      onChange={(e) => setSettings({ ...settings, modelProvider: e.target.value as any })}
                      className="mt-2 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                    >
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      OpenAI API Key
                    </label>
                    <input
                      type="password"
                      value={settings.openaiKey}
                      onChange={(e) => setSettings({ ...settings, openaiKey: e.target.value })}
                      className="input mt-2"
                      placeholder="sk-..."
                    />
                    <p className="mt-1 text-sm text-gray-500">
                      用于GPT模型调用，请妥善保管
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      Anthropic API Key
                    </label>
                    <input
                      type="password"
                      value={settings.anthropicKey}
                      onChange={(e) => setSettings({ ...settings, anthropicKey: e.target.value })}
                      className="input mt-2"
                      placeholder="sk-ant-..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      嵌入模型
                    </label>
                    <select className="mt-2 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6">
                      <option>text-embedding-ada-002</option>
                      <option>text-embedding-3-small</option>
                      <option>text-embedding-3-large</option>
                    </select>
                  </div>
                </div>
              </>
            )}

            {/* 通知设置 */}
            {activeTab === 'notifications' && (
              <>
                <div className="card-header">
                  <h3 className="text-base font-semibold leading-6 text-gray-900">
                    通知设置
                  </h3>
                </div>
                <div className="card-body space-y-6">
                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      飞书Webhook地址
                    </label>
                    <input
                      type="text"
                      value={settings.feishuWebhook}
                      onChange={(e) => setSettings({ ...settings, feishuWebhook: e.target.value })}
                      className="input mt-2"
                      placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..."
                    />
                    <p className="mt-1 text-sm text-gray-500">
                      用于接收系统告警和异常通知
                    </p>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">邮件通知</h4>
                      <p className="text-sm text-gray-500">接收每日报告和重要告警</p>
                    </div>
                    <button
                      onClick={() => setSettings({ ...settings, emailNotifications: !settings.emailNotifications })}
                      className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 ${
                        settings.emailNotifications ? 'bg-indigo-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                          settings.emailNotifications ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">Slack通知</h4>
                      <p className="text-sm text-gray-500">推送实时对话提醒</p>
                    </div>
                    <button
                      onClick={() => setSettings({ ...settings, slackNotifications: !settings.slackNotifications })}
                      className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 ${
                        settings.slackNotifications ? 'bg-indigo-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                          settings.slackNotifications ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </>
            )}

            {/* 安全设置 */}
            {activeTab === 'security' && (
              <>
                <div className="card-header">
                  <h3 className="text-base font-semibold leading-6 text-gray-900">
                    安全设置
                  </h3>
                </div>
                <div className="card-body space-y-6">
                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      API访问密钥
                    </label>
                    <div className="mt-2 flex gap-2">
                      <input
                        type="text"
                        readOnly
                        value="aics_live_xxxxxxxxxxxxxxxx"
                        className="input flex-1 bg-gray-50"
                      />
                      <button className="btn-secondary">重新生成</button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium leading-6 text-gray-900">
                      允许的来源域名 (CORS)
                    </label>
                    <textarea
                      rows={3}
                      className="input mt-2"
                      placeholder="https://example.com&#10;https://app.example.com"
                    />
                    <p className="mt-1 text-sm text-gray-500">
                      每行一个域名，使用 * 允许所有来源（不推荐）
                    </p>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">启用访问日志</h4>
                      <p className="text-sm text-gray-500">记录所有API请求详情</p>
                    </div>
                    <button className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent bg-indigo-600 transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2">
                      <span className="pointer-events-none inline-block h-5 w-5 translate-x-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" />
                    </button>
                  </div>
                </div>
              </>
            )}

            {/* 保存按钮 */}
            <div className="card-body border-t border-gray-200">
              <div className="flex justify-end gap-3">
                <button className="btn-secondary">取消</button>
                <button onClick={handleSave} className="btn-primary">
                  保存设置
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
