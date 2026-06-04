import React from 'react';
import { createRoot } from 'react-dom/client';
import {
  BookOpen,
  Brain,
  CheckCircle2,
  ChevronDown,
  Download,
  FileSpreadsheet,
  FolderKanban,
  Lightbulb,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Users
} from 'lucide-react';
import { fetchDashboard, patchRecord } from './api';
import type { DashboardResponse, DataRecord, LabelField, LabelOption, LabelSchema, LabelValue } from './types';
import './styles.css';

type ViewFilter = 'all' | 'unconfirmed' | 'negative' | 'conflict' | 'report';

const navItems = [
  { key: 'projects', label: '项目管理', icon: FolderKanban },
  { key: 'import', label: '数据导入', icon: FileSpreadsheet },
  { key: 'auto', label: '自动打标', icon: Sparkles },
  { key: 'labeling', label: '人工标注', icon: CheckCircle2 },
  { key: 'learning', label: '规则学习', icon: Brain },
  { key: 'report', label: '在线报告', icon: BookOpen },
  { key: 'users', label: '用户权限', icon: Users }
];

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

function App() {
  const [dashboard, setDashboard] = React.useState<DashboardResponse | null>(null);
  const [activeView, setActiveView] = React.useState('labeling');
  const [activeFilter, setActiveFilter] = React.useState<ViewFilter>('all');
  const [error, setError] = React.useState<string | null>(null);
  const [saveError, setSaveError] = React.useState<string | null>(null);
  const [saving, setSaving] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('');

  React.useEffect(() => {
    fetchDashboard()
      .then(setDashboard)
      .catch(err => setError(err instanceof Error ? err.message : '加载失败'));
  }, []);

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

  if (error) {
    return <div className="error-screen">{error}</div>;
  }

  if (!dashboard) {
    return <div className="loading-screen">正在加载舆情标注平台...</div>;
  }

  const visibleRecords = dashboard.records
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

  return (
    <div className="platform-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark" />
          <div>
            <strong>舆情标注平台</strong>
            <span>Sentiment Lab</span>
          </div>
        </div>
        <nav className="nav-list">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                className={activeView === item.key ? 'active' : ''}
                onClick={() => setActiveView(item.key)}
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
          <div>
            <p className="eyebrow">项目工作台 / {dashboard.active_project.rule_version}</p>
            <h1>{dashboard.active_project.name}</h1>
            <p className="header-copy">
              自动规则先打标，人工在多维表格中校正确认，系统把修改差异沉淀为规则建议。
            </p>
          </div>
          <div className="user-card">
            <div className="avatar">{dashboard.user.avatar}</div>
            <div>
              <strong>{dashboard.user.name}</strong>
              <span>{dashboard.user.role}</span>
            </div>
          </div>
        </header>

        <section className="metric-grid">
          <div className="metric-card">
            <span>项目进度</span>
            <strong>{dashboard.active_project.progress}%</strong>
            <p>已确认 {dashboard.active_project.confirmed_count.toLocaleString()} / {dashboard.active_project.total_count.toLocaleString()}</p>
          </div>
          <div className="metric-card">
            <span>标签体系</span>
            <strong>{dashboard.label_schema.name}</strong>
            <p>{dashboard.label_schema.fields.length} 个动态标签字段</p>
          </div>
          <div className="metric-card warning">
            <span>规则建议</span>
            <strong>{dashboard.suggestions.length} 条</strong>
            <p>来自本轮人工修改差异</p>
          </div>
          <div className="metric-card">
            <span>报告状态</span>
            <strong>{dashboard.report.status}</strong>
            <p>{dashboard.report.version} / 可在线确认</p>
          </div>
        </section>

        {activeView !== 'labeling' && (
          <PlaceholderView view={activeView} dashboard={dashboard} />
        )}

        {activeView === 'labeling' && (
          <section className="labeling-layout">
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
              <div className="save-strip">
                <span className={saving ? 'status-saving' : 'status-saved'}>
                  {saving ? '自动保存中...' : saveError ? '保存失败' : '已保存'}
                </span>
                <span>{saveError ?? '人工确认以黄色点标记，后续规则重跑不会覆盖。'}</span>
                <button type="button"><RefreshCw size={16} /> 重新打标未确认数据</button>
              </div>
              <LabelGrid
                records={visibleRecords}
                schema={dashboard.label_schema}
                onChange={updateLabel}
              />
            </div>
            <aside className="insight-panel">
              <div className="panel-card">
                <h3><Lightbulb size={18} /> 规则学习建议</h3>
                {dashboard.suggestions.map(suggestion => (
                  <article key={suggestion.id} className="suggestion-card">
                    <strong>{suggestion.title}</strong>
                    <p>{suggestion.summary}</p>
                    <div className="keyword-row">
                      {suggestion.keywords.map(keyword => <span key={keyword}>{keyword}</span>)}
                    </div>
                    <button type="button">查看 {suggestion.evidence_count} 条证据</button>
                  </article>
                ))}
              </div>
              <div className="panel-card">
                <h3><BookOpen size={18} /> 在线报告</h3>
                <p>{dashboard.report.title}，{dashboard.report.version}，状态：{dashboard.report.status}</p>
                <div className="report-blocks">
                  {dashboard.report.blocks.map(block => (
                    <article key={block.id}>
                      <strong>{block.title}</strong>
                      <span>{block.content}</span>
                    </article>
                  ))}
                </div>
                <button type="button" className="primary-action"><Download size={16} /> 导出 Word</button>
              </div>
            </aside>
          </section>
        )}
      </main>
    </div>
  );
}

