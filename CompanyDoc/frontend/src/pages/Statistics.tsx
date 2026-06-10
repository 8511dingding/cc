import { useState, useEffect } from 'react';
import { FileText, Layout, BookOpen, CheckCircle, AlertCircle } from 'lucide-react';
import { statsApi, type Stats } from '../api';
import './Statistics.css';

export default function Statistics() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const res = await statsApi.get();
        setStats(res.data);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const statCards = stats
    ? [
        { label: '文档总数', value: stats.total_documents, icon: FileText, color: '#3b82f6' },
        { label: '草稿文档', value: stats.draft_documents, icon: AlertCircle, color: '#f59e0b' },
        { label: '已审批', value: stats.approved_documents, icon: CheckCircle, color: '#16a34a' },
        { label: '模板总数', value: stats.total_templates, icon: Layout, color: '#8b5cf6' },
        { label: '术语总数', value: stats.total_terms, icon: BookOpen, color: '#ec4899' },
      ]
    : [];

  return (
    <div className="page">
      <header className="page-header">
        <h2 className="page-title">统计分析</h2>
      </header>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="stats-grid">
          {statCards.map((card) => (
            <div key={card.label} className="stat-card">
              <div className="stat-icon" style={{ background: `${card.color}15`, color: card.color }}>
                <card.icon size={24} />
              </div>
              <div className="stat-info">
                <span className="stat-value">{card.value}</span>
                <span className="stat-label">{card.label}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}