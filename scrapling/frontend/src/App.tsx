import { useState } from 'react'
import { Search, Play, Download, Database, Settings, BarChart3, Users, MessageSquare, Clock, ThumbsUp, Share2, Eye, Link, Plus, Trash2 } from 'lucide-react'

// 类型定义
interface CrawlConfig {
  keyword: string
  urls: string[]
  platform: 'douyin' | 'xiaohongshu' | 'all'
  limit: number
  sortBy: 'like_count' | 'comment_count' | 'publish_time' | 'play_count'
}

interface CrawlItem {
  id: number
  platform: string
  type: string
  title: string
  description: string
  url: string
  cover_url: string
  author_name: string
  author_url: string
  author_avatar: string
  publish_time: string
  like_count: number
  comment_count: number
  share_count: number
  play_count: number
  crawl_time: string
  source_type: string
}

interface PreviewResult {
  platform: string
  estimated_count: number
}

type CrawlStatus = 'idle' | 'previewing' | 'crawling' | 'completed' | 'error'

function App() {
  const [config, setConfig] = useState<CrawlConfig>({
    keyword: '',
    urls: [],
    platform: 'all',
    limit: 100,
    sortBy: 'like_count'
  })
  const [newUrl, setNewUrl] = useState('')
  const [status, setStatus] = useState<CrawlStatus>('idle')
  const [previewResults, setPreviewResults] = useState<PreviewResult[]>([])
  const [items, setItems] = useState<CrawlItem[]>([])
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [savedCount, setSavedCount] = useState(0)
  const [skippedCount, setSkippedCount] = useState(0)
  const [activeTab, setActiveTab] = useState<'config' | 'results' | 'export'>('config')

  // 添加URL
  const addUrl = () => {
    if (newUrl.trim() && !config.urls.includes(newUrl.trim())) {
      setConfig({ ...config, urls: [...config.urls, newUrl.trim()] })
      setNewUrl('')
    }
  }

  // 删除URL
  const removeUrl = (index: number) => {
    setConfig({ ...config, urls: config.urls.filter((_, i) => i !== index) })
  }

  // 检查是否有输入
  const hasInput = () => {
    return config.keyword.trim() !== '' || config.urls.length > 0
  }

  // 模拟预抓取
  const handlePreview = async () => {
    if (!config.keyword.trim()) {
      setError('预抓取只支持关键词搜索')
      return
    }
    
    setStatus('previewing')
    setError('')
    
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const results: PreviewResult[] = [
      { platform: 'douyin', estimated_count: Math.floor(Math.random() * 5000) + 1000 },
      { platform: 'xiaohongshu', estimated_count: Math.floor(Math.random() * 3000) + 500 }
    ]
    
    setPreviewResults(results)
    setStatus('idle')
  }

  // 模拟抓取
  const handleCrawl = async () => {
    if (!hasInput()) {
      setError('请提供关键词或内容链接')
      return
    }
    
    setStatus('crawling')
    setProgress(0)
    setError('')
    setSavedCount(0)
    setSkippedCount(0)
    
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 500))
      setProgress(i)
    }
    
    const mockItems: CrawlItem[] = []
    const platforms = config.platform === 'all' ? ['douyin', 'xiaohongshu'] : [config.platform]
    const totalItems = Math.min(config.limit + config.urls.length, 50)
    
    // 添加关键词搜索的模拟数据
    for (let i = 0; i < Math.min(config.limit, totalItems); i++) {
      const platform = platforms[i % platforms.length]
      mockItems.push({
        id: i + 1,
        platform,
        type: platform === 'douyin' ? 'video' : 'note',
        title: config.keyword ? `【${config.keyword}】第${i + 1}条内容标题` : `推荐内容第${i + 1}条`,
        description: `这是第${i + 1}条内容描述，包含详细的产品介绍和使用体验分享。`,
        url: platform === 'douyin' ? `https://www.douyin.com/video/${Date.now()}-${i}` : `https://www.xiaohongshu.com/item/${Date.now()}-${i}`,
        cover_url: `https://picsum.photos/seed/${i}/400/300`,
        author_name: `用户${i + 1}号`,
        author_url: `https://example.com/user/${i}`,
        author_avatar: `https://picsum.photos/seed/avatar${i}/50/50`,
        publish_time: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toLocaleDateString('zh-CN'),
        like_count: Math.floor(Math.random() * 10000),
        comment_count: Math.floor(Math.random() * 1000),
        share_count: Math.floor(Math.random() * 500),
        play_count: platform === 'douyin' ? Math.floor(Math.random() * 100000) : 0,
        crawl_time: new Date().toISOString(),
        source_type: 'keyword'
      })
    }
    
    // 添加URL抓取的模拟数据
    for (let i = 0; i < Math.min(config.urls.length, totalItems - mockItems.length); i++) {
      const url = config.urls[i]
      const platform = url.includes('douyin') ? 'douyin' : (url.includes('xiaohongshu') || url.includes('xhs') ? 'xiaohongshu' : platforms[i % platforms.length])
      mockItems.push({
        id: mockItems.length + 1,
        platform,
        type: platform === 'douyin' ? 'video' : 'note',
        title: `从链接抓取的内容 ${i + 1}`,
        description: `这是从链接 ${url} 抓取的内容描述。`,
        url: url,
        cover_url: `https://picsum.photos/seed/url${i}/400/300`,
        author_name: `链接用户${i + 1}号`,
        author_url: `https://example.com/user/url${i}`,
        author_avatar: `https://picsum.photos/seed/avatar_url${i}/50/50`,
        publish_time: new Date(Date.now() - Math.random() * 3 * 24 * 60 * 60 * 1000).toLocaleDateString('zh-CN'),
        like_count: Math.floor(Math.random() * 5000),
        comment_count: Math.floor(Math.random() * 500),
        share_count: Math.floor(Math.random() * 200),
        play_count: platform === 'douyin' ? Math.floor(Math.random() * 50000) : 0,
        crawl_time: new Date().toISOString(),
        source_type: 'url'
      })
    }
    
    setItems(mockItems)
    setSavedCount(mockItems.length)
    setSkippedCount(Math.floor(totalItems * 0.1))
    setStatus('completed')
    setActiveTab('results')
  }

  // 导出数据
  const handleExport = async (format: 'csv' | 'json' | 'xlsx') => {
    if (items.length === 0) {
      setError('没有数据可导出')
      return
    }
    
    const data = items.map(item => ({
      '平台': item.platform === 'douyin' ? '抖音' : '小红书',
      '类型': item.type === 'video' ? '视频' : '笔记',
      '来源': item.source_type === 'keyword' ? '关键词搜索' : '链接抓取',
      '标题': item.title,
      '描述': item.description,
      '链接': item.url,
      '封面图': item.cover_url,
      '作者名称': item.author_name,
      '作者链接': item.author_url,
      '作者头像': item.author_avatar,
      '发布时间': item.publish_time,
      '点赞数': item.like_count,
      '评论数': item.comment_count,
      '分享数': item.share_count,
      '播放量': item.play_count,
      '抓取时间': new Date(item.crawl_time).toLocaleString('zh-CN')
    }))
    
    let content = ''
    let filename = `scrapling_${config.keyword || 'urls'}_${Date.now()}`
    let mimeType = ''
    
    if (format === 'csv') {
      const headers = Object.keys(data[0])
      content = headers.join(',') + '\n' + data.map(row => headers.map(h => `"${String(row[h])}"`).join(',')).join('\n')
      filename += '.csv'
      mimeType = 'text/csv;charset=utf-8;'
    } else if (format === 'json') {
      content = JSON.stringify(data, null, 2)
      filename += '.json'
      mimeType = 'application/json'
    }
    
    const blob = new Blob([content], { type: mimeType })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
  }

  // 格式化数字
  const formatNumber = (num: number): string => {
    if (num >= 10000) {
      return (num / 10000).toFixed(1) + '万'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Search className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ScrapLing</h1>
                <p className="text-xs text-gray-500">社交媒体智能爬虫</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Database className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-600">数据库: {items.length} 条</span>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 标签页 */}
        <div className="bg-white rounded-2xl shadow-sm p-6 mb-6">
          <div className="flex border-b border-gray-200 mb-6">
            {[
              { key: 'config', label: '抓取配置', icon: Settings },
              { key: 'results', label: '数据结果', icon: BarChart3 },
              { key: 'export', label: '数据导出', icon: Download }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as 'config' | 'results' | 'export')}
                className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>

          {/* 配置面板 */}
          {activeTab === 'config' && (
            <div className="space-y-6">
              {/* 模式切换 */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">📌 抓取模式</h3>
                <div className="flex items-center space-x-4">
                  <div className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                    config.keyword.trim() ? 'border-blue-500 bg-white' : 'border-gray-200'
                  }`}>
                    <div className="flex items-center space-x-2">
                      <Search className="w-5 h-5 text-blue-500" />
                      <span className="text-sm font-medium text-gray-700">关键词搜索</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">根据关键词自动搜索内容</p>
                  </div>
                  <div className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                    config.urls.length > 0 ? 'border-purple-500 bg-white' : 'border-gray-200'
                  }`}>
                    <div className="flex items-center space-x-2">
                      <Link className="w-5 h-5 text-purple-500" />
                      <span className="text-sm font-medium text-gray-700">链接抓取</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">直接抓取指定链接内容</p>
                  </div>
                </div>
                {config.keyword.trim() && config.urls.length > 0 && (
                  <div className="mt-2 text-xs text-green-600 bg-green-50 px-3 py-2 rounded-lg">
                    ✅ 已启用混合模式：同时使用关键词和链接抓取
                  </div>
                )}
              </div>

              {/* 关键词输入 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  搜索关键词 <span className="text-gray-400">(可选)</span>
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={config.keyword}
                    onChange={(e) => setConfig({ ...config, keyword: e.target.value })}
                    placeholder="请输入要搜索的关键词，如：美妆产品、旅游攻略..."
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  />
                </div>
              </div>

              {/* URL输入 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  内容链接 <span className="text-gray-400">(可选，支持多个)</span>
                </label>
                
                {/* 添加URL */}
                <div className="flex space-x-2 mb-3">
                  <div className="relative flex-1">
                    <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={newUrl}
                      onChange={(e) => setNewUrl(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addUrl()}
                      placeholder="粘贴抖音或小红书内容链接..."
                      className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                    />
                  </div>
                  <button
                    onClick={addUrl}
                    disabled={!newUrl.trim()}
                    className="px-4 py-3 bg-purple-100 text-purple-700 rounded-xl hover:bg-purple-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
                  >
                    <Plus className="w-5 h-5" />
                    <span className="hidden sm:inline">添加</span>
                  </button>
                </div>

                {/* URL列表 */}
                {config.urls.length > 0 && (
                  <div className="space-y-2">
                    {config.urls.map((url, index) => (
                      <div key={index} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          url.includes('douyin') ? 'bg-blue-100 text-blue-700' : 
                          (url.includes('xiaohongshu') || url.includes('xhs')) ? 'bg-pink-100 text-pink-700' : 
                          'bg-gray-200 text-gray-600'
                        }`}>
                          {url.includes('douyin') ? '抖音' : 
                           (url.includes('xiaohongshu') || url.includes('xhs')) ? '小红书' : '未知'}
                        </span>
                        <span className="flex-1 text-sm text-gray-700 truncate">{url}</span>
                        <button
                          onClick={() => removeUrl(index)}
                          className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* 平台选择 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">目标平台</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'all', label: '全部平台', desc: '抖音 + 小红书' },
                    { value: 'douyin', label: '抖音', desc: '短视频内容' },
                    { value: 'xiaohongshu', label: '小红书', desc: '图文笔记' }
                  ].map(option => (
                    <button
                      key={option.value}
                      onClick={() => setConfig({ ...config, platform: option.value as 'douyin' | 'xiaohongshu' | 'all' })}
                      className={`p-4 rounded-xl border-2 transition-all text-left ${
                        config.platform === option.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium text-gray-900">{option.label}</div>
                      <div className="text-xs text-gray-500 mt-1">{option.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 抓取数量和排序 */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">抓取数量（关键词搜索）</label>
                  <div className="flex items-center space-x-4">
                    {[100, 300, 500].map(num => (
                      <button
                        key={num}
                        onClick={() => setConfig({ ...config, limit: num })}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          config.limit === num
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {num}条
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">排序方式</label>
                  <select
                    value={config.sortBy}
                    onChange={(e) => setConfig({ ...config, sortBy: e.target.value as 'like_count' | 'comment_count' | 'publish_time' | 'play_count' })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  >
                    <option value="like_count">按点赞数降序</option>
                    <option value="comment_count">按评论数降序</option>
                    <option value="play_count">按播放量降序</option>
                    <option value="publish_time">按发布时间降序</option>
                  </select>
                </div>
              </div>

              {/* 预抓取结果 */}
              {previewResults.length > 0 && (
                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">📊 预抓取统计</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {previewResults.map(result => (
                      <div key={result.platform} className="bg-white rounded-lg p-4 shadow-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            {result.platform === 'douyin' ? '抖音' : '小红书'}
                          </span>
                          <span className="text-lg font-bold text-blue-600">
                            {formatNumber(result.estimated_count)}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 mt-1">预估可抓取内容</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 错误提示 */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600">
                  ⚠️ {error}
                </div>
              )}

              {/* 操作按钮 */}
              <div className="flex space-x-4 pt-4">
                <button
                  onClick={handlePreview}
                  disabled={status === 'previewing' || status === 'crawling' || !config.keyword.trim()}
                  className="flex items-center space-x-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Eye className="w-5 h-5" />
                  <span>预抓取（统计数量）</span>
                </button>
                <button
                  onClick={handleCrawl}
                  disabled={status === 'previewing' || status === 'crawling'}
                  className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {status === 'crawling' ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>抓取中...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>开始抓取</span>
                    </>
                  )}
                </button>
              </div>

              {/* 进度条 */}
              {status === 'crawling' && (
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>抓取进度</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* 抓取结果统计 */}
              {status === 'completed' && (
                <div className="bg-green-50 border border-green-200 rounded-xl p-4 mt-4">
                  <div className="flex items-center space-x-2 text-green-700">
                    <span className="text-xl">🎉</span>
                    <span className="font-medium">抓取完成！</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-3">
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-xl font-bold text-blue-600">{savedCount}</div>
                      <div className="text-xs text-gray-500">新抓取</div>
                    </div>
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-xl font-bold text-gray-500">{skippedCount}</div>
                      <div className="text-xs text-gray-500">重复跳过</div>
                    </div>
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-xl font-bold text-green-600">{items.length}</div>
                      <div className="text-xs text-gray-500">数据库总计</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 结果面板 */}
          {activeTab === 'results' && (
            <div className="space-y-4">
              {items.length === 0 ? (
                <div className="text-center py-12">
                  <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">暂无数据，请先进行抓取</p>
                </div>
              ) : (
                <>
                  {/* 结果统计 */}
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-gray-600">共 {items.length} 条数据</span>
                    <div className="flex space-x-2">
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                        抖音: {items.filter(i => i.platform === 'douyin').length}
                      </span>
                      <span className="px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-xs">
                        小红书: {items.filter(i => i.platform === 'xiaohongshu').length}
                      </span>
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                        关键词: {items.filter(i => i.source_type === 'keyword').length}
                      </span>
                      <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs">
                        链接: {items.filter(i => i.source_type === 'url').length}
                      </span>
                    </div>
                  </div>

                  {/* 数据表格 */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="text-left py-3 px-4 font-medium text-gray-600 rounded-tl-xl">平台</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">来源</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">标题</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">作者</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">发布时间</th>
                          <th className="text-center py-3 px-4 font-medium text-gray-600">
                            <div className="flex items-center justify-center">
                              <ThumbsUp className="w-4 h-4 mr-1" />
                              点赞
                            </div>
                          </th>
                          <th className="text-center py-3 px-4 font-medium text-gray-600">
                            <div className="flex items-center justify-center">
                              <MessageSquare className="w-4 h-4 mr-1" />
                              评论
                            </div>
                          </th>
                          <th className="text-center py-3 px-4 font-medium text-gray-600">
                            <div className="flex items-center justify-center">
                              <Share2 className="w-4 h-4 mr-1" />
                              分享
                            </div>
                          </th>
                          <th className="text-center py-3 px-4 font-medium text-gray-600 rounded-tr-xl">
                            <div className="flex items-center justify-center">
                              <Eye className="w-4 h-4 mr-1" />
                              播放
                            </div>
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {items.map(item => (
                          <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-3 px-4">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                item.platform === 'douyin' ? 'bg-blue-100 text-blue-700' : 'bg-pink-100 text-pink-700'
                              }`}>
                                {item.platform === 'douyin' ? '抖音' : '小红书'}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                item.source_type === 'keyword' ? 'bg-green-100 text-green-700' : 'bg-purple-100 text-purple-700'
                              }`}>
                                {item.source_type === 'keyword' ? '关键词' : '链接'}
                              </span>
                            </td>
                            <td className="py-3 px-4 max-w-xs truncate">
                              <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                {item.title}
                              </a>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center space-x-2">
                                <img src={item.author_avatar} alt={item.author_name} className="w-6 h-6 rounded-full" />
                                <span className="text-gray-700">{item.author_name}</span>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center space-x-1 text-gray-500">
                                <Clock className="w-4 h-4" />
                                <span>{item.publish_time}</span>
                              </div>
                            </td>
                            <td className="py-3 px-4 text-center text-gray-600">
                              {formatNumber(item.like_count)}
                            </td>
                            <td className="py-3 px-4 text-center text-gray-600">
                              {formatNumber(item.comment_count)}
                            </td>
                            <td className="py-3 px-4 text-center text-gray-600">
                              {formatNumber(item.share_count)}
                            </td>
                            <td className="py-3 px-4 text-center text-gray-600">
                              {formatNumber(item.play_count)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          )}

          {/* 导出面板 */}
          {activeTab === 'export' && (
            <div className="space-y-6">
              {items.length === 0 ? (
                <div className="text-center py-12">
                  <Download className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">暂无数据可导出，请先进行抓取</p>
                </div>
              ) : (
                <>
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">导出数据</h3>
                    <div className="grid grid-cols-3 gap-4">
                      {[
                        { format: 'csv' as const, label: 'CSV', desc: '适用于 Excel', icon: '📊' },
                        { format: 'json' as const, label: 'JSON', desc: '适用于编程处理', icon: '📄' },
                      ].map(option => (
                        <button
                          key={option.format}
                          onClick={() => handleExport(option.format)}
                          className="p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-sm transition-all text-center"
                        >
                          <div className="text-3xl mb-2">{option.icon}</div>
                          <div className="font-medium text-gray-900">{option.label}</div>
                          <div className="text-xs text-gray-500 mt-1">{option.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-xl p-4">
                    <div className="flex items-start space-x-3">
                      <Users className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-800">数据说明</h4>
                        <ul className="text-sm text-blue-700 mt-2 space-y-1">
                          <li>• 导出文件包含所有已抓取的内容数据</li>
                          <li>• 包含作者信息、互动数据、发布时间等字段</li>
                          <li>• 新增"来源"字段，标识数据来自关键词搜索或链接抓取</li>
                          <li>• 建议使用 UTF-8 编码打开 CSV 文件</li>
                          <li>• 支持多次导出，数据会自动去重</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* 功能说明卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Search className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">智能搜索</h3>
                <p className="text-sm text-gray-500">支持多平台关键词搜索</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <Link className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">链接抓取</h3>
                <p className="text-sm text-gray-500">直接抓取指定内容链接</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Database className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">智能去重</h3>
                <p className="text-sm text-gray-500">基于内容指纹自动去重</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 页脚 */}
      <footer className="bg-white border-t border-gray-100 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            ScrapLing - 社交媒体智能爬虫工具 © 2024
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
