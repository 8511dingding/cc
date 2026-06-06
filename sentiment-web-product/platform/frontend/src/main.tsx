import React from 'react';
import { createRoot } from 'react-dom/client';
import {
  BookOpen,
  Brain,
  CheckCircle2,
  ChevronDown,
  FileSpreadsheet,
  FolderKanban,
  LogOut,
  Menu,
  Lightbulb,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Users
} from 'lucide-react';
import {
  createProject,
  deleteProject,
  fetchDashboard,
  patchBrands,
  patchRecord,
  patchReportCandidate,
  previewImportFile,
  updateProject
} from './api';
import type {
  DashboardResponse,
  DataRecord,
  ImportPreviewResponse,
  LabelField,
  LabelOption,
  LabelSchema,
  LabelValue,
  ProjectPayload,
  ProjectSummary
} from './types';
import './styles.css';

type ViewFilter = 'all' | 'unconfirmed' | 'negative' | 'conflict' | 'report';
type SortKey =
  | 'none'
  | 'comment_likes'
  | 'comment_replies'
  | 'comment_total'
  | 'comment_publish_time'
  | 'source_publish_time'
  | 'source_comments'
  | 'source_likes'
  | 'source_favorites'
  | 'source_shares';
type SortDirection = 'desc' | 'asc';
type ImportStage = 'upload' | 'mapping' | 'cleaning' | 'preview' | 'history';

interface AdvancedFilters {
  platform: string;
  commentType: string;
  minLikes: string;
  minReplies: string;
  sentimentPolarity: string;
  cognition: string;
  sentimentType: string;
  action: string;
  brand: string;
  reportStatus: string;
}

const defaultAdvancedFilters: AdvancedFilters = {
  platform: '',
  commentType: '',
  minLikes: '',
  minReplies: '',
  sentimentPolarity: '',
  cognition: '',
  sentimentType: '',
  action: '',
  brand: '',
  reportStatus: ''
};

const navItems = [
  { key: 'projects', label: '项目管理', icon: FolderKanban },
  { key: 'import', label: '数据导入', icon: FileSpreadsheet },
  { key: 'learning', label: '规则学习', icon: Brain },
  { key: 'auto', label: '自动打标', icon: Sparkles },
  { key: 'labeling', label: '人工标注', icon: CheckCircle2 },
  { key: 'report', label: '在线报告', icon: BookOpen },
  { key: 'users', label: '用户权限', icon: Users }
];

const projectPlatformOptions = ['小红书', '抖音', '微博', 'B站', '公众号', '视频号', '快手', '知乎'];

function optionLabel(schema: LabelSchema, fieldKey: string, value?: string | null): string {
  if (!value) return '未选择';
  const field = schema.fields.find(item => item.key === fieldKey);
  return field?.options.find(item => item.value === value)?.label ?? value;
}

function filteredOptions(field: LabelField, record: DataRecord): LabelOption[] {
  if (!field.parent_key) return field.options;
  const parentValue = record.labels[field.parent_key]?.final;
  return field.options.filter(option => option.parent_value === parentValue);
}

function labelTooltip(label: LabelValue | undefined, schema: LabelSchema, fieldKey: string): string {
  if (!label?.confirmed || !label.confirmed_by) return '未人工确认';
  const from = optionLabel(schema, fieldKey, label.previous_value);
  const to = optionLabel(schema, fieldKey, label.final);
  return `${label.confirmed_by.name}（${label.confirmed_by.role}）确认\n${label.confirmed_at ?? ''}\n${from} -> ${to}`;
}

function priorityRank(priority: ProjectSummary['priority']): number {
  return priority === '高' ? 3 : priority === '中' ? 2 : 1;
}