function LabelGrid({
  records,
  schema,
  onChange
}: {
  records: DataRecord[];
  schema: LabelSchema;
  onChange: (record: DataRecord, field: LabelField, value: string) => void;
}) {
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
            <th className="sticky-col">状态</th>
            <th>平台</th>
            <th className="content-col">内容</th>
            <th>品牌</th>
            {schema.fields.map(field => <th key={field.key}>{field.name}</th>)}
            <th>报告</th>
          </tr>
        </thead>
        <tbody>
          {records.map(record => (
            <tr key={record.id}>
              <td className="sticky-col">
                {Object.values(record.labels).some(label => label.confirmed) ? (
                  <span className="manual-dot" title="本行包含人工确认标签" />
                ) : (
                  <span className="empty-dot" />
                )}
                {Object.values(record.labels).some(label => label.confirmed) ? '已确认' : '待确认'}
              </td>
              <td>{record.platform}<small>{record.publish_time}</small></td>
              <td className="content-col"><strong>{record.author}</strong><p>{record.content}</p></td>
              <td>{record.brand_detected}</td>
              {schema.fields.map(field => {
                const label = record.labels[field.key];
                const options = filteredOptions(field, record);
                return (
                  <td key={field.key}>
                    <div className="cell-editor" title={labelTooltip(label, schema, field.key)}>
                      {label?.confirmed && <span className="manual-dot" />}
                      <select value={label?.final ?? ''} onChange={event => onChange(record, field, event.target.value)}>
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
              })}
              <td>{record.report_candidate ? <span className="report-badge">候选</span> : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PlaceholderView({ view, dashboard }: { view: string; dashboard: DashboardResponse }) {
  const titles: Record<string, string> = {
    projects: '项目管理',
    import: '数据导入与字段映射',
    auto: '自动打标',
    learning: '规则学习',
    report: '在线报告',
    users: '用户权限'
  };

  return (
    <section className="placeholder-view">
      <div className="placeholder-copy">
        <h2>{titles[view]}</h2>
        <p>第一阶段先实现页面骨架和业务对象。后续会把这里扩展成完整流程页面。</p>
      </div>
      <div className="placeholder-grid">
        {dashboard.projects.map(project => (
          <article key={project.id}>
            <ShieldCheck size={20} />
            <strong>{project.name}</strong>
            <p>{project.label_schema} / {project.rule_version}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
