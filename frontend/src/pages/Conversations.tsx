import { useState } from 'react'
import { 
  ChatBubbleLeftRightIcon,
  UserIcon,
  CheckCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

interface Conversation {
  id: string
  userId: string
  userName: string
  message: string
  response: string
  timestamp: string
  status: 'resolved' | 'pending' | 'escalated'
  satisfaction?: number
}

const mockConversations: Conversation[] = [
  {
    id: '1',
    userId: 'user_001',
    userName: '张三',
    message: '请问如何重置密码？',
    response: '您可以通过以下步骤重置密码：1. 点击登录页面的"忘记密码" 2. 输入您的邮箱地址 3. 查收重置邮件并点击链接',
    timestamp: '2026-03-17 14:30',
    status: 'resolved',
    satisfaction: 5,
  },
  {
    id: '2',
    userId: 'user_002',
    userName: '李四',
    message: '企业版有什么功能？',
    response: '企业版包含以下核心功能：团队协作、高级分析、API访问、专属客服支持、自定义集成等。',
    timestamp: '2026-03-17 14:25',
    status: 'resolved',
    satisfaction: 4,
  },
  {
    id: '3',
    userId: 'user_003',
    userName: '王五',
    message: '我需要退款，怎么操作？',
    response: '已为您转接人工客服处理退款事宜。',
    timestamp: '2026-03-17 14:20',
    status: 'escalated',
  },
  {
    id: '4',
    userId: 'user_004',
    userName: '赵六',
    message: '系统无法登录',
    response: '请检查您的网络连接，或尝试清除浏览器缓存后重新登录。',
    timestamp: '2026-03-17 14:15',
    status: 'pending',
  },
]

export default function Conversations() {
  const [conversations] = useState<Conversation[]>(mockConversations)
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [filter, setFilter] = useState<'all' | 'resolved' | 'pending' | 'escalated'>('all')

  const filteredConversations = conversations.filter(conv =>
    filter === 'all' || conv.status === filter
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'resolved':
        return <span className="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800">已解决</span>
      case 'pending':
        return <span className="inline-flex rounded-full bg-yellow-100 px-2 text-xs font-semibold leading-5 text-yellow-800">待处理</span>
      case 'escalated':
        return <span className="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800">已转人工</span>
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">对话记录</h1>
        <p className="mt-1 text-sm text-gray-500">
          查看和管理用户与AI客服的对话历史
        </p>
      </div>

      {/* 统计和筛选 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex gap-2">
          {(['all', 'resolved', 'pending', 'escalated'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md ${
                filter === status
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              {status === 'all' ? '全部' :
               status === 'resolved' ? '已解决' :
               status === 'pending' ? '待处理' : '已转人工'}
            </button>
          ))}
        </div>
        <button className="btn-secondary flex items-center gap-2">
          <ArrowPathIcon className="h-4 w-4" />
          刷新
        </button>
      </div>

      {/* 对话列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧列表 */}
        <div className="lg:col-span-1 card overflow-hidden">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              对话列表 ({filteredConversations.length})
            </h3>
          </div>
          <div className="overflow-y-auto max-h-[600px]">
            <ul className="divide-y divide-gray-200">
              {filteredConversations.map((conv) => (
                <li
                  key={conv.id}
                  className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                    selectedConversation?.id === conv.id ? 'bg-indigo-50' : ''
                  }`}
                  onClick={() => setSelectedConversation(conv)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <UserIcon className="h-5 w-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-900">{conv.userName}</span>
                    </div>
                    {getStatusBadge(conv.status)}
                  </div>
                  <p className="mt-1 text-sm text-gray-500 truncate">{conv.message}</p>
                  <p className="mt-1 text-xs text-gray-400">{conv.timestamp}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* 右侧详情 */}
        <div className="lg:col-span-2 card">
          {selectedConversation ? (
            <>
              <div className="card-header border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                      <UserIcon className="h-5 w-5 text-indigo-600" />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-gray-900">
                        {selectedConversation.userName}
                      </h3>
                      <p className="text-sm text-gray-500">ID: {selectedConversation.userId}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(selectedConversation.status)}
                    {selectedConversation.satisfaction && (
                      <div className="flex items-center gap-1 text-sm text-gray-600">
                        <CheckCircleIcon className="h-4 w-4 text-green-500" />
                        满意度: {selectedConversation.satisfaction}/5
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="card-body space-y-4">
                {/* 用户消息 */}
                <div className="flex gap-3">
                  <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                    <UserIcon className="h-4 w-4 text-gray-600" />
                  </div>
                  <div className="flex-1">
                    <div className="bg-gray-100 rounded-lg p-3">
                      <p className="text-sm text-gray-800">{selectedConversation.message}</p>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{selectedConversation.timestamp}</p>
                  </div>
                </div>

                {/* AI回复 */}
                <div className="flex gap-3">
                  <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                    <ChatBubbleLeftRightIcon className="h-4 w-4 text-indigo-600" />
                  </div>
                  <div className="flex-1">
                    <div className="bg-indigo-50 rounded-lg p-3">
                      <p className="text-sm text-gray-800">{selectedConversation.response}</p>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">AI助手</p>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-300" />
                <p className="mt-2 text-sm text-gray-500">选择左侧对话查看详情</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