function App() {
  const [dashboard, setDashboard] = React.useState<DashboardResponse | null>(null);
  const [activeView, setActiveView] = React.useState('labeling');
  const [activeFilter, setActiveFilter] = React.useState<ViewFilter>('all');
  const [error, setError] = React.useState<string | null>(null);
  const [saveError, setSaveError] = React.useState<string | null>(null);
  const [saving, setSaving] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedRecordId, setSelectedRecordId] = React.useState<string | null>(null);
  const [sidebarPinned, setSidebarPinned] = React.useState(false);
  const [userMenuOpen, setUserMenuOpen] = React.useState(false);
  const [projectMenuOpen, setProjectMenuOpen] = React.useState(false);
  const [activeProjectId, setActiveProjectId] = React.useState<string | undefined>(undefined);
  const [advancedFilters, setAdvancedFilters] = React.useState<AdvancedFilters>(defaultAdvancedFilters);
  const [sortKey, setSortKey] = React.useState<SortKey>('none');
  const [sortDirection, setSortDirection] = React.useState<SortDirection>('desc');

  React.useEffect(() => {
    fetchDashboard(activeProjectId)
      .then(data => {
        setDashboard(data);
        setActiveProjectId(data.active_project.id);
        setSelectedRecordId(null);
        setActiveFilter('all');
        setAdvancedFilters(defaultAdvancedFilters);
      })
      .catch(err => setError(err instanceof Error ? err.message : '加载失败'));
  }, [activeProjectId]);

  const switchProject = (projectId: string) => {
    setProjectMenuOpen(false);
    setActiveProjectId(projectId);
    setActiveView('projects');
  };

  const addProject = async (payload: ProjectPayload) => {
    setSaveError(null);
    const created = await createProject(payload);
    setDashboard(current => current ? {
      ...current,
      projects: [created, ...current.projects],
      active_project: created,
      records: [],
      imports: [],
      export_records: [],
      report: {
        ...current.report,
        id: `report-${created.id}`,
        project_id: created.id,
        title: '在线舆情分析报告',
        version: 'v00',
        status: '待生成',
        blocks: [{
          id: `${created.id}-empty-summary`,
          title: '项目摘要',
          block_type: 'text',
          content: '项目创建后，请先完成数据导入、规则学习与自动打标，再生成在线报告。'
        }]
      }
    } : current);
    setActiveProjectId(created.id);
    setActiveView('projects');
    return created;
  };

  const editProject = async (projectId: string, payload: ProjectPayload) => {
    setSaveError(null);
    const updated = await updateProject(projectId, payload);
    setDashboard(current => current ? {
      ...current,
      projects: current.projects.map(project => (project.id === updated.id ? updated : project)),
      active_project: current.active_project.id === updated.id ? updated : current.active_project
    } : current);
    return updated;
  };

  const removeProject = async (projectId: string) => {
    if (!dashboard) return;
    setSaveError(null);
    const remaining = dashboard.projects.filter(project => project.id !== projectId);
    await deleteProject(projectId);
    const nextActive = dashboard.active_project.id === projectId ? remaining[0] : dashboard.active_project;
    setDashboard({
      ...dashboard,
      projects: remaining,
      active_project: nextActive
    });
    if (nextActive?.id && nextActive.id !== dashboard.active_project.id) {
      setActiveProjectId(nextActive.id);
    }
  };

  const updateLabel = async (record: DataRecord, field: LabelField, value: string) => {
    if (!dashboard) return;
    setSaving(true);
    setSaveError(null);
    try {
      const updated = await patchRecord(record.id, [
        { field_key: field.key, value, confirmed: true }
      ]);
      setDashboard({
        ...dashboard,
        records: dashboard.records.map(item => (item.id === updated.id ? updated : item))
      });
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const updateReportCandidate = async (record: DataRecord, reportCandidate: boolean) => {
    if (!dashboard) return;
    setSaving(true);
    setSaveError(null);
    try {
      const updated = await patchReportCandidate(record.id, reportCandidate);
      setDashboard({
        ...dashboard,
        records: dashboard.records.map(item => (item.id === updated.id ? updated : item))
      });
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const updateBrands = async (record: DataRecord, brands: string[]) => {
    if (!dashboard) return;
    setSaving(true);
    setSaveError(null);
    try {
      const updated = await patchBrands(record.id, brands);
      setDashboard({
        ...dashboard,
        records: dashboard.records.map(item => (item.id === updated.id ? updated : item))
      });
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  if (error) {
    return <div className="error-screen">{error}</div>;
  }

  if (!dashboard) {
    return <div className="loading-screen">正在加载舆情标注平台...</div>;
  }

  const baseRecords = dashboard.records
    .filter(record => {
      if (activeFilter === 'unconfirmed') {
        return !Object.values(record.labels).some(label => label.confirmed);
      }
      if (activeFilter === 'negative') {
        return record.labels.sentiment_polarity?.final === 'negative';
      }
      if (activeFilter === 'conflict') {
        return Object.values(record.labels).some(label => label.manual && label.manual !== label.auto);
      }
      if (activeFilter === 'report') {
        return record.report_candidate;
      }
      return true;
    })
    .filter(record => {
      const term = searchTerm.trim();
      if (!term) return true;
      return record.content.includes(term) || record.platform.includes(term) || record.author.includes(term);
    });
  const filteredRecords = applyAdvancedFilters(baseRecords, advancedFilters);
  const visibleRecords = sortRecords(filteredRecords, sortKey, sortDirection);
  const tableStats = buildTableStats(filteredRecords, dashboard.label_schema);
  const platformOptions = uniqueOptions(dashboard.records.map(record => record.platform));
  const brandOptions = uniqueOptions([
    ...dashboard.brand_rules.map(rule => rule.brand),
    ...dashboard.records.flatMap(record => record.brands)
  ]);
  const selectedRecord = visibleRecords.find(record => record.id === selectedRecordId) ?? visibleRecords[0];
  const labelingProjectCount = dashboard.projects.filter(project => project.status === '标注中').length;
  const activeProjectCount = dashboard.projects.filter(project => project.status !== '已交付').length;
  const totalProjectRows = dashboard.projects.reduce((total, project) => total + project.total_count, 0);
  const dueProjectCount = dashboard.projects.filter(project => project.delivery_due && project.status !== '已交付').length;

  return (
    <div className={`platform-shell ${activeView === 'labeling' ? 'is-labeling' : ''} ${sidebarPinned ? 'sidebar-pinned' : ''}`}>
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark" />
          <div>
            <strong>舆情标注平台</strong>
            <span>Sentiment Lab</span>
          </div>
        </div>
        <button
          type="button"
          className="sidebar-toggle"
          aria-pressed={sidebarPinned}
          aria-label={sidebarPinned ? '收起侧边导航' : '展开侧边导航'}
          title={sidebarPinned ? '收起侧边导航' : '展开侧边导航'}
          onClick={() => setSidebarPinned(value => !value)}
        >
          <Menu size={17} />
          <span>{sidebarPinned ? '收起导航' : '展开导航'}</span>
        </button>
        <nav className="nav-list">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                type="button"
                key={item.key}
                className={activeView === item.key ? 'active' : ''}
                onClick={() => setActiveView(item.key)}
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="workspace">
        <header className="workspace-header">
          <div className="project-title-wrap">
            <p className="eyebrow">当前项目 / {dashboard.active_project.rule_version}</p>
            <div className="project-title-row">
              <h1>{dashboard.active_project.name}</h1>
              <div className="project-switch-wrap">
                <button
                  type="button"
                  className="project-switch"
                  aria-expanded={projectMenuOpen}
                  onClick={() => setProjectMenuOpen(value => !value)}
                >
                  切换项目
                  <ChevronDown size={15} />
                </button>
                {projectMenuOpen && (
                  <div className="project-menu" role="menu">
                    {dashboard.projects.map(project => (
                      <button
                        key={project.id}
                        type="button"
                        role="menuitem"
                        className={project.id === dashboard.active_project.id ? 'active' : ''}
                        onClick={() => switchProject(project.id)}
                      >
                        <strong>{project.name}</strong>
                        <span>{project.date_range} / {project.status}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <p className="header-copy">
              {dashboard.active_project.date_range} / 更新于 {dashboard.active_project.updated_at} / 负责人 {dashboard.active_project.owner.name}
            </p>
          </div>
          <div className="user-menu-wrap">
            <button
              type="button"
              className="user-card"
              aria-expanded={userMenuOpen}
              onClick={() => setUserMenuOpen(value => !value)}
            >
              <div className="avatar">{dashboard.user.avatar}</div>
              <div>
                <strong>{dashboard.user.name}</strong>
                <span>{dashboard.user.role}</span>
              </div>
              <ChevronDown size={15} />
            </button>
            {userMenuOpen && (
              <div className="user-menu" role="menu">
                <button type="button" role="menuitem" onClick={() => { setActiveView('users'); setUserMenuOpen(false); }}>
                  <Users size={16} />
                  <span>用户与权限</span>
                </button>
                <button type="button" role="menuitem" onClick={() => setUserMenuOpen(false)}>
                  <Settings size={16} />
                  <span>偏好设置</span>
                </button>
                <button type="button" role="menuitem" onClick={() => setUserMenuOpen(false)}>
                  <LogOut size={16} />
                  <span>退出登录</span>
                </button>
              </div>
            )}
          </div>
        </header>

        <section className="metric-grid">
          {activeView === 'projects' ? (
            <>
              <button type="button" className="metric-card" onClick={() => setActiveView('projects')}>
                <span>累计项目</span>
                <strong>{dashboard.projects.length.toLocaleString()} 个</strong>
                <p>{activeProjectCount.toLocaleString()} 个项目仍在推进</p>
              </button>
              <button type="button" className="metric-card" onClick={() => setActiveView('labeling')}>
                <span>标注中项目</span>
                <strong>{labelingProjectCount.toLocaleString()} 个</strong>
                <p>点击进入人工标注工作台</p>
              </button>
              <button type="button" className="metric-card" onClick={() => setActiveView('import')}>
                <span>累计数据量</span>
                <strong>{totalProjectRows.toLocaleString()}</strong>
                <p>所有项目累计评论行数</p>
              </button>
              <button type="button" className="metric-card warning" onClick={() => setActiveView('projects')}>
                <span>待交付项目</span>
                <strong>{dueProjectCount.toLocaleString()} 个</strong>
                <p>按项目交付日期跟踪</p>
              </button>
            </>
          ) : (
            <>
              <button type="button" className="metric-card" onClick={() => setActiveView('projects')}>
                <span>项目进度</span>
                <strong>{dashboard.active_project.progress}%</strong>
                <p>已确认 {dashboard.active_project.confirmed_count.toLocaleString()} / {dashboard.active_project.total_count.toLocaleString()}</p>
              </button>
              <button type="button" className="metric-card" onClick={() => setActiveView('auto')}>
                <span>标签体系</span>
                <strong>{dashboard.label_schema.name}</strong>
                <p>{dashboard.label_schema.fields.length} 个动态标签字段</p>
              </button>
              <button type="button" className="metric-card warning" onClick={() => setActiveView('learning')}>
                <span>规则建议</span>
                <strong>{dashboard.suggestions.length} 条</strong>
                <p>来自本轮人工修改差异</p>
              </button>
              <button type="button" className="metric-card" onClick={() => setActiveView('report')}>
                <span>报告状态</span>
                <strong>{dashboard.report.status}</strong>
                <p>{dashboard.report.version} / 可在线确认</p>
              </button>
            </>
          )}
        </section>

        {activeView !== 'labeling' && (
          <WorkbenchView
            view={activeView}
            dashboard={dashboard}
            onNavigate={setActiveView}
            onProjectSwitch={switchProject}
            onProjectCreate={addProject}
            onProjectUpdate={editProject}
            onProjectDelete={removeProject}
          />
        )}

        {activeView === 'labeling' && (
          <section className="labeling-layout">
            <div className="labeling-top">
              <div>
                <h2>人工标注工作台</h2>
                <p>表格区域已优先铺开，适合连续下拉选择、批量校正和横向比对。</p>
              </div>
              <LabelingInsights dashboard={dashboard} onNavigate={setActiveView} />
            </div>
            <div className="labeling-main">
              <div className="table-toolbar">
                <div className="view-tabs">
                  <button type="button" className={activeFilter === 'all' ? 'active' : ''} onClick={() => setActiveFilter('all')}>全部</button>
                  <button type="button" className={activeFilter === 'unconfirmed' ? 'active' : ''} onClick={() => setActiveFilter('unconfirmed')}>未确认</button>
                  <button type="button" className={activeFilter === 'negative' ? 'active' : ''} onClick={() => setActiveFilter('negative')}>负面</button>
                  <button type="button" className={activeFilter === 'conflict' ? 'active' : ''} onClick={() => setActiveFilter('conflict')}>规则冲突</button>
                  <button type="button" className={activeFilter === 'report' ? 'active' : ''} onClick={() => setActiveFilter('report')}>报告候选</button>
                </div>
                <div className="search-box">
                  <Search size={16} />
                  <input value={searchTerm} onChange={event => setSearchTerm(event.target.value)} placeholder="搜索内容、平台、作者" />
                </div>
              </div>
              <TableFilters
                filters={advancedFilters}
                onChange={setAdvancedFilters}
                schema={dashboard.label_schema}
                platformOptions={platformOptions}
                brandOptions={brandOptions}
                sortKey={sortKey}
                sortDirection={sortDirection}
                onSortKeyChange={setSortKey}
                onSortDirectionChange={setSortDirection}
              />
              <TableStats stats={tableStats} />
              <div className="save-strip">
                <span className={saving ? 'status-saving' : 'status-saved'}>
                  {saving ? '自动保存中...' : saveError ? '保存失败' : '已保存'}
                </span>
                <span>{saveError ?? '人工确认以黄色点标记，后续规则重跑不会覆盖。'}</span>
                <button type="button"><RefreshCw size={16} /> 重新打标未确认数据</button>
                {selectedRecord && <span className="selected-record">当前：{selectedRecord.author} / {selectedRecord.platform}</span>}
              </div>
              <LabelGrid
                records={visibleRecords}
                schema={dashboard.label_schema}
                onChange={updateLabel}
                onReportCandidateChange={updateReportCandidate}
                onBrandsChange={updateBrands}
                brandOptions={brandOptions}
                selectedRecordId={selectedRecord?.id ?? null}
                onSelect={setSelectedRecordId}
              />
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function LabelingInsights({
  dashboard,
  onNavigate
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
}) {
  const topSuggestion = dashboard.suggestions[0];

  return (
    <div className="insight-strip" aria-label="标注辅助信息">
      {topSuggestion && (
        <button type="button" className="mini-insight warning" onClick={() => onNavigate('learning')}>
          <div>
            <h3><Lightbulb size={16} /> 规则学习建议</h3>
            <strong>{topSuggestion.title}</strong>
            <span>{topSuggestion.evidence_count} 条证据</span>
          </div>
          <em>查看</em>
        </button>
      )}
      <button type="button" className="mini-insight" onClick={() => onNavigate('report')}>
        <div>
          <h3><BookOpen size={16} /> 在线报告</h3>
          <strong>{dashboard.report.version} / {dashboard.report.status}</strong>
          <span>{dashboard.report.blocks.length} 个报告块待确认</span>
        </div>
        <em>打开</em>
      </button>
    </div>
  );
}

function TableFilters({
  filters,
  onChange,
  schema,
  platformOptions,
  brandOptions,
  sortKey,
  sortDirection,
  onSortKeyChange,
  onSortDirectionChange
}: {
  filters: AdvancedFilters;
  onChange: (filters: AdvancedFilters) => void;
  schema: LabelSchema;
  platformOptions: string[];
  brandOptions: string[];
  sortKey: SortKey;
  sortDirection: SortDirection;
  onSortKeyChange: (key: SortKey) => void;
  onSortDirectionChange: (direction: SortDirection) => void;
}) {
  const update = (key: keyof AdvancedFilters, value: string) => onChange({ ...filters, [key]: value });

  return (
    <div className="filter-panel">
      <label>
        <span>平台</span>
        <select value={filters.platform} onChange={event => update('platform', event.target.value)}>
          <option value="">全部平台</option>
          {platformOptions.map(platform => <option key={platform} value={platform}>{platform}</option>)}
        </select>
      </label>
      <label>
        <span>点赞 ≥</span>
        <input inputMode="numeric" value={filters.minLikes} onChange={event => update('minLikes', event.target.value)} placeholder="不限" />
      </label>
      <label>
        <span>回复 ≥</span>
        <input inputMode="numeric" value={filters.minReplies} onChange={event => update('minReplies', event.target.value)} placeholder="不限" />
      </label>
      <label>
        <span>评论类型</span>
        <select value={filters.commentType} onChange={event => update('commentType', event.target.value)}>
          <option value="">全部类型</option>
          {['长评论', '提及竞品', '普通内容', '@他人', '符号表情'].map(type => <option key={type} value={type}>{type}</option>)}
        </select>
      </label>
      <FilterSelect label="正负面" fieldKey="sentiment_polarity" schema={schema} value={filters.sentimentPolarity} onChange={value => update('sentimentPolarity', value)} />
      <FilterSelect label="认知" fieldKey="cognition" schema={schema} value={filters.cognition} onChange={value => update('cognition', value)} />
      <FilterSelect label="情绪" fieldKey="sentiment_type" schema={schema} value={filters.sentimentType} onChange={value => update('sentimentType', value)} />
      <FilterSelect label="行动" fieldKey="action" schema={schema} value={filters.action} onChange={value => update('action', value)} />
      <label>
        <span>品牌</span>
        <select value={filters.brand} onChange={event => update('brand', event.target.value)}>
          <option value="">全部品牌</option>
          {brandOptions.map(brand => <option key={brand} value={brand}>{brand}</option>)}
        </select>
      </label>
      <label>
        <span>报告统计</span>
        <select value={filters.reportStatus} onChange={event => update('reportStatus', event.target.value)}>
          <option value="">全部</option>
          <option value="included">纳入</option>
          <option value="excluded">排除</option>
        </select>
      </label>
      <label className="sort-control">
        <span>排序</span>
        <select value={sortKey} onChange={event => onSortKeyChange(event.target.value as SortKey)}>
          <option value="none">默认顺序</option>
          <option value="comment_total">评论互动合计</option>
          <option value="comment_likes">评论点赞</option>
          <option value="comment_replies">评论回复</option>
          <option value="comment_publish_time">评论发布时间</option>
          <option value="source_publish_time">内容发布时间</option>
          <option value="source_comments">内容评论数</option>
          <option value="source_likes">内容点赞数</option>
          <option value="source_favorites">内容收藏数</option>
          <option value="source_shares">内容分享数</option>
        </select>
      </label>
      <label>
        <span>方向</span>
        <select value={sortDirection} onChange={event => onSortDirectionChange(event.target.value as SortDirection)}>
          <option value="desc">从高到低 / 新到旧</option>
          <option value="asc">从低到高 / 旧到新</option>
        </select>
      </label>
      <button type="button" className="clear-filters" onClick={() => onChange(defaultAdvancedFilters)}>清空筛选</button>
    </div>
  );
}

function FilterSelect({
  label,
  fieldKey,
  schema,
  value,
  onChange
}: {
  label: string;
  fieldKey: string;
  schema: LabelSchema;
  value: string;
  onChange: (value: string) => void;
}) {
  const field = schema.fields.find(item => item.key === fieldKey);
  return (
    <label>
      <span>{label}</span>
      <select value={value} onChange={event => onChange(event.target.value)}>
        <option value="">全部</option>
        {field?.options.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
    </label>
  );
}

function TableStats({ stats }: { stats: ReturnType<typeof buildTableStats> }) {
  return (
    <div className="table-stats">
      <StatBlock title="当前结果" value={stats.total.toLocaleString()} detail={`纳入 ${stats.reportIncluded.toLocaleString()} / 排除 ${stats.reportExcluded.toLocaleString()}`} />
      <StatBlock title="正负面" value={stats.topSentiment} detail={stats.sentimentSummary} />
      <StatBlock title="认知" value={stats.topCognition} detail={stats.cognitionSummary} />
      <StatBlock title="情绪" value={stats.topEmotion} detail={stats.emotionSummary} />
      <StatBlock title="行动" value={stats.topAction} detail={stats.actionSummary} />
    </div>
  );
}

function StatBlock({ title, value, detail }: { title: string; value: string; detail: string }) {
  return (
    <div className="stat-block">
      <span>{title}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function LabelGrid({
  records,
  schema,
  onChange,
  onReportCandidateChange,
  onBrandsChange,
  brandOptions,
  selectedRecordId,
  onSelect
}: {
  records: DataRecord[];
  schema: LabelSchema;
  onChange: (record: DataRecord, field: LabelField, value: string) => void;
  onReportCandidateChange: (record: DataRecord, reportCandidate: boolean) => void;
  onBrandsChange: (record: DataRecord, brands: string[]) => void;
  brandOptions: string[];
  selectedRecordId: string | null;
  onSelect: (recordId: string) => void;
}) {
  const [expandedRecordIds, setExpandedRecordIds] = React.useState<Set<string>>(new Set());

  const toggleExpanded = (recordId: string) => {
    setExpandedRecordIds(previous => {
      const next = new Set(previous);
      if (next.has(recordId)) {
        next.delete(recordId);
      } else {
        next.add(recordId);
      }
      return next;
    });
  };

  if (records.length === 0) {
    return (
      <div className="empty-state">
        <strong>没有匹配的数据</strong>
        <span>调整筛选条件或搜索词后再试。</span>
      </div>
    );
  }

  return (
    <div className="grid-frame">
      <table className="label-grid">
        <thead>
          <tr>
            <th className="id-col">评论ID</th>
            <th>平台</th>
            <th className="sticky-col content-col">内容</th>
            <th>互动数据</th>
            <th>正负面</th>
            <th>认知</th>
            <th>情绪</th>
            <th>行动</th>
            <th>品牌</th>
            <th>报告统计</th>
            <th className="source-col">内容数据</th>
          </tr>
        </thead>
        <tbody>
          {records.map(record => {
            const isLongContent = record.content.length > 100;
            const isExpanded = expandedRecordIds.has(record.id);
            const typeTags = commentTypeTags(record);
            return (
              <tr
                key={record.id}
                className={selectedRecordId === record.id ? 'selected-row' : ''}
                onClick={() => onSelect(record.id)}
              >
                <td className="id-col">
                  {Object.values(record.labels).some(label => label.confirmed) ? (
                    <span className="manual-dot" title="本行包含人工确认标签" />
                  ) : (
                    <span className="empty-dot" />
                  )}
                  <strong>{tailId(record.id, 6)}</strong>
                  <small>{Object.values(record.labels).some(label => label.confirmed) ? '已确认' : '待确认'}</small>
                </td>
                <td>{record.platform}</td>
                <td className="sticky-col content-col">
                  <div className="comment-meta">
                    <strong>{record.author}</strong>
                    <span>{record.publish_time}</span>
                  </div>
                  <div className="comment-types">
                    {typeTags.map(tag => <em key={tag}>{tag}</em>)}
                  </div>
                  <p className={isLongContent && !isExpanded ? 'long-comment' : ''}>
                    <HighlightedText text={record.content} keywords={record.matched_keywords} />
                  </p>
                  {isLongContent && (
                    <button
                      type="button"
                      className="content-toggle"
                      onClick={event => {
                        event.stopPropagation();
                        toggleExpanded(record.id);
                      }}
                    >
                      {isExpanded ? '收起长文' : '展开长文'}
                    </button>
                  )}
                </td>
                <td>
                  <strong>{record.engagement.likes.toLocaleString()}</strong>
                  <small>点赞</small>
                  <small>{record.engagement.replies.toLocaleString()} 回复</small>
                </td>
                <LabelCell record={record} schema={schema} fieldKey="sentiment_polarity" onChange={onChange} />
                <LabelCell record={record} schema={schema} fieldKey="cognition" onChange={onChange} />
                <LabelCell record={record} schema={schema} fieldKey="sentiment_type" onChange={onChange} />
                <LabelCell record={record} schema={schema} fieldKey="action" onChange={onChange} />
                <td>
                  <BrandEditor record={record} brandOptions={brandOptions} onChange={onBrandsChange} />
                </td>
                <td>
                  <label className="report-check" onClick={event => event.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={record.report_candidate}
                      onChange={event => onReportCandidateChange(record, event.target.checked)}
                    />
                    <span>{record.report_candidate ? '纳入' : '排除'}</span>
                  </label>
                </td>
                <td className="source-col">
                  <strong>{record.source_content.id ? tailId(record.source_content.id, 4) : '-'}</strong>
                  {record.source_content.url && (
                    <a href={record.source_content.url} target="_blank" rel="noreferrer" onClick={event => event.stopPropagation()}>
                      内容链接
                    </a>
                  )}
                  <small>话题：{formatTopics(record.source_content.topics).join('、') || '-'}</small>
                  <small>发布者：{record.source_content.author ?? '-'}</small>
                  <small>发布时间：{record.source_content.publish_time ?? '-'}</small>
                  <small>评论 {record.source_content.comments.toLocaleString()} / 点赞 {record.source_content.likes.toLocaleString()} / 收藏 {record.source_content.favorites.toLocaleString()} / 分享 {record.source_content.shares.toLocaleString()}</small>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function commentTypeTags(record: DataRecord): string[] {
  const tags = new Set<string>();
  if (record.content.length > 100) tags.add('长评论');
  if (record.brands.length > 1) tags.add('提及竞品');
  if (record.content.includes('@')) tags.add('@他人');
  if (/[\u{1F300}-\u{1FAFF}]/u.test(record.content) || /^[\p{P}\p{S}\s]+$/u.test(record.content)) tags.add('符号表情');
  if (record.comment_type !== '普通内容' || tags.size === 0) tags.add(record.comment_type);
  if (tags.size === 0) tags.add('普通内容');
  return Array.from(tags);
}

function BrandEditor({
  record,
  brandOptions,
  onChange
}: {
  record: DataRecord;
  brandOptions: string[];
  onChange: (record: DataRecord, brands: string[]) => void;
}) {
  const [draft, setDraft] = React.useState('');
  const canAdd = record.brands.length < 5;

  const addBrand = (brand: string) => {
    const normalized = brand.trim();
    if (!normalized || record.brands.includes(normalized) || !canAdd) return;
    onChange(record, [...record.brands, normalized].slice(0, 5));
    setDraft('');
  };

  const removeBrand = (brand: string) => {
    onChange(record, record.brands.filter(item => item !== brand));
  };

  return (
    <div className="brand-editor" onClick={event => event.stopPropagation()}>
      <div className="brand-tags editable">
        {record.brands.slice(0, 5).map(brand => (
          <button type="button" key={brand} title="移除品牌" onClick={() => removeBrand(brand)}>
            <span>{brand}</span>
            <b>×</b>
          </button>
        ))}
      </div>
      <div className="brand-input-row">
        <input
          list={`brand-options-${record.id}`}
          value={draft}
          disabled={!canAdd}
          placeholder={canAdd ? '添加品牌' : '最多5个'}
          onChange={event => setDraft(event.target.value)}
          onKeyDown={event => {
            if (event.key === 'Enter') {
              event.preventDefault();
              addBrand(draft);
            }
          }}
          onBlur={() => addBrand(draft)}
        />
        <datalist id={`brand-options-${record.id}`}>
          {brandOptions.map(brand => <option key={brand} value={brand} />)}
        </datalist>
      </div>
      <small>{record.brands.length}/5</small>
    </div>
  );
}

function LabelCell({
  record,
  schema,
  fieldKey,
  onChange
}: {
  record: DataRecord;
  schema: LabelSchema;
  fieldKey: string;
  onChange: (record: DataRecord, field: LabelField, value: string) => void;
}) {
  const field = schema.fields.find(item => item.key === fieldKey);
  if (!field) return <td>-</td>;
  const label = record.labels[field.key];
  const options = filteredOptions(field, record);
  return (
    <td>
      <div className="cell-editor" title={labelTooltip(label, schema, field.key)}>
        {label?.confirmed && <span className="manual-dot" />}
        <select
          value={label?.final ?? ''}
          onClick={event => event.stopPropagation()}
          onChange={event => onChange(record, field, event.target.value)}
        >
          <option value="">未选择</option>
          {options.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
        <ChevronDown size={14} />
      </div>
      <small>自动：{optionLabel(schema, field.key, label?.auto)}</small>
    </td>
  );
}

function HighlightedText({ text, keywords }: { text: string; keywords: string[] }) {
  const safeKeywords = keywords.filter(Boolean).sort((a, b) => b.length - a.length);
  if (!safeKeywords.length) return <>{text}</>;
  const pattern = new RegExp(`(${safeKeywords.map(escapeRegExp).join('|')})`, 'g');
  return (
    <>
      {text.split(pattern).map((part, index) => (
        safeKeywords.includes(part) ? <mark key={`${part}-${index}`}>{part}</mark> : <React.Fragment key={`${part}-${index}`}>{part}</React.Fragment>
      ))}
    </>
  );
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function WorkbenchView({
  view,
  dashboard,
  onNavigate,
  onProjectSwitch,
  onProjectCreate,
  onProjectUpdate,
  onProjectDelete
}: {
  view: string;
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
  onProjectSwitch: (projectId: string) => void;
  onProjectCreate: (payload: ProjectPayload) => Promise<ProjectSummary>;
  onProjectUpdate: (projectId: string, payload: ProjectPayload) => Promise<ProjectSummary>;
  onProjectDelete: (projectId: string) => Promise<void>;
}) {
  if (view === 'projects') {
    return (
      <ProjectsView
        dashboard={dashboard}
        onNavigate={onNavigate}
        onProjectSwitch={onProjectSwitch}
        onProjectCreate={onProjectCreate}
        onProjectUpdate={onProjectUpdate}
        onProjectDelete={onProjectDelete}
      />
    );
  }
  if (view === 'import') return <ImportView dashboard={dashboard} onNavigate={onNavigate} />;
  if (view === 'auto') return <AutoLabelView dashboard={dashboard} onNavigate={onNavigate} />;
  if (view === 'learning') return <RuleLearningView dashboard={dashboard} />;
  if (view === 'report') return <ReportView dashboard={dashboard} />;
  if (view === 'users') return <UsersView dashboard={dashboard} />;
  return null;
}

function ProjectsView({
  dashboard,
  onNavigate,
  onProjectSwitch,
  onProjectCreate,
  onProjectUpdate,
  onProjectDelete
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
  onProjectSwitch: (projectId: string) => void;
  onProjectCreate: (payload: ProjectPayload) => Promise<ProjectSummary>;
  onProjectUpdate: (projectId: string, payload: ProjectPayload) => Promise<ProjectSummary>;
  onProjectDelete: (projectId: string) => Promise<void>;
}) {
  const activeProject = dashboard.active_project;
  const blankDraft: ProjectPayload = {
    name: '',
    client: '',
    brand: '',
    description: '',
    objective: '',
    platforms: activeProject.platforms.length ? activeProject.platforms : ['小红书', '抖音'],
    date_range: activeProject.date_range,
    delivery_due: activeProject.delivery_due,
    owner_id: dashboard.user.id,
    label_schema: activeProject.label_schema,
    rule_version: activeProject.rule_version,
    report_template: activeProject.report_template,
    export_pattern: activeProject.export_pattern || dashboard.export_presets[0]?.pattern || '{project}_{date}_{version}_{format}',
    priority: '中',
    status: '项目配置中'
  };
  const [projectStatusFilter, setProjectStatusFilter] = React.useState('全部');
  const [projectOwnerFilter, setProjectOwnerFilter] = React.useState('全部');
  const [projectSearch, setProjectSearch] = React.useState('');
  const [projectSort, setProjectSort] = React.useState('updated_desc');
  const [editingProjectId, setEditingProjectId] = React.useState<string | null>(null);
  const [draft, setDraft] = React.useState<ProjectPayload>(blankDraft);
  const [projectActionError, setProjectActionError] = React.useState<string | null>(null);
  const [projectSaving, setProjectSaving] = React.useState(false);
  const statusOptions = ['全部', ...Array.from(new Set(dashboard.projects.map(project => project.status)))];
  const reportTemplateOptions = Array.from(new Set([
    draft.report_template,
    ...dashboard.report_templates.map(template => template.name),
    '默认报告模板'
  ].filter(Boolean)));
  const ownerOptions = ['全部', ...dashboard.users.map(user => user.id)];
  const visibleProjects = dashboard.projects
    .filter(project => {
      const term = projectSearch.trim().toLowerCase();
      const searchable = [
        project.name,
        project.client,
        project.brand,
        project.description,
        project.objective,
        project.owner.name,
        project.status,
        project.platforms.join(' ')
      ].join(' ').toLowerCase();
      if (projectStatusFilter !== '全部' && project.status !== projectStatusFilter) return false;
      if (projectOwnerFilter !== '全部' && project.owner.id !== projectOwnerFilter) return false;
      if (term && !searchable.includes(term)) return false;
      return true;
    })
    .sort((left, right) => {
      if (projectSort === 'progress_desc') return right.progress - left.progress;
      if (projectSort === 'progress_asc') return left.progress - right.progress;
      if (projectSort === 'due_asc') return (left.delivery_due || '9999-99-99').localeCompare(right.delivery_due || '9999-99-99');
      if (projectSort === 'priority') return priorityRank(right.priority) - priorityRank(left.priority);
      return right.updated_at.localeCompare(left.updated_at);
    });
  const editingProject = dashboard.projects.find(project => project.id === editingProjectId) ?? null;
  const totalProjectRows = dashboard.projects.reduce((total, project) => total + project.total_count, 0);
  const totalConfirmedRows = dashboard.projects.reduce((total, project) => total + project.confirmed_count, 0);
  const highPriorityCount = dashboard.projects.filter(project => project.priority === '高').length;
  const dueSoonCount = dashboard.projects.filter(project => project.delivery_due && project.delivery_due <= '2026-06-10' && project.status !== '已交付').length;
  const resetProjectFilters = () => {
    setProjectSearch('');
    setProjectStatusFilter('全部');
    setProjectOwnerFilter('全部');
    setProjectSort('updated_desc');
  };

  const projectToPayload = (project: ProjectSummary): ProjectPayload => ({
    name: project.name,
    client: project.client,
    brand: project.brand,
    description: project.description,
    objective: project.objective,
    platforms: project.platforms,
    date_range: project.date_range,
    delivery_due: project.delivery_due,
    owner_id: project.owner.id,
    label_schema: project.label_schema,
    rule_version: project.rule_version,
    report_template: project.report_template,
    export_pattern: project.export_pattern,
    priority: project.priority,
    status: project.status
  });

  const changeDraft = (key: keyof ProjectPayload, value: string | string[]) => {
    setDraft(current => ({ ...current, [key]: value }));
  };

  const toggleDraftPlatform = (platform: string) => {
    setDraft(current => {
      const nextPlatforms = current.platforms.includes(platform)
        ? current.platforms.filter(item => item !== platform)
        : [...current.platforms, platform];
      return { ...current, platforms: nextPlatforms };
    });
  };

  const startCreate = () => {
    setEditingProjectId(null);
    setDraft(blankDraft);
    setProjectActionError(null);
  };

  const startEdit = (project: ProjectSummary) => {
    setEditingProjectId(project.id);
    setDraft(projectToPayload(project));
    setProjectActionError(null);
  };

  const copyProject = (project: ProjectSummary) => {
    setEditingProjectId(null);
    setDraft({
      ...projectToPayload(project),
      name: `${project.name} 副本`,
      status: '项目配置中'
    });
    setProjectActionError(null);
  };

  const submitProject = async () => {
    setProjectSaving(true);
    setProjectActionError(null);
    try {
      if (!draft.platforms.length) {
        throw new Error('至少选择一个数据平台');
      }
      if (editingProjectId) {
        await onProjectUpdate(editingProjectId, draft);
      } else {
        await onProjectCreate(draft);
      }
      setEditingProjectId(null);
      setDraft(blankDraft);
    } catch (err) {
      setProjectActionError(err instanceof Error ? err.message : '项目保存失败');
    } finally {
      setProjectSaving(false);
    }
  };

  const deleteProject = async (project: ProjectSummary) => {
    if (dashboard.projects.length <= 1) {
      setProjectActionError('至少需要保留一个项目');
      return;
    }
    if (!window.confirm(`确认删除「${project.name}」吗？这个操作会从项目列表移除它。`)) {
      return;
    }
    setProjectSaving(true);
    setProjectActionError(null);
    try {
      await onProjectDelete(project.id);
      if (editingProjectId === project.id) startCreate();
    } catch (err) {
      setProjectActionError(err instanceof Error ? err.message : '项目删除失败');
    } finally {
      setProjectSaving(false);
    }
  };

  return (
    <section className="workbench-view">
      <ViewHeader
        title="项目管理"
        copy="这里管理所有舆情项目。项目配置、切换、复制和删除都从项目列表进入。"
        action="新建项目"
        onAction={startCreate}
      />
      <div className="project-management-grid">
        <div className="data-table-card">
          <div className="table-card-head">
            <h3>项目列表</h3>
            <span>共有 {dashboard.projects.length.toLocaleString()} 个项目，当前显示 {visibleProjects.length.toLocaleString()} 个</span>
          </div>
          <div className="project-overview-strip">
            <StatBlock title="项目总数" value={dashboard.projects.length.toLocaleString()} detail={`${visibleProjects.length} 个符合筛选`} />
            <StatBlock title="总数据量" value={totalProjectRows.toLocaleString()} detail="所有项目累计行数" />
            <StatBlock title="确认总量" value={totalConfirmedRows.toLocaleString()} detail="人工确认累计" />
            <StatBlock title="高优先级" value={highPriorityCount.toLocaleString()} detail={`${dueSoonCount} 个近期交付`} />
          </div>
          <div className="project-list-toolbar">
            <div className="project-search-box">
              <Search size={15} />
              <input value={projectSearch} onChange={event => setProjectSearch(event.target.value)} placeholder="搜索项目、客户、品牌、负责人" />
            </div>
            <div className="project-filter-tabs">
              {statusOptions.map(status => (
                <button
                  key={status}
                  type="button"
                  className={projectStatusFilter === status ? 'active' : ''}
                  onClick={() => setProjectStatusFilter(status)}
                >
                  {status}
                </button>
              ))}
            </div>
            <div className="project-list-controls">
              <select value={projectOwnerFilter} onChange={event => setProjectOwnerFilter(event.target.value)}>
                {ownerOptions.map(ownerId => (
                  <option key={ownerId} value={ownerId}>
                    {ownerId === '全部' ? '全部负责人' : dashboard.users.find(user => user.id === ownerId)?.name ?? ownerId}
                  </option>
                ))}
              </select>
              <select value={projectSort} onChange={event => setProjectSort(event.target.value)}>
                <option value="updated_desc">最近更新</option>
                <option value="priority">优先级最高</option>
                <option value="due_asc">交付日最近</option>
                <option value="progress_desc">进度最高</option>
                <option value="progress_asc">进度最低</option>
              </select>
              <button type="button" className="secondary-action" onClick={resetProjectFilters}>重置筛选</button>
              <button type="button" className="primary-action" onClick={startCreate}>新建项目</button>
            </div>
          </div>
          <table className="simple-table">
            <thead>
              <tr><th>项目</th><th>客户/品牌</th><th>平台</th><th>负责人</th><th>交付/优先级</th><th>状态</th><th>进度</th><th>操作</th></tr>
            </thead>
            <tbody>
              {visibleProjects.length > 0 ? visibleProjects.map(project => (
                <tr key={project.id} className={project.id === activeProject.id ? 'active-row' : ''}>
                  <td><strong>{project.name}</strong><small>{project.created_at} 创建 / 更新 {project.updated_at}</small></td>
                  <td>{project.client} / {project.brand}<small>{project.label_schema}</small></td>
                  <td><div className="project-mini-tags">{project.platforms.map(platform => <span key={platform}>{platform}</span>)}</div></td>
                  <td>{project.owner.name}</td>
                  <td>{project.delivery_due || '待定'}<small>{project.priority}优先级</small></td>
                  <td><span className="status-pill">{project.status}</span></td>
                  <td>{project.progress}%</td>
                  <td>
                    <div className="project-row-actions">
                      <button type="button" className="tiny-action" onClick={() => onProjectSwitch(project.id)}>打开</button>
                      <button type="button" className="tiny-action" onClick={() => startEdit(project)}>配置</button>
                      <button type="button" className="tiny-action" onClick={() => onNavigate('labeling')}>标注</button>
                      <button type="button" className="tiny-action" onClick={() => copyProject(project)}>复制</button>
                      <button
                        type="button"
                        className="tiny-action danger-action"
                        disabled={dashboard.projects.length <= 1 || projectSaving}
                        onClick={() => deleteProject(project)}
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={8}>
                    <div className="project-empty-state">
                      <strong>没有符合条件的项目</strong>
                      <span>可以重置筛选查看全部项目，或直接新建一个项目。</span>
                      <div>
                        <button type="button" className="secondary-action" onClick={resetProjectFilters}>重置筛选</button>
                        <button type="button" className="primary-action" onClick={startCreate}>新建项目</button>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="new-project-panel">
          <h3>{editingProject ? '编辑项目' : '新建项目'}</h3>
          <label><span>项目名称</span><input value={draft.name} onChange={event => changeDraft('name', event.target.value)} placeholder="例如：某品牌舆情分析项目" /></label>
          <label><span>客户</span><input value={draft.client} onChange={event => changeDraft('client', event.target.value)} placeholder="客户名" /></label>
          <label><span>品牌</span><input value={draft.brand} onChange={event => changeDraft('brand', event.target.value)} placeholder="品牌或多品牌" /></label>
          <label><span>项目说明</span><textarea value={draft.description} onChange={event => changeDraft('description', event.target.value)} placeholder="这次项目的背景、范围、需要注意的问题" /></label>
          <label><span>分析目标</span><textarea value={draft.objective} onChange={event => changeDraft('objective', event.target.value)} placeholder="例如：识别正负向、竞品提及、风险行动倾向" /></label>
          <div className="platform-check-grid">
            <span>数据平台</span>
            <div>
              {projectPlatformOptions.map(platform => (
                <label key={platform}>
                  <input type="checkbox" checked={draft.platforms.includes(platform)} onChange={() => toggleDraftPlatform(platform)} />
                  <span>{platform}</span>
                </label>
              ))}
            </div>
          </div>
          <label><span>数据周期</span><input value={draft.date_range} onChange={event => changeDraft('date_range', event.target.value)} placeholder="YYYY-MM-DD 至 YYYY-MM-DD" /></label>
          <label><span>交付日期</span><input type="date" value={draft.delivery_due} onChange={event => changeDraft('delivery_due', event.target.value)} /></label>
          <label>
            <span>优先级</span>
            <select value={draft.priority} onChange={event => changeDraft('priority', event.target.value as ProjectPayload['priority'])}>
              <option>高</option>
              <option>中</option>
              <option>低</option>
            </select>
          </label>
          <label>
            <span>负责人</span>
            <select value={draft.owner_id} onChange={event => changeDraft('owner_id', event.target.value)}>
              {dashboard.users.map(user => <option key={user.id} value={user.id}>{user.name} / {user.role}</option>)}
            </select>
          </label>
          <label>
            <span>标签体系</span>
            <select value={draft.label_schema} onChange={event => changeDraft('label_schema', event.target.value)}>
              <option>A2 三层标签体系</option>
              <option>风险等级 + 议题类型</option>
              <option>正负向 + 议题 + 品牌识别</option>
            </select>
          </label>
          <label><span>规则版本</span><input value={draft.rule_version} onChange={event => changeDraft('rule_version', event.target.value)} placeholder="例如：v1.0" /></label>
          <label>
            <span>报告模板</span>
            <select value={draft.report_template} onChange={event => changeDraft('report_template', event.target.value)}>
              {reportTemplateOptions.map(templateName => <option key={templateName} value={templateName}>{templateName}</option>)}
            </select>
          </label>
          <label><span>导出命名</span><input value={draft.export_pattern} onChange={event => changeDraft('export_pattern', event.target.value)} placeholder="{project}_{date}_{version}_{format}" /></label>
          <label>
            <span>状态</span>
            <select value={draft.status} onChange={event => changeDraft('status', event.target.value)}>
              <option>项目配置中</option>
              <option>待导入数据</option>
              <option>标注中</option>
              <option>报告待确认</option>
              <option>已交付</option>
            </select>
          </label>
          {projectActionError && <div className="form-error">{projectActionError}</div>}
          <div className="project-form-actions">
            <button type="button" className="primary-action" disabled={projectSaving} onClick={submitProject}>
              {projectSaving ? '保存中...' : editingProject ? '保存项目' : '创建项目'}
            </button>
            {editingProject && <button type="button" className="secondary-action" onClick={startCreate}>取消编辑</button>}
          </div>
        </div>
      </div>
      <div className="entity-grid">
        {dashboard.projects.map(project => (
          <button key={project.id} type="button" className={`entity-card ${project.id === activeProject.id ? 'active-card' : ''}`} onClick={() => onProjectSwitch(project.id)}>
            <div className="entity-head">
              <ShieldCheck size={20} />
              <span>{project.status}</span>
            </div>
            <strong>{project.name}</strong>
            <p>{project.client} / {project.brand} / {project.label_schema}</p>
            <div className="project-mini-tags">{project.platforms.map(platform => <span key={platform}>{platform}</span>)}</div>
            <div className="progress-track"><span style={{ width: `${project.progress}%` }} /></div>
            <small>{project.confirmed_count.toLocaleString()} / {project.total_count.toLocaleString()} 已确认 / {project.delivery_due || '交付待定'}</small>
          </button>
        ))}
      </div>
    </section>
  );
}

function ImportView({
  dashboard,
  onNavigate
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
}) {
  const [activeStage, setActiveStage] = React.useState<ImportStage>('upload');
  const [selectedFileName, setSelectedFileName] = React.useState(dashboard.imports[0]?.filename ?? '');
  const [importPreview, setImportPreview] = React.useState<ImportPreviewResponse | null>(null);
  const [importPreviewError, setImportPreviewError] = React.useState<string | null>(null);
  const [importPreviewing, setImportPreviewing] = React.useState(false);
  const activeImport = dashboard.imports[0];
  const previewInvalidRows = importPreview?.quality_issues
    .filter(issue => issue.action === '排除' || issue.action === '合并')
    .reduce((total, issue) => total + issue.count, 0) ?? activeImport?.invalid_rows ?? 0;
  const previewTotalRows = importPreview?.total_rows ?? activeImport?.total_rows ?? 0;
  const previewUsableRows = Math.max(previewTotalRows - previewInvalidRows, 0);
  const invalidRate = previewTotalRows ? Math.round((previewInvalidRows / previewTotalRows) * 1000) / 10 : 0;

  const handleImportFile = async (file: File | undefined) => {
    if (!file) return;
    setSelectedFileName(file.name);
    setImportPreviewing(true);
    setImportPreviewError(null);
    try {
      const preview = await previewImportFile(file);
      setImportPreview(preview);
      setActiveStage('mapping');
    } catch (err) {
      setImportPreviewError(err instanceof Error ? err.message : '导入预览失败');
    } finally {
      setImportPreviewing(false);
    }
  };

  return (
    <section className="workbench-view">
      <ViewHeader
        title="数据导入与字段映射"
        copy="支持按项目导入 Excel，先做字段映射、数据清洗和无效数据识别，再进入规则学习与自动打标。"
        action="导入 Excel"
      />
      <div className="import-stage-nav" aria-label="数据导入流程">
        {[
          ['upload', '上传文件', '选择 Excel 并确认项目'],
          ['mapping', '字段映射', '匹配评论和内容字段'],
          ['cleaning', '清洗校验', '识别无效与重复数据'],
          ['preview', '数据预览', '抽样确认导入结果'],
          ['history', '导入历史', '查看版本和状态']
        ].map(([stage, title, copy], index) => (
          <button
            key={stage}
            type="button"
            className={activeStage === stage ? 'active' : ''}
            onClick={() => setActiveStage(stage as ImportStage)}
          >
            <span>{index + 1}</span>
            <strong>{title}</strong>
            <small>{copy}</small>
          </button>
        ))}
      </div>
      <div className="import-status-strip">
        <StatBlock title="当前文件" value={selectedFileName || '未选择'} detail={importPreview ? `${importPreview.total_rows.toLocaleString()} 行 / ${importPreview.inferred_platform}` : activeImport ? `${activeImport.total_rows.toLocaleString()} 行 / ${activeImport.status}` : '等待上传'} />
        <StatBlock title="预计有效" value={importPreview ? previewUsableRows.toLocaleString() : activeImport ? activeImport.valid_rows.toLocaleString() : '0'} detail="通过清洗后进入规则学习" />
        <StatBlock title="问题命中" value={`${previewInvalidRows.toLocaleString()} / ${invalidRate}%`} detail="可在清洗校验里查看原因" />
        <StatBlock title="批量上限" value="100,000" detail="单次导入建议上限" />
      </div>
      {importPreviewError && <div className="import-error">{importPreviewError}</div>}
      <div className="import-grid">
        <label className="upload-zone">
          <FileSpreadsheet size={26} />
          <strong>拖拽或选择 Excel 文件</strong>
          <span>支持 10 万行以内批量导入，字段映射确认后进入清洗队列。</span>
          <input
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={event => handleImportFile(event.target.files?.[0])}
          />
          <em>{importPreviewing ? '正在解析文件...' : selectedFileName || '尚未选择文件'}</em>
        </label>
        <div className="mapping-panel">
          <h3>字段映射预览</h3>
          <div className="mapping-list">
            {(importPreview?.mappings ?? importFieldMappings()).slice(0, 7).map(mapping => (
              <button key={mapping.source} type="button" onClick={() => setActiveStage('mapping')}>
                <span>{mapping.source}</span>
                <strong>{mapping.target}</strong>
              </button>
            ))}
          </div>
        </div>
        <div className="quality-panel">
          <h3>导入质量检查</h3>
          <div className="quality-grid">
            <StatBlock title="重复内容" value="自动识别" detail="按评论ID、内容ID、正文组合去重" />
            <StatBlock title="无效数据" value="可配置" detail="空内容、乱码、纯符号、纯@等规则" />
            <StatBlock title="字段缺失" value="允许为空" detail="内容ID、链接、话题等保留但非必填" />
          </div>
        </div>
      </div>
      {activeStage === 'upload' && <ImportUploadDetails selectedFileName={selectedFileName} onNext={() => setActiveStage('mapping')} />}
      {activeStage === 'mapping' && <ImportMappingPanel preview={importPreview} />}
      {activeStage === 'cleaning' && <ImportCleaningPanel activeImport={activeImport} preview={importPreview} />}
      {activeStage === 'preview' && <DataPreviewPanel dashboard={dashboard} preview={importPreview} />}
      {activeStage === 'history' && <ImportHistoryPanel dashboard={dashboard} onNavigate={onNavigate} />}
      <div className="import-next-strip">
        <span>确认字段映射和清洗结果后，可以先进入规则学习，再运行自动打标；人工确认过的数据后续不会被覆盖。</span>
        <button type="button" className="primary-action" onClick={() => onNavigate('learning')}>进入规则学习</button>
      </div>
    </section>
  );
}

function AutoLabelView({
  dashboard,
  onNavigate
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
}) {
  const protectedCount = dashboard.records.filter(record => Object.values(record.labels).some(label => label.confirmed)).length;
  return (
    <section className="workbench-view">
      <ViewHeader
        title="自动打标"
        copy="按当前规则版本识别品牌、竞品、情绪、认知和行动标签。人工确认过的标签不会被规则重跑覆盖。"
        action="运行自动打标"
      />
      <div className="auto-console">
        <div className="run-panel">
          <Sparkles size={24} />
          <h3>规则重跑范围</h3>
          <p>本轮会处理未确认标签，保留所有人工确认黄点。运行后可直接进入人工标注页复核冲突项。</p>
          <div className="run-stats">
            <StatBlock title="待处理样本" value={dashboard.records.length.toLocaleString()} detail="当前预览数据" />
            <StatBlock title="人工保护" value={protectedCount.toLocaleString()} detail="不会被自动规则覆盖" />
            <StatBlock title="规则版本" value={dashboard.active_project.rule_version} detail="项目当前版本" />
          </div>
          <button type="button" className="primary-action" onClick={() => onNavigate('labeling')}>运行并查看结果</button>
        </div>
        <div className="auto-samples">
          <h3>最近样本预判</h3>
          {dashboard.records.map(record => (
            <button key={record.id} type="button" onClick={() => onNavigate('labeling')}>
              <strong>{record.content}</strong>
              <span>{optionLabel(dashboard.label_schema, 'sentiment_polarity', record.labels.sentiment_polarity?.final)} / {record.brands.join('、') || '未识别品牌'}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="entity-grid">
        {dashboard.rule_sets.map(ruleSet => (
          <button key={ruleSet.id} type="button" className="entity-card" onClick={() => onNavigate('learning')}>
            <div className="entity-head">
              <Sparkles size={20} />
              <span>{ruleSet.version}</span>
            </div>
            <strong>{ruleSet.name}</strong>
            <p>{ruleSet.layer} / {ruleSet.rule_count} 条规则</p>
            <small>更新于 {ruleSet.last_updated}</small>
          </button>
        ))}
      </div>
      <BrandRuleList dashboard={dashboard} />
      <RuleRunChecklist dashboard={dashboard} />
    </section>
  );
}

function RuleLearningView({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <section className="workbench-view">
      <ViewHeader
        title="规则学习"
        copy="系统从人工修改里识别规则偏差，把可解释的关键词、优先级和样本证据整理成人工可确认的建议。"
        action="应用已选建议"
      />
      <div className="learning-layout">
        <div className="suggestion-board">
          {dashboard.suggestions.map(suggestion => (
            <article key={suggestion.id} className="suggestion-card warning-card">
              <div className="entity-head">
                <Lightbulb size={20} />
                <span>{suggestion.evidence_count} 条证据</span>
              </div>
              <strong>{suggestion.title}</strong>
              <p>{suggestion.summary}</p>
              <div className="keyword-row">
                {suggestion.keywords.map(keyword => <span key={keyword}>{keyword}</span>)}
              </div>
              <div className="suggestion-actions">
                <button type="button">采纳为规则</button>
                <button type="button">查看样本</button>
                <button type="button">暂不处理</button>
              </div>
            </article>
          ))}
        </div>
        <aside className="rule-editor-panel">
          <h3>规则编辑器</h3>
          {dashboard.rule_sets.map(ruleSet => (
            <button key={ruleSet.id} type="button">
              <strong>{ruleSet.name}</strong>
              <span>{ruleSet.layer} / {ruleSet.rule_count} 条 / {ruleSet.version}</span>
            </button>
          ))}
        </aside>
      </div>
      <BrandRuleList dashboard={dashboard} />
      <RuleEvidenceTable dashboard={dashboard} />
    </section>
  );
}

function ReportView({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <section className="workbench-view">
      <ViewHeader
        title="在线报告"
        copy="报告由可编辑块组成，分析师在线确认内容、图表、重点样本和结论后，再导出 Word、PDF 或 PPT。"
        action="复制模板"
      />
      <div className="report-layout">
        <div className="report-canvas">
          <div className="report-title-row">
            <div>
              <span className="status-pill">{dashboard.report.version}</span>
              <h2>{dashboard.report.title}</h2>
            </div>
            <div className="report-export-actions">
              <button type="button">导出 Word</button>
              <button type="button">导出 PDF</button>
              <button type="button">导出 PPT</button>
            </div>
          </div>
          {dashboard.report.blocks.map(block => (
            <article key={block.id} className="report-block">
              <span>{block.block_type}</span>
              <strong>{block.title}</strong>
              <p>{block.content}</p>
              <textarea defaultValue={block.content} />
            </article>
          ))}
          <button type="button" className="add-report-block">添加报告块</button>
        </div>
        <aside className="report-side">
          <h3>模板与导出</h3>
          {dashboard.report_templates.map(template => (
            <button key={template.id} type="button">
              <strong>{template.name}</strong>
              <p>{template.version} / {template.sections.length} 个章节</p>
            </button>
          ))}
          {dashboard.export_presets.map(preset => (
            <button key={preset.id} type="button">
              <strong>{preset.name}</strong>
              <code>{preset.pattern}</code>
            </button>
          ))}
        </aside>
      </div>
      <ReportOpsPanel dashboard={dashboard} />
    </section>
  );
}

function UsersView({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <section className="workbench-view">
      <ViewHeader
        title="用户权限"
        copy="用户、角色和权限需要支持增删改查。人工确认记录会保留确认人和确认时间，后续规则重跑不覆盖。"
        action="邀请用户"
      />
      <div className="permission-layout">
        <div className="role-panel">
          {['项目管理员', '分析师', '标注员', '客户查看'].map((role, index) => (
            <button key={role} type="button" className={index === 0 ? 'active' : ''}>
              <strong>{role}</strong>
              <span>{index === 0 ? '全量权限' : index === 1 ? '规则与报告' : index === 2 ? '人工标注' : '只读报告'}</span>
            </button>
          ))}
        </div>
        <div className="permission-matrix">
          <h3>权限矩阵</h3>
          {['项目配置', '数据导入', '规则学习', '自动打标', '人工确认', '报告导出', '用户管理'].map((permission, index) => (
            <label key={permission}>
              <span>{permission}</span>
              <input type="checkbox" defaultChecked={index < 6} />
            </label>
          ))}
        </div>
      </div>
      <div className="entity-grid user-grid">
        {dashboard.users.map(user => (
          <button key={user.id} type="button" className="entity-card">
            <div className="large-avatar">{user.avatar}</div>
            <strong>{user.name}</strong>
            <p>{user.role}</p>
            <span className="status-pill">{user.status}</span>
          </button>
        ))}
      </div>
      <AuditTrail dashboard={dashboard} />
    </section>
  );
}

function ImportUploadDetails({
  selectedFileName,
  onNext
}: {
  selectedFileName: string;
  onNext: () => void;
}) {
  return (
    <div className="import-detail-grid">
      <div className="import-card">
        <h3>上传设置</h3>
        <label><span>目标项目</span><select defaultValue="A2 舆情分析项目"><option>A2 舆情分析项目</option><option>母婴品牌风险监测</option></select></label>
        <label><span>数据来源</span><select defaultValue="混合平台"><option>混合平台</option><option>小红书</option><option>抖音</option><option>微博</option></select></label>
        <label><span>导入模式</span><select defaultValue="replace"><option value="append">追加到当前项目</option><option value="replace">替换未确认数据</option><option value="snapshot">创建新数据版本</option></select></label>
      </div>
      <div className="import-card">
        <h3>文件校验</h3>
        <div className="file-check-list">
          {[
            ['文件类型', selectedFileName ? '已选择' : '等待选择'],
            ['行数上限', '100,000 行以内'],
            ['表头识别', '自动匹配常见字段'],
            ['历史版本', '保留导入记录和导出记录']
          ].map(([label, value]) => (
            <div key={label}><span>{label}</span><strong>{value}</strong></div>
          ))}
        </div>
        <button type="button" className="primary-action" onClick={onNext}>确认并进入字段映射</button>
      </div>
    </div>
  );
}

function ImportMappingPanel({ preview }: { preview: ImportPreviewResponse | null }) {
  const mappings = preview?.mappings ?? importFieldMappings();
  return (
    <div className="data-table-card">
      <div className="table-card-head">
        <h3>字段映射工作台</h3>
        <span>{preview ? `${preview.filename} / ${preview.sheet_name}` : '必填字段需要确认，非必填字段会保留为空值继续导入'}</span>
      </div>
      <table className="simple-table mapping-table">
        <thead>
          <tr><th>Excel 字段</th><th>系统字段</th><th>是否必填</th><th>识别置信度</th><th>样例</th><th>操作</th></tr>
        </thead>
        <tbody>
          {mappings.map(mapping => (
            <tr key={mapping.source}>
              <td>{mapping.source}</td>
              <td><select defaultValue={mapping.target}><option>{mapping.target}</option><option>忽略该字段</option></select></td>
              <td>{mapping.required ? <span className="status-pill">必填</span> : '可为空'}</td>
              <td><div className="confidence-bar"><span style={{ width: `${mapping.confidence}%` }} /></div><small>{mapping.confidence}%</small></td>
              <td>{mapping.sample}</td>
              <td><button type="button" className="tiny-action">确认</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ImportCleaningPanel({
  activeImport,
  preview
}: {
  activeImport?: DashboardResponse['imports'][number];
  preview: ImportPreviewResponse | null;
}) {
  const issueRows = preview?.quality_issues ?? [
    { rule: '空内容', count: 428, description: '正文为空或只包含空格', action: '排除', enabled: true },
    { rule: '纯符号表情', count: 312, description: '仅包含标点、emoji 或无语义符号', action: '排除', enabled: true },
    { rule: '纯@他人', count: 184, description: '评论只是在 @ 账号，无实际观点', action: '排除', enabled: true },
    { rule: '乱码内容', count: 96, description: '异常编码、重复不可读字符', action: '排除', enabled: true },
    { rule: '重复评论', count: 1880, description: '评论ID或内容组合重复', action: '合并', enabled: true },
    { rule: '缺失平台', count: 23, description: '平台为空但内容有效', action: '保留并待补', enabled: false }
  ];
  return (
    <div className="cleaning-workbench">
      <div className="ops-grid">
        <StatBlock title="总行数" value={activeImport ? activeImport.total_rows.toLocaleString() : '0'} detail="Excel 原始行数" />
        <StatBlock title="有效行" value={activeImport ? activeImport.valid_rows.toLocaleString() : '0'} detail="将进入规则学习与自动打标" />
        <StatBlock title="无效行" value={activeImport ? activeImport.invalid_rows.toLocaleString() : '0'} detail="可导出问题清单" />
        <StatBlock title="处理策略" value="规则可编辑" detail="保留非必填字段空值" />
      </div>
      <div className="data-table-card">
        <div className="table-card-head">
          <h3>无效数据原因</h3>
          <span>这里会决定哪些数据被排除、合并或保留待补</span>
        </div>
        <table className="simple-table">
          <thead>
            <tr><th>规则</th><th>命中数量</th><th>说明</th><th>处理方式</th><th>启用</th></tr>
          </thead>
          <tbody>
            {issueRows.map(issue => (
              <tr key={issue.rule}>
                <td>{issue.rule}</td>
                <td>{issue.count.toLocaleString()}</td>
                <td>{issue.description}</td>
                <td><select defaultValue={issue.action}><option>排除</option><option>合并</option><option>保留并待补</option><option>自动补平台</option></select></td>
                <td><input type="checkbox" defaultChecked={issue.enabled} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ImportHistoryPanel({
  dashboard,
  onNavigate
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
}) {
  return (
    <div className="data-table-card">
      <div className="table-card-head">
        <h3>导入历史</h3>
        <span>每次导入都保留文件、负责人、状态和版本入口</span>
      </div>
      <table className="simple-table">
        <thead>
          <tr><th>文件名</th><th>状态</th><th>总行数</th><th>有效</th><th>无效</th><th>负责人</th><th>时间</th><th>下一步</th></tr>
        </thead>
        <tbody>
          {dashboard.imports.map(job => (
            <tr key={job.id}>
              <td>{job.filename}</td>
              <td><span className="status-pill">{job.status}</span></td>
              <td>{job.total_rows.toLocaleString()}</td>
              <td>{job.valid_rows.toLocaleString()}</td>
              <td>{job.invalid_rows.toLocaleString()}</td>
              <td>{job.owner.name}</td>
              <td>{job.created_at}</td>
              <td><button type="button" className="tiny-action" onClick={() => onNavigate('auto')}>自动打标</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DataPreviewPanel({
  dashboard,
  preview
}: {
  dashboard: DashboardResponse;
  preview?: ImportPreviewResponse | null;
}) {
  const previewRows = preview?.samples ?? [];
  return (
    <div className="preview-layout">
      <div className="data-table-card">
        <div className="table-card-head">
          <h3>导入数据预览</h3>
          <span>按当前字段映射抽取前 3 条样本</span>
        </div>
        <table className="simple-table">
          <thead>
            <tr><th>评论ID</th><th>平台</th><th>评论内容</th><th>内容链接</th><th>品牌</th><th>报告统计</th></tr>
          </thead>
          <tbody>
            {previewRows.length > 0 ? previewRows.map((row, index) => (
              <tr key={`${row.comment_id}-${index}`}>
                <td>{tailId(row.comment_id ?? '', 6)}</td>
                <td>{row.platform || preview?.inferred_platform || '-'}</td>
                <td>{row.content}</td>
                <td>{row['source_content.url'] ? '已生成' : '-'}</td>
                <td>{detectBrands(row.content ?? '').join('、') || '-'}</td>
                <td>待确认</td>
              </tr>
            )) : dashboard.records.map(record => (
              <tr key={record.id}>
                <td>{tailId(record.id, 6)}</td>
                <td>{record.platform}</td>
                <td>{record.content}</td>
                <td>{record.source_content.url ? '已识别' : '-'}</td>
                <td>{record.brands.join('、') || '-'}</td>
                <td>{record.report_candidate ? '纳入' : '排除'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="cleaning-panel">
        <h3>清洗规则配置</h3>
        {(preview?.quality_issues.map(issue => issue.rule) ?? ['空内容', '纯符号表情', '纯@他人', '乱码内容', '重复评论', '缺失平台']).map((rule, index) => (
          <label key={rule}>
            <span>{rule}</span>
            <input type="checkbox" defaultChecked={preview?.quality_issues[index]?.enabled ?? index < 5} />
          </label>
        ))}
      </div>
    </div>
  );
}

function RuleRunChecklist({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <div className="ops-grid">
      {[
        ['品牌识别', `${dashboard.brand_rules.length} 个品牌规则`, '识别本品、竞品、别名和错字输入'],
        ['标签保护', '人工确认优先', '规则重跑不会覆盖人工黄点'],
        ['冲突复核', '自动生成队列', '自动标签和人工标签不一致时进入复核'],
        ['报告候选', '复选框控制', '只有纳入样本进入报告统计']
      ].map(([title, value, detail]) => (
        <StatBlock key={title} title={title} value={value} detail={detail} />
      ))}
    </div>
  );
}

function RuleEvidenceTable({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <div className="data-table-card">
      <div className="table-card-head">
        <h3>规则学习证据样本</h3>
        <span>展示人工修改前后的差异，供采纳规则前复核</span>
      </div>
      <table className="simple-table">
        <thead>
          <tr><th>样本</th><th>自动判断</th><th>人工确认</th><th>命中关键词</th><th>建议动作</th></tr>
        </thead>
        <tbody>
          {dashboard.records.filter(record => Object.values(record.labels).some(label => label.previous_value)).map(record => (
            <tr key={record.id}>
              <td>{record.content}</td>
              <td>{optionLabel(dashboard.label_schema, 'sentiment_type', record.labels.sentiment_type?.previous_value)}</td>
              <td>{optionLabel(dashboard.label_schema, 'sentiment_type', record.labels.sentiment_type?.final)}</td>
              <td>{record.matched_keywords.join('、')}</td>
              <td><span className="status-pill">建议提高权重</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ReportOpsPanel({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <div className="report-ops-grid">
      <div className="data-table-card">
        <div className="table-card-head">
          <h3>导出记录</h3>
          <span>同一项目可保留多版本文件</span>
        </div>
        <table className="simple-table">
          <thead>
            <tr><th>文件名</th><th>格式</th><th>版本</th><th>状态</th><th>大小</th><th>负责人</th><th>时间</th></tr>
          </thead>
          <tbody>
            {dashboard.export_records.map(record => (
              <tr key={record.id}>
                <td>{record.filename}</td>
                <td>{record.format}</td>
                <td>{record.report_version}</td>
                <td><span className="status-pill">{record.status}</span></td>
                <td>{record.size}</td>
                <td>{record.owner.name}</td>
                <td>{record.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="report-checklist">
        <h3>发布前检查</h3>
        {['报告文字已确认', '图表口径已确认', '重点样本已纳入', '导出命名已选择', 'Word / PDF / PPT 均可生成'].map((item, index) => (
          <label key={item}>
            <span>{item}</span>
            <input type="checkbox" defaultChecked={index < 3} />
          </label>
        ))}
      </div>
    </div>
  );
}

function AuditTrail({ dashboard }: { dashboard: DashboardResponse }) {
  const rows = dashboard.records
    .flatMap(record => Object.values(record.labels).filter(label => label.confirmed && label.confirmed_by).map(label => ({
      record,
      label
    })))
    .slice(0, 6);
  return (
    <div className="data-table-card">
      <div className="table-card-head">
        <h3>最近人工确认记录</h3>
        <span>用于追踪是谁在什么时候修改了标签</span>
      </div>
      <table className="simple-table">
        <thead>
          <tr><th>评论ID</th><th>用户</th><th>角色</th><th>时间</th><th>修改</th></tr>
        </thead>
        <tbody>
          {rows.map(({ record, label }, index) => (
            <tr key={`${record.id}-${index}`}>
              <td>{tailId(record.id, 6)}</td>
              <td>{label.confirmed_by?.name}</td>
              <td>{label.confirmed_by?.role}</td>
              <td>{label.confirmed_at}</td>
              <td>{label.previous_value ?? '自动'} → {label.final ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BrandRuleList({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <div className="brand-rule-list">
      <h3>品牌与竞品识别规则</h3>
      <div className="data-table-card">
        <table className="simple-table">
          <thead>
            <tr><th>品牌</th><th>类型</th><th>别名</th><th>主力产品</th><th>口语/错字</th></tr>
          </thead>
          <tbody>
            {dashboard.brand_rules.map(rule => (
              <tr key={rule.id}>
                <td><strong>{rule.brand}</strong></td>
                <td>{rule.competitor ? '竞品' : '本品'}</td>
                <td>{rule.aliases.join('、')}</td>
                <td>{rule.products.join('、')}</td>
                <td>{rule.typo_variants.join('、')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ViewHeader({
  title,
  copy,
  action,
  onAction
}: {
  title: string;
  copy: string;
  action: string;
  onAction?: () => void;
}) {
  return (
    <div className="view-header">
      <div>
        <h2>{title}</h2>
        <p>{copy}</p>
      </div>
      <button type="button" onClick={onAction}>{action}</button>
    </div>
  );
}

function applyAdvancedFilters(records: DataRecord[], filters: AdvancedFilters): DataRecord[] {
  const minLikes = parseNumberFilter(filters.minLikes);
  const minReplies = parseNumberFilter(filters.minReplies);
  return records.filter(record => {
    if (filters.platform && record.platform !== filters.platform) return false;
    if (filters.commentType && !commentTypeTags(record).includes(filters.commentType)) return false;
    if (minLikes !== null && record.engagement.likes < minLikes) return false;
    if (minReplies !== null && record.engagement.replies < minReplies) return false;
    if (filters.sentimentPolarity && record.labels.sentiment_polarity?.final !== filters.sentimentPolarity) return false;
    if (filters.cognition && record.labels.cognition?.final !== filters.cognition) return false;
    if (filters.sentimentType && record.labels.sentiment_type?.final !== filters.sentimentType) return false;
    if (filters.action && record.labels.action?.final !== filters.action) return false;
    if (filters.brand && !record.brands.includes(filters.brand)) return false;
    if (filters.reportStatus === 'included' && !record.report_candidate) return false;
    if (filters.reportStatus === 'excluded' && record.report_candidate) return false;
    return true;
  });
}

function sortRecords(records: DataRecord[], sortKey: SortKey, direction: SortDirection): DataRecord[] {
  if (sortKey === 'none') return records;
  const factor = direction === 'desc' ? -1 : 1;
  return [...records].sort((a, b) => {
    const left = sortValue(a, sortKey);
    const right = sortValue(b, sortKey);
    if (left === right) return a.id.localeCompare(b.id);
    return left > right ? factor : -factor;
  });
}

function sortValue(record: DataRecord, sortKey: SortKey): number {
  if (sortKey === 'comment_likes') return record.engagement.likes;
  if (sortKey === 'comment_replies') return record.engagement.replies;
  if (sortKey === 'comment_total') return record.engagement.likes + record.engagement.replies;
  if (sortKey === 'comment_publish_time') return parseDateValue(record.publish_time);
  if (sortKey === 'source_publish_time') return parseDateValue(record.source_content.publish_time);
  if (sortKey === 'source_comments') return record.source_content.comments;
  if (sortKey === 'source_likes') return record.source_content.likes;
  if (sortKey === 'source_favorites') return record.source_content.favorites;
  if (sortKey === 'source_shares') return record.source_content.shares;
  return 0;
}

function buildTableStats(records: DataRecord[], schema: LabelSchema) {
  const sentiment = countLabels(records, schema, 'sentiment_polarity');
  const cognition = countLabels(records, schema, 'cognition');
  const emotion = countLabels(records, schema, 'sentiment_type');
  const action = countLabels(records, schema, 'action');
  const reportIncluded = records.filter(record => record.report_candidate).length;
  return {
    total: records.length,
    reportIncluded,
    reportExcluded: records.length - reportIncluded,
    topSentiment: topCount(sentiment),
    topCognition: topCount(cognition),
    topEmotion: topCount(emotion),
    topAction: topCount(action),
    sentimentSummary: summarizeCounts(sentiment),
    cognitionSummary: summarizeCounts(cognition),
    emotionSummary: summarizeCounts(emotion),
    actionSummary: summarizeCounts(action)
  };
}

function countLabels(records: DataRecord[], schema: LabelSchema, fieldKey: string): Record<string, number> {
  return records.reduce<Record<string, number>>((counts, record) => {
    const label = optionLabel(schema, fieldKey, record.labels[fieldKey]?.final);
    counts[label] = (counts[label] ?? 0) + 1;
    return counts;
  }, {});
}

function topCount(counts: Record<string, number>): string {
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  return top ? `${top[0]} ${top[1]}` : '无数据';
}

function summarizeCounts(counts: Record<string, number>): string {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return entries.length ? entries.map(([label, count]) => `${label} ${count}`).join(' / ') : '无数据';
}

function parseNumberFilter(value: string): number | null {
  const normalized = Number(value);
  return Number.isFinite(normalized) && normalized >= 0 ? normalized : null;
}

function parseDateValue(value?: string | null): number {
  if (!value) return 0;
  const parsed = Date.parse(value.replace(/-/g, '/'));
  return Number.isFinite(parsed) ? parsed : 0;
}

function uniqueOptions(values: string[]): string[] {
  return Array.from(new Set(values.map(value => value.trim()).filter(Boolean)));
}

function tailId(value: string, length: number): string {
  const compact = value.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '');
  return compact.length <= length ? compact : compact.slice(-length);
}

function formatTopics(topics: string[]): string[] {
  return topics.slice(0, 3).map(topic => {
    const normalized = topic.trim();
    return normalized.startsWith('#') ? normalized : `#${normalized}`;
  });
}

function detectBrands(content: string): string[] {
  const terms = ['a2', '爱他美', '飞鹤', '金领冠', '合生元', '美素佳儿', '完达山', '君乐宝', '贝因美', '伊利', '圣元', '蒙牛', '澳优', '雅士利'];
  const lower = content.toLowerCase();
  return terms.filter(term => lower.includes(term.toLowerCase())).slice(0, 5);
}

function importFieldMappings() {
  return [
    { source: '评论ID', target: 'id', required: true, confidence: 98, sample: 'r-001' },
    { source: '平台', target: 'platform', required: true, confidence: 96, sample: '小红书' },
    { source: '评论内容', target: 'content', required: true, confidence: 99, sample: '不敢喝了，有没有事啊？' },
    { source: '评论发布时间', target: 'publish_time', required: false, confidence: 92, sample: '2026-05-22' },
    { source: '评论作者', target: 'author', required: false, confidence: 88, sample: '小小妈妈' },
    { source: '评论点赞数', target: 'engagement.likes', required: false, confidence: 91, sample: '128' },
    { source: '评论回复数', target: 'engagement.replies', required: false, confidence: 86, sample: '18' },
    { source: '内容ID', target: 'source_content.id', required: false, confidence: 90, sample: 'note-001' },
    { source: '内容链接', target: 'source_content.url', required: false, confidence: 94, sample: 'https://...' },
    { source: '内容话题标签', target: 'source_content.topics', required: false, confidence: 83, sample: '#奶粉 #母婴' },
    { source: '内容发布者', target: 'source_content.author', required: false, confidence: 87, sample: '母婴观察号' },
    { source: '内容发布时间', target: 'source_content.publish_time', required: false, confidence: 89, sample: '2026-05-22 09:18' },
    { source: '内容评论数', target: 'source_content.comments', required: false, confidence: 84, sample: '240' },
    { source: '内容点赞数', target: 'source_content.likes', required: false, confidence: 84, sample: '1840' },
    { source: '内容收藏数', target: 'source_content.favorites', required: false, confidence: 79, sample: '316' },
    { source: '内容分享数', target: 'source_content.shares', required: false, confidence: 79, sample: '72' }
  ];
}

createRoot(document.getElementById('root')!).render(<App />);
