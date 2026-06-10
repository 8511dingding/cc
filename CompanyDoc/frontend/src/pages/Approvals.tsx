import { useState, useEffect } from 'react';
import { documentsApi, type Document } from '../api';
import StatusBadge from '../components/StatusBadge';
import './Approvals.css';

export default function Approvals() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res = await documentsApi.getAll();
      setDocs(res.data.filter((d) => d.status !== 'draft'));
    } catch (err) {
      console.error('Failed to fetch:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <h2 className="page-title">审批流程</h2>
      </header>

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
              </tr>
            </thead>
            <tbody>
              {docs.length === 0 ? (
                <tr>
                  <td colSpan={4} className="empty-cell">暂无审批记录</td>
                </tr>
              ) : (
                docs.map((doc) => (
                  <tr key={doc.id}>
                    <td className="title-cell">{doc.title}</td>
                    <td>{doc.category}</td>
                    <td><StatusBadge status={doc.status as 'draft' | 'approved' | 'rejected'} /></td>
                    <td>{doc.created_at ? new Date(doc.created_at).toLocaleDateString() : '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}