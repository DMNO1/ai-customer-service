import { useState } from 'react'
import { useMutation } from 'react-query'
import { 
  DocumentArrowUpIcon, 
  LinkIcon, 
  TrashIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { parseDocument, parseDocumentFromUrl } from '../services/api'

interface Document {
  id: string
  title: string
  type: 'file' | 'url'
  source: string
  size?: string
  createdAt: string
  status: 'active' | 'processing' | 'error'
}

const mockDocuments: Document[] = [
  { id: '1', title: '产品使用手册.pdf', type: 'file', source: 'upload', size: '2.4 MB', createdAt: '2026-03-17', status: 'active' },
  { id: '2', title: '常见问题FAQ', type: 'url', source: 'https://example.com/faq', createdAt: '2026-03-16', status: 'active' },
  { id: '3', title: '退款政策文档.docx', type: 'file', source: 'upload', size: '156 KB', createdAt: '2026-03-15', status: 'active' },
]

export default function KnowledgeBase() {
  const [documents, setDocuments] = useState<Document[]>(mockDocuments)
  const [urlInput, setUrlInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  const uploadMutation = useMutation(parseDocument, {
    onSuccess: (data) => {
      toast.success('文档上传成功')
      // 添加新文档到列表
      const newDoc: Document = {
        id: Date.now().toString(),
        title: data.data?.metadata?.filename || '新文档',
        type: 'file',
        source: 'upload',
        createdAt: new Date().toISOString().split('T')[0],
        status: 'active',
      }
      setDocuments([newDoc, ...documents])
    },
    onError: () => {
      toast.error('文档上传失败')
    },
  })

  const urlMutation = useMutation(parseDocumentFromUrl, {
    onSuccess: (data) => {
      toast.success('URL解析成功')
      const newDoc: Document = {
        id: Date.now().toString(),
        title: data.data?.metadata?.title || '网页文档',
        type: 'url',
        source: urlInput,
        createdAt: new Date().toISOString().split('T')[0],
        status: 'active',
      }
      setDocuments([newDoc, ...documents])
      setUrlInput('')
    },
    onError: () => {
      toast.error('URL解析失败')
    },
  })

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  const handleUrlSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (urlInput.trim()) {
      urlMutation.mutate(urlInput.trim())
    }
  }

  const handleDelete = (id: string) => {
    setDocuments(documents.filter(doc => doc.id !== id))
    toast.success('文档已删除')
  }

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">知识库</h1>
        <p className="mt-1 text-sm text-gray-500">
          管理AI客服的知识库文档，支持文件上传和网页抓取
        </p>
      </div>

      {/* 添加文档区域 */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 文件上传 */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              上传文档
            </h3>
          </div>
          <div className="card-body">
            <div className="flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10">
              <div className="text-center">
                <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-300" aria-hidden="true" />
                <div className="mt-4 flex text-sm leading-6 text-gray-600 justify-center">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer rounded-md bg-white font-semibold text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 hover:text-indigo-500"
                  >
                    <span>选择文件</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      onChange={handleFileUpload}
                      accept=".pdf,.docx,.txt,.md"
                    />
                  </label>
                </div>
                <p className="text-xs leading-5 text-gray-600">支持 PDF, DOCX, TXT, Markdown</p>
                {uploadMutation.isLoading && (
                  <p className="mt-2 text-sm text-indigo-600">上传中...</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* URL输入 */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              添加网页
            </h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleUrlSubmit} className="space-y-4">
              <div>
                <label htmlFor="url" className="block text-sm font-medium leading-6 text-gray-900">
                  网页链接
                </label>
                <div className="mt-2 flex rounded-md shadow-sm">
                  <div className="relative flex flex-grow items-stretch focus-within:z-10">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                      <LinkIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                    </div>
                    <input
                      type="url"
                      name="url"
                      id="url"
                      className="input pl-10"
                      placeholder="https://example.com/help"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={urlMutation.isLoading || !urlInput.trim()}
                    className="btn-primary ml-3"
                  >
                    {urlMutation.isLoading ? '解析中...' : '添加'}
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500">
                输入帮助文档或FAQ页面的URL，系统将自动抓取内容
              </p>
            </form>
          </div>
        </div>
      </div>

      {/* 文档列表 */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h3 className="text-base font-semibold leading-6 text-gray-900">
            文档列表
          </h3>
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            </div>
            <input
              type="text"
              className="input pl-10 w-64"
              placeholder="搜索文档..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                  文档
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  类型
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  大小/来源
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  添加时间
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  状态
                </th>
                <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                  <span className="sr-only">操作</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {filteredDocuments.length > 0 ? (
                filteredDocuments.map((doc) => (
                  <tr key={doc.id}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm sm:pl-6">
                      <div className="flex items-center">
                        <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-2" />
                        <div className="font-medium text-gray-900">{doc.title}</div>
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {doc.type === 'file' ? '文件' : '网页'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {doc.size || doc.source}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {doc.createdAt}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm">
                      <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        doc.status === 'active' ? 'bg-green-100 text-green-800' :
                        doc.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {doc.status === 'active' ? '可用' :
                         doc.status === 'processing' ? '处理中' : '错误'}
                      </span>
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-gray-500">
                    暂无文档
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
