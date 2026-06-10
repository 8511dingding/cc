import { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import { templatesApi, type Template } from '../api';
import './Templates.css';

export default function Templates() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);

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

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个模板吗？')) return;
    try {
      await templatesApi.delete(id);
      fetchTemplates();
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h2 className="page-title">模板管理</h2>
      </header>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="template-grid">
          {templates.length === 0 ? (
            <div className="empty-state">暂无模板</div>
          ) : (
            templates.map((tpl) => (
              <div key={tpl.id} className="template-card">
                <div className="template-icon">
                  <FileText size={24} />
                </div>
                <div className="template-info">
                  <h3>{tpl.name}</h3>
                  <span className="template-category">{tpl.category}</span>
                </div>
                <button className="btn-icon danger" onClick={() => handleDelete(tpl.id!)}>
                  删除
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}