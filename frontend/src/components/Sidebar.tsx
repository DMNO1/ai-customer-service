import { NavLink } from 'react-router-dom'
import {
  HomeIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  HeartIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: '概览', href: '/', icon: HomeIcon },
  { name: '知识库', href: '/knowledge-base', icon: BookOpenIcon },
  { name: '对话记录', href: '/conversations', icon: ChatBubbleLeftRightIcon },
  { name: '数据分析', href: '/analytics', icon: ChartBarIcon },
  { name: '健康状态', href: '/health', icon: HeartIcon },
  { name: '设置', href: '/settings', icon: Cog6ToothIcon },
]

export default function Sidebar() {
  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
      <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-indigo-600 px-6 pb-4">
        <div className="flex h-16 shrink-0 items-center">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-white flex items-center justify-center">
              <span className="text-indigo-600 font-bold text-lg">AI</span>
            </div>
            <span className="text-white font-semibold text-lg">智能客服</span>
          </div>
        </div>
        <nav className="flex flex-1 flex-col">
          <ul role="list" className="flex flex-1 flex-col gap-y-7">
            <li>
              <ul role="list" className="-mx-2 space-y-1">
                {navigation.map((item) => (
                  <li key={item.name}>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors ${
                          isActive
                            ? 'bg-indigo-700 text-white'
                            : 'text-indigo-200 hover:text-white hover:bg-indigo-700'
                        }`
                      }
                    >
                      <item.icon
                        className="h-6 w-6 shrink-0"
                        aria-hidden="true"
                      />
                      {item.name}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </li>
            <li className="mt-auto">
              <div className="text-xs text-indigo-200">
                <p>版本: v1.0.0</p>
                <p className="mt-1">© 2026 AI Customer Service</p>
              </div>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  )
}
