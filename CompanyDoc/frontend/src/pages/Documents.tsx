import { useState, useEffect } from 'react';
import { Plus, Search, Eye, Edit2, Trash2 } from 'lucide-react';
import { documentsApi, type Document } from '../api';
import StatusBadge from '../components/StatusBadge';
import './Documents.css';

const categories = ['全部', '合同', '通知', '会议', '报告', '其他'];
const statuses = [
  { value: '', label: '全部状态' },
  { value: 'draft', label: '草稿' },
  { value: 'approved', label: '已审批' },
  { value: 'rejected', label: '已驳回' },
];

export default function Documents() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('全部');
  const [status, setStatus] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingDoc, setEditingDoc] = useState<Document | null>(null);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const params: { category?: string; status?: string } = {};
      if (category !== '全部') params.category = category;
      if (status) params.status = status;
      const res = await documentsApi.getAll(params);
      setDocs(res.data);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [category, status]);

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这篇文档吗？')) return;
    try {
      await documentsApi.delete(id);
      fetchDocs();
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await documentsApi.approve(id, '当前用户');
      fetchDocs();
    } catch (err) {
      console.error('Failed to approve:', err);
    }
  };

  const filteredDocs = docs.filter((doc) =>
    doc.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page">
      <header className="page-header">
        <h2 className="page-title">文档管理</h2>
        <button className="btn-primary" onClick={() => { setEditingDoc(null); setShowModal(true); }}>
          <Plus size={18} />
          新建文档
        </button>
      </header>

      <div className="filters">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="搜索文档标题..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {statuses.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>标题</th>
                <th>分类</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="empty-cell">暂无文档</td>
                </tr>
              ) : (
                filteredDocs.map((doc) => (
                  <tr key={doc.id}>
                    <td className="title-cell">{doc.title}</td>
                    <td>{doc.category}</td>
                    <td><StatusBadge status={doc.status as 'draft' | 'approved' | 'rejected'} /></td>
                    <td>{doc.created_at ? new Date(doc.created_at).toLocaleDateString() : '-'}</td>
                    <td className="actions-cell">
                      <button className="btn-icon" title="查看"><Eye size={16} /></button>
                      <button className="btn-icon" title="编辑"><Edit2 size={16} /></button>
                      {doc.status === 'draft' && (
                        <button className="btn-icon success" title="审批" onClick={() => handleApprove(doc.id!)}>✓</button>
                      )}
                      <button className="btn-icon danger" title="删除" onClick={() => handleDelete(doc.id!)}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <DocumentModal
          doc={editingDoc}
          onClose={() => setShowModal(false)}
          onSave={() => { setShowModal(false); fetchDocs(); }}
        />
      )}
    </div>
  );
}

function DocumentModal({ doc, onClose, onSave }: { doc: Document | null; onClose: () => void; onSave: () => void }) {
  const [title, setTitle] = useState(doc?.title || '');
  const [content, setContent] = useState(doc?.content || '');
  const [category, setCategory] = useState(doc?.category || '其他');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (doc?.id) {
        await documentsApi.update(doc.id, { title, content, category, status: doc.status });
      } else {
        await documentsApi.create({ title, content, category, status: 'draft' });
      }
      onSave();
    } catch (err) {
      console.error('Failed to save:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>{doc?.id ? '编辑文档' : '新建文档'}</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>标题</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>分类</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              {categories.slice(1).map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>内容</label>
            <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={10} />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>取消</button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}