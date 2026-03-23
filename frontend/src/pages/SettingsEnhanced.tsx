import { useState, useEffect } from 'react'
import { 
  UserIcon, 
  KeyIcon, 
  CreditCardIcon,
  ShieldCheckIcon,
  BellIcon,
  CheckIcon,
  XMarkIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

// 类型定义
interface UserProfile {
  id: string
  name: string
  email: string
  avatar: string
  company: string
  phone: string
}

interface Plan {
  id: string
  name: string
  price: number
  period: 'month' | 'year'
  features: string[]
  limits: {
    conversations: number
    knowledgeBases: number
    teamMembers: number
  }
}

interface PasswordForm {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

// 套餐数据
const PLANS: Plan[] = [
  {
    id: 'free',
    name: '免费版',
    price: 0,
    period: 'month',
    features: [
      '每月 100 次对话',
      '1 个知识库',
      '基础 AI 模型',
      '邮件支持'
    ],
    limits: {
      conversations: 100,
      knowledgeBases: 1,
      teamMembers: 1
    }
  },
  {
    id: 'pro',
    name: '专业版',
    price: 99,
    period: 'month',
    features: [
      '每月 10,000 次对话',
      '10 个知识库',
      '高级 AI 模型 (GPT-4)',
      '优先技术支持',
      '对话质检',
      '数据分析报表'
    ],
    limits: {
      conversations: 10000,
      knowledgeBases: 10,
      teamMembers: 5
    }
  },
  {
    id: 'enterprise',
    name: '企业版',
    price: 299,
    period: 'month',
    features: [
      '无限对话次数',
      '无限知识库',
      '全模型支持 (含 Claude)',
      '7x24 专属支持',
      '高级质检与审计',
      '自定义集成',
      'SLA 保障'
    ],
    limits: {
      conversations: -1,
      knowledgeBases: -1,
      teamMembers: -1
    }
  }
]

export default function SettingsEnhanced() {
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'billing' | 'notifications'>('profile')
  const [currentPlan, setCurrentPlan] = useState<string>('free')
  const [isLoading, setIsLoading] = useState(false)
  
  // 用户资料状态
  const [profile, setProfile] = useState<UserProfile>({
    id: '',
    name: '',
    email: '',
    avatar: '',
    company: '',
    phone: ''
  })
  
  // 密码表单状态
  const [passwordForm, setPasswordForm] = useState<PasswordForm>({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  
  // 通知设置
  const [notifications, setNotifications] = useState({
    email: true,
    browser: false,
    weeklyReport: true,
    newConversation: true,
    systemUpdates: true
  })

  // 加载用户数据
  useEffect(() => {
    // 模拟从API加载
    const loadUserData = async () => {
      try {
        // 这里应该是实际的API调用
        setProfile({
          id: 'usr_123456',
          name: '张三',
          email: 'zhangsan@example.com',
          avatar: '',
          company: '示例科技',
          phone: '138****8888'
        })
      } catch (error) {
        toast.error('加载用户信息失败')
      }
    }
    loadUserData()
  }, [])

  // 保存个人资料
  const handleSaveProfile = async () => {
    setIsLoading(true)
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('个人资料已更新')
    } catch (error) {
      toast.error('保存失败，请重试')
    } finally {
      setIsLoading(false)
    }
  }

  // 修改密码
  const handleChangePassword = async () => {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast.error('两次输入的密码不一致')
      return
    }
    if (passwordForm.newPassword.length < 8) {
      toast.error('新密码长度至少为8位')
      return
    }
    
    setIsLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('密码修改成功')
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
    } catch (error) {
      toast.error('密码修改失败')
    } finally {
      setIsLoading(false)
    }
  }

  // 升级套餐
  const handleUpgrade = async (planId: string) => {
    if (planId === currentPlan) {
      toast.info('您已经是该套餐')
      return
    }
    
    setIsLoading(true)
    try {
      // 模拟跳转到支付页面
      await new Promise(resolve => setTimeout(resolve, 500))
      toast.success(`正在跳转到支付页面...`)
      // 实际应该跳转到支付网关
      setCurrentPlan(planId)
    } catch (error) {
      toast.error('升级失败，请重试')
    } finally {
      setIsLoading(false)
    }
  }

  // 保存通知设置
  const handleSaveNotifications = async () => {
    setIsLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      toast.success('通知设置已保存')
    } catch (error) {
      toast.error('保存失败')
    } finally {
      setIsLoading(false)
    }
  }

  const tabs = [
    { id: 'profile', name: '个人资料', icon: UserIcon },
    { id: 'security', name: '安全设置', icon: ShieldCheckIcon },
    { id: 'billing', name: '套餐升级', icon: CreditCardIcon },
    { id: 'notifications', name: '通知设置', icon: BellIcon },
  ]

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">账户设置</h1>
        <p className="mt-1 text-sm text-gray-500">
          管理您的账户信息、安全设置和套餐订阅
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
        <div className="flex-1 space-y-6">
          {/* 个人资料 */}
          {activeTab === 'profile' && (
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">个人资料</h3>
                <p className="mt-1 text-sm text-gray-500">更新您的个人信息和联系方式</p>
              </div>
              <div className="px-6 py-6 space-y-6">
                {/* 头像 */}
                <div className="flex items-center gap-6">
                  <div className="h-20 w-20 rounded-full bg-indigo-100 flex items-center justify-center">
                    <UserIcon className="h-10 w-10 text-indigo-600" />
                  </div>
                  <div>
                    <button className="btn-secondary text-sm">更换头像</button>
                    <p className="mt-1 text-xs text-gray-500">支持 JPG、PNG 格式，最大 2MB</p>
                  </div>
                </div>

                {/* 表单字段 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">姓名</label>
                    <input
                      type="text"
                      value={profile.name}
                      onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">公司名称</label>
                    <input
                      type="text"
                      value={profile.company}
                      onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">邮箱</label>
                    <input
                      type="email"
                      value={profile.email}
                      disabled
                      className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 shadow-sm sm:text-sm"
                    />
                    <p className="mt-1 text-xs text-gray-500">邮箱不可修改</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">手机号</label>
                    <input
                      type="tel"
                      value={profile.phone}
                      onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={handleSaveProfile}
                    disabled={isLoading}
                    className="btn-primary"
                  >
                    {isLoading ? '保存中...' : '保存更改'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 安全设置 */}
          {activeTab === 'security' && (
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">安全设置</h3>
                <p className="mt-1 text-sm text-gray-500">管理您的密码和账户安全</p>
              </div>
              <div className="px-6 py-6 space-y-6">
                {/* 修改密码 */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-4">修改密码</h4>
                  <div className="space-y-4 max-w-md">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">当前密码</label>
                      <input
                        type="password"
                        value={passwordForm.currentPassword}
                        onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">新密码</label>
                      <input
                        type="password"
                        value={passwordForm.newPassword}
                        onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">确认新密码</label>
                      <input
                        type="password"
                        value={passwordForm.confirmPassword}
                        onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                    <button
                      onClick={handleChangePassword}
                      disabled={isLoading}
                      className="btn-primary"
                    >
                      {isLoading ? '修改中...' : '修改密码'}
                    </button>
                  </div>
                </div>

                <hr className="border-gray-200" />

                {/* API 密钥 */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-4">API 密钥</h4>
                  <div className="bg-gray-50 rounded-md p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">访问密钥</p>
                        <p className="text-xs text-gray-500 mt-1">用于嵌入客服组件到您的网站</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <code className="text-sm bg-gray-200 px-2 py-1 rounded">aics_live_xxxxxxxx</code>
                        <button className="text-indigo-600 hover:text-indigo-800 text-sm">重新生成</button>
                      </div>
                    </div>
                  </div>
                </div>

                <hr className="border-gray-200" />

                {/* 登录历史 */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-4">最近登录</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between py-2">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                          <CheckIcon className="h-4 w-4 text-green-600" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">Windows Chrome</p>
                          <p className="text-xs text-gray-500">IP: 192.168.1.1 · 北京</p>
                        </div>
                      </div>
                      <span className="text-xs text-gray-500">当前会话</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 套餐升级 */}
          {activeTab === 'billing' && (
            <div className="space-y-6">
              {/* 当前套餐 */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">当前套餐</h3>
                </div>
                <div className="px-6 py-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        {PLANS.find(p => p.id === currentPlan)?.name}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        有效期至 2026年12月31日
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-indigo-600">
                        ¥{PLANS.find(p => p.id === currentPlan)?.price}
                        <span className="text-sm text-gray-500 font-normal">/月</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* 套餐选择 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">选择套餐</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {PLANS.map((plan) => (
                    <div
                      key={plan.id}
                      className={`bg-white rounded-lg shadow-sm border-2 ${
                        currentPlan === plan.id
                          ? 'border-indigo-600'
                          : 'border-transparent hover:border-gray-200'
                      } p-6`}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-gray-900">{plan.name}</h4>
                        {currentPlan === plan.id && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                            当前
                          </span>
                        )}
                      </div>
                      <div className="mb-4">
                        <span className="text-3xl font-bold text-gray-900">¥{plan.price}</span>
                        <span className="text-gray-500">/月</span>
                      </div>
                      <ul className="space-y-3 mb-6">
                        {plan.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                            <CheckIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                      <button
                        onClick={() => handleUpgrade(plan.id)}
                        disabled={isLoading || currentPlan === plan.id}
                        className={`w-full py-2 px-4 rounded-md text-sm font-medium ${
                          currentPlan === plan.id
                            ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                            : 'bg-indigo-600 text-white hover:bg-indigo-700'
                        }`}
                      >
                        {currentPlan === plan.id ? '当前套餐' : '升级'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* 支付方式 */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">支付方式</h3>
                </div>
                <div className="px-6 py-6">
                  <div className="flex items-center justify-between py-3 border-b border-gray-100">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 bg-blue-100 rounded flex items-center justify-center">
                        <span className="text-blue-600 font-bold text-xs">支付宝</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">支付宝</p>
                        <p className="text-xs text-gray-500">已绑定</p>
                      </div>
                    </div>
                    <button className="text-sm text-gray-500 hover:text-gray-700">管理</button>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 bg-green-100 rounded flex items-center justify-center">
                        <span className="text-green-600 font-bold text-xs">微信</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">微信支付</p>
                        <p className="text-xs text-gray-500">未绑定</p>
                      </div>
                    </div>
                    <button className="text-sm text-indigo-600 hover:text-indigo-800">绑定</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 通知设置 */}
          {activeTab === 'notifications' && (
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">通知设置</h3>
                <p className="mt-1 text-sm text-gray-500">选择您希望接收的通知类型</p>
              </div>
              <div className="px-6 py-6 space-y-6">
                {[
                  { key: 'email', label: '邮件通知', desc: '接收重要更新和账户信息' },
                  { key: 'browser', label: '浏览器通知', desc: '在浏览器中接收实时提醒' },
                  { key: 'weeklyReport', label: '周报', desc: '每周一接收上周数据汇总' },
                  { key: 'newConversation', label: '新对话提醒', desc: '当有新用户咨询时通知' },
                  { key: 'systemUpdates', label: '系统更新', desc: '产品功能更新和维护通知' },
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{item.label}</h4>
                      <p className="text-sm text-gray-500">{item.desc}</p>
                    </div>
                    <button
                      onClick={() => setNotifications({
                        ...notifications,
                        [item.key]: !notifications[item.key as keyof typeof notifications]
                      })}
                      className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
                        notifications[item.key as keyof typeof notifications]
                          ? 'bg-indigo-600'
                          : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                          notifications[item.key as keyof typeof notifications]
                            ? 'translate-x-5'
                            : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                ))}

                <div className="flex justify-end pt-4">
                  <button
                    onClick={handleSaveNotifications}
                    disabled={isLoading}
                    className="btn-primary"
                  >
                    {isLoading ? '保存中...' : '保存设置'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
