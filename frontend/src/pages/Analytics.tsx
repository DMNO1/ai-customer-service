import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

const conversationData = [
  { name: '周一', conversations: 120, resolved: 110 },
  { name: '周二', conversations: 145, resolved: 135 },
  { name: '周三', conversations: 138, resolved: 128 },
  { name: '周四', conversations: 162, resolved: 150 },
  { name: '周五', conversations: 185, resolved: 172 },
  { name: '周六', conversations: 98, resolved: 92 },
  { name: '周日', conversations: 87, resolved: 82 },
]

const responseTimeData = [
  { time: '00:00', avgTime: 1.2 },
  { time: '04:00', avgTime: 0.8 },
  { time: '08:00', avgTime: 2.1 },
  { time: '12:00', avgTime: 3.5 },
  { time: '16:00', avgTime: 2.8 },
  { time: '20:00', avgTime: 1.9 },
  { time: '23:59', avgTime: 1.1 },
]

const topicData = [
  { name: '账户问题', value: 35, color: '#4F46E5' },
  { name: '产品咨询', value: 25, color: '#10B981' },
  { name: '技术支持', value: 20, color: '#F59E0B' },
  { name: '退款/售后', value: 12, color: '#EF4444' },
  { name: '其他', value: 8, color: '#6B7280' },
]

const satisfactionData = [
  { rating: '5星', count: 450, percentage: 45 },
  { rating: '4星', count: 280, percentage: 28 },
  { rating: '3星', count: 150, percentage: 15 },
  { rating: '2星', count: 70, percentage: 7 },
  { rating: '1星', count: 50, percentage: 5 },
]

export default function Analytics() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d')

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">数据分析</h1>
          <p className="mt-1 text-sm text-gray-500">
            深入了解AI客服系统的使用情况和性能指标
          </p>
        </div>
        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md ${
                timeRange === range
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              {range === '7d' ? '近7天' : range === '30d' ? '近30天' : '近90天'}
            </button>
          ))}
        </div>
      </div>

      {/* 关键指标 */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="card-body">
            <p className="text-sm font-medium text-gray-500">总会话数</p>
            <p className="mt-1 text-3xl font-semibold text-gray-900">1,284</p>
            <p className="mt-1 text-sm text-green-600">+12% 较上期</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <p className="text-sm font-medium text-gray-500">平均响应时间</p>
            <p className="mt-1 text-3xl font-semibold text-gray-900">1.8s</p>
            <p className="mt-1 text-sm text-green-600">-0.3s 较上期</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <p className="text-sm font-medium text-gray-500">解决率</p>
            <p className="mt-1 text-3xl font-semibold text-gray-900">94.2%</p>
            <p className="mt-1 text-sm text-green-600">+2.1% 较上期</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <p className="text-sm font-medium text-gray-500">平均满意度</p>
            <p className="mt-1 text-3xl font-semibold text-gray-900">4.3/5</p>
            <p className="mt-1 text-sm text-green-600">+0.2 较上期</p>
          </div>
        </div>
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 会话趋势 */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              会话趋势
            </h3>
          </div>
          <div className="card-body">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={conversationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="conversations" fill="#4F46E5" name="总会话" />
                  <Bar dataKey="resolved" fill="#10B981" name="已解决" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* 响应时间趋势 */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              平均响应时间 (秒)
            </h3>
          </div>
          <div className="card-body">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={responseTimeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="avgTime" 
                    stroke="#4F46E5" 
                    strokeWidth={2}
                    dot={{ fill: '#4F46E5' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* 话题分布 */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              咨询话题分布
            </h3>
          </div>
          <div className="card-body">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={topicData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {topicData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2">
              {topicData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-gray-600">{item.name} ({item.value}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 满意度分布 */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              满意度分布
            </h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {satisfactionData.map((item) => (
                <div key={item.rating}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{item.rating}</span>
                    <span className="text-sm text-gray-500">{item.count} ({item.percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        item.rating === '5星' ? 'bg-green-500' :
                        item.rating === '4星' ? 'bg-green-400' :
                        item.rating === '3星' ? 'bg-yellow-400' :
                        item.rating === '2星' ? 'bg-orange-400' : 'bg-red-500'
                      }`}
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
