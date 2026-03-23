import { useQuery } from 'react-query'
import { ArrowPathIcon, CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { fetchHealthStatus } from '../services/api'

export default function HealthStatus() {
  const { data: health, isLoading, refetch } = useQuery('health', fetchHealthStatus, {
    refetchInterval: 10000, // 每10秒刷新
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />
      case 'degraded':
        return <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />
      case 'unhealthy':
        return <XCircleIcon className="h-6 w-6 text-red-500" />
      default:
        return <XCircleIcon className="h-6 w-6 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <span className="status-healthy">正常</span>
      case 'degraded':
        return <span className="status-degraded">降级</span>
      case 'unhealthy':
        return <span className="status-unhealthy">异常</span>
      default:
        return <span className="status-badge bg-gray-100 text-gray-800">未知</span>
    }
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">健康状态</h1>
          <p className="mt-1 text-sm text-gray-500">
            实时监控各服务组件的运行状态
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="btn-secondary flex items-center gap-2"
        >
          <ArrowPathIcon className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          刷新
        </button>
      </div>

      {/* 整体状态卡片 */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {health?.data?.status && getStatusIcon(health.data.status)}
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  整体状态: {health?.data?.status === 'healthy' ? '正常运行' : 
                           health?.data?.status === 'degraded' ? '部分降级' : 
                           health?.data?.status === 'unhealthy' ? '服务异常' : '检查中...'}
                </h3>
                <p className="text-sm text-gray-500">
                  最后检查: {health?.data?.timestamp ? new Date(health.data.timestamp).toLocaleString('zh-CN') : '-'}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-semibold text-gray-900">
                {health?.data?.checks?.filter((c: any) => c.status === 'healthy').length || 0}
                <span className="text-gray-400 text-lg">/{health?.data?.checks?.length || 0}</span>
              </div>
              <p className="text-sm text-gray-500">组件正常运行</p>
            </div>
          </div>
        </div>
      </div>

      {/* 组件详细状态 */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-base font-semibold leading-6 text-gray-900">
            组件详细状态
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                  组件
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  状态
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  响应时间
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  消息
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  最后检查
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-gray-500">
                    加载中...
                  </td>
                </tr>
              ) : health?.data?.checks?.length > 0 ? (
                health.data.checks.map((check: any) => (
                  <tr key={check.component}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 capitalize">
                      {check.component.replace('_', ' ')}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm">
                      {getStatusBadge(check.status)}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {check.response_time_ms}ms
                    </td>
                    <td className="px-3 py-4 text-sm text-gray-500 max-w-md truncate">
                      {check.message}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {new Date(check.last_checked).toLocaleString('zh-CN')}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-gray-500">
                    暂无健康检查数据
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 响应时间图表 */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-base font-semibold leading-6 text-gray-900">
            响应时间概览
          </h3>
        </div>
        <div className="card-body">
          {health?.data?.checks ? (
            <div className="space-y-4">
              {health.data.checks.map((check: any) => (
                <div key={check.component}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {check.component.replace('_', ' ')}
                    </span>
                    <span className="text-sm text-gray-500">{check.response_time_ms}ms</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        check.response_time_ms < 100 ? 'bg-green-500' :
                        check.response_time_ms < 500 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min((check.response_time_ms / 1000) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              暂无数据
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
