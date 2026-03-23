import { BellIcon } from '@heroicons/react/24/outline'
import { useQuery } from 'react-query'
import { fetchHealthStatus } from '../services/api'

export default function Header() {
  const { data: health } = useQuery('health', fetchHealthStatus, {
    refetchInterval: 30000, // 每30秒刷新一次
  })

  const getStatusColor = () => {
    if (!health) return 'bg-gray-400'
    switch (health.data?.status) {
      case 'healthy':
        return 'bg-green-500'
      case 'degraded':
        return 'bg-yellow-500'
      case 'unhealthy':
        return 'bg-red-500'
      default:
        return 'bg-gray-400'
    }
  }

  return (
    <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6 justify-end">
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* 系统状态指示器 */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">系统状态:</span>
            <div className="flex items-center gap-1.5">
              <div className={`h-2.5 w-2.5 rounded-full ${getStatusColor()}`} />
              <span className="text-sm font-medium text-gray-700">
                {health?.data?.status === 'healthy' ? '正常运行' : 
                 health?.data?.status === 'degraded' ? '部分降级' : 
                 health?.data?.status === 'unhealthy' ? '服务异常' : '检查中...'}
              </span>
            </div>
          </div>

          <div
            className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200"
            aria-hidden="true"
          />

          {/* 通知图标 */}
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500"
          >
            <span className="sr-only">查看通知</span>
            <BellIcon className="h-6 w-6" aria-hidden="true" />
          </button>

          <div
            className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200"
            aria-hidden="true"
          />

          {/* 用户头像 */}
          <div className="flex items-center gap-x-4 lg:gap-x-6">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center">
                <span className="text-indigo-600 font-medium text-sm">A</span>
              </div>
              <span className="hidden lg:block text-sm font-medium text-gray-700">
                管理员
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
