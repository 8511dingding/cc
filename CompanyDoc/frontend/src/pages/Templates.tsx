import { useState, useEffect } from 'react';
import { FileText, ChevronDown, ChevronRight, Eye, Download } from 'lucide-react';
import api, { templatesApi, type Template } from '../api';
import './Templates.css';

interface TemplateVersion {
  id: number;
  template_id: number;
  version: number;
  content: string;
  description: string;
  created_at: string;
  doc_count: number;
}

export default function Templates() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [versions, setVersions] = useState<Record<number, TemplateVersion[]>>({});
  const [loading, setLoading] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<TemplateVersion | null>(null);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const res = await templatesApi.getAll();
      setTemplates(res.data);
    } catch (err) {
      console.error('Failed to fetch templates:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const toggleExpand = async (id: number) => {
    if (expandedId === id) {
      setExpandedId(null);
    } else {
      setExpandedId(id);
      if (!versions[id]) {
        try {
          const res = await api.get(`/templates/${id}/versions`);
          setVersions((prev) => ({ ...prev, [id]: res.data }));
        } catch (err) {
          console.error('Failed to fetch versions:', err);
        }
      }
    }
  };

  const selectVersion = (version: TemplateVersion) => {
    setSelectedVersion(version);
  };

  const downloadContent = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page">
      <header className="page-header">
        <h2 className="page-title">模板管理</h2>
      </header>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="template-list">
          {templates.length === 0 ? (
            <div className="empty-state">暂无模板</div>
          ) : (
            templates.map((tmpl) => (
              <div key={tmpl.id} className="template-item">
                <div className="template-row" onClick={() => tmpl.id && toggleExpand(tmpl.id)}>
                  <div className="template-main">
                    {expandedId === tmpl.id ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                    <FileText size={20} className="template-icon" />
                    <span className="template-name">{tmpl.name}</span>
                    <span className="template-category">{tmpl.category}</span>
                  </div>
                  <div className="template-meta">
                    <span className="version-badge">v{tmpl.latest_version}</span>
                    <span className="version-count">{tmpl.version_count} 个版本</span>
                  </div>
                </div>

                {expandedId === tmpl.id && versions[tmpl.id] && (
                  <div className="template-versions">
                    <div className="version-tabs">
                      {versions[tmpl.id].map((v) => (
                        <button
                          key={v.id}
                          className={`version-tab ${selectedVersion?.id === v.id ? 'active' : ''}`}
                          onClick={() => selectVersion(v)}
                        >
                          v{v.version}
                          {v.doc_count > 0 && <span className="doc-count">{v.doc_count}</span>}
                        </button>
                      ))}
                    </div>

                    {selectedVersion && (
                      <div className="version-content">
                        <div className="version-header">
                          <div className="version-info">
                            <h4>版本 {selectedVersion.version}</h4>
                            <span>{selectedVersion.description}</span>
                           <span className="version-date">
                              {new Date(selectedVersion.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="version-actions">
                            <button
                              className="btn-action"
                              onClick={() => downloadContent(selectedVersion.content, `${tmpl.name}_v${selectedVersion.version}.md`)}
                            >
                              <Download size={16} />
                              下载
                            </button>
                          </div>
                        </div>
                        <div className="version-preview">
                          <pre>{selectedVersion.content}</pre>
                        </div>

                        {selectedVersion.doc_count > 0 && (
                          <div className="version-documents">
                            <h5>已应用文档 ({selectedVersion.doc_count})</h5>
                            <VersionDocuments versionId={selectedVersion.id} />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function VersionDocuments({ versionId }: { versionId: number }) {
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchDocs = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/template-versions/${versionId}/documents`);
        setDocs(res.data);
      } catch (err) {
        console.error('Failed to fetch documents:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, [versionId]);

  if (loading) return <div className="loading">加载中...</div>;

  return (
    <div className="doc-list">
      {docs.map((doc) => (
        <div key={doc.id} className="doc-item">
          <div className="doc-info">
            <span className="doc-title">{doc.title}</span>
            <span className="doc-meta">{doc.category} | {doc.status}</span>
          </div>
          <div className="doc-actions">
            <button className="btn-action" onClick={() => window.open(`/documents/${doc.id}`, '_blank')}>
              <Eye size={14} />
              查看
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}