import { useQuery } from 'react-query'
import {
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  UsersIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'
import { fetchHealthStatus } from '../services/api'

const stats = [
  { name: '今日对话', stat: '1,284', icon: ChatBubbleLeftRightIcon, change: '+12%', changeType: 'increase' },
  { name: '知识库文档', stat: '3,456', icon: DocumentTextIcon, change: '+8%', changeType: 'increase' },
  { name: '活跃用户', stat: '892', icon: UsersIcon, change: '+23%', changeType: 'increase' },
  { name: '解决率', stat: '94.2%', icon: CheckCircleIcon, change: '+2.1%', changeType: 'increase' },
]

const recentActivity = [
  { id: 1, type: '对话', description: '用户询问产品退款政策', time: '2分钟前', status: '已解决' },
  { id: 2, type: '文档', description: '新增帮助文档：账户设置指南', time: '15分钟前', status: '已发布' },
  { id: 3, type: '对话', description: '用户咨询企业版定价', time: '32分钟前', status: '已转人工' },
  { id: 4, type: '系统', description: '知识库自动更新完成', time: '1小时前', status: '成功' },
  { id: 5, type: '对话', description: '用户反馈功能建议', time: '2小时前', status: '已记录' },
]

export default function Dashboard() {
  const { data: health, isLoading: healthLoading } = useQuery('health', fetchHealthStatus, {
    refetchInterval: 30000,
  })

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">概览</h1>
        <p className="mt-1 text-sm text-gray-500">
          实时监控AI客服系统的运行状态和关键指标
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.name} className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <item.icon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="truncate text-sm font-medium text-gray-500">
                      {item.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">
                        {item.stat}
                      </div>
                      <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                        item.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {item.change}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 系统健康状态 */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              系统健康状态
            </h3>
          </div>
          <div className="card-body">
            {healthLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="text-gray-500">加载中...</div>
              </div>
            ) : health?.data?.checks ? (
              <div className="space-y-3">
                {health.data.checks.map((check: any) => (
                  <div key={check.component} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`h-2.5 w-2.5 rounded-full ${
                        check.status === 'healthy' ? 'bg-green-500' :
                        check.status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
                      }`} />
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {check.component.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xs text-gray-500">
                        {check.response_time_ms}ms
                      </span>
                      <span className={`text-xs font-medium ${
                        check.status === 'healthy' ? 'text-green-600' :
                        check.status === 'degraded' ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {check.status === 'healthy' ? '正常' :
                         check.status === 'degraded' ? '降级' : '异常'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-500 text-center py-8">
                无法获取健康状态
              </div>
            )}
          </div>
        </div>

        {/* 最近活动 */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              最近活动
            </h3>
          </div>
          <div className="card-body">
            <div className="flow-root">
              <ul role="list" className="-mb-8">
                {recentActivity.map((activity, activityIdx) => (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      {activityIdx !== recentActivity.length - 1 ? (
                        <span
                          className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                            activity.type === '对话' ? 'bg-blue-500' :
                            activity.type === '文档' ? 'bg-green-500' :
                            activity.type === '系统' ? 'bg-purple-500' : 'bg-gray-500'
                          }`}>
                            <span className="text-white text-xs font-medium">
                              {activity.type[0]}
                            </span>
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-gray-600">
                              {activity.description}
                            </p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-gray-500">
                            <time>{activity.time}</time>
                            <span className="ml-2 text-xs font-medium text-green-600">
                              {activity.status}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
