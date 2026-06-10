import { useState, useEffect } from 'react';
import { termsApi, type Term } from '../api';
import './Terms.css';

const categories = ['全部', '合同', '通知', '会议', '报告', '法律', '税务', '贸易', '电商', '通用'];

export default function Terms() {
  const [terms, setTerms] = useState<Term[]>([]);
  const [loading, setLoading] = useState(false);
  const [category, setCategory] = useState('全部');

  const fetchTerms = async () => {
    setLoading(true);
    try {
      const params = category !== '全部' ? { category } : undefined;
      const res = await termsApi.getAll(params);
      setTerms(res.data);
    } catch (err) {
      console.error('Failed to fetch terms:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTerms();
  }, [category]);

  return (
    <div className="page">
      <header className="page-header">
        <h2 className="page-title">术语库</h2>
      </header>

      <div className="filters">
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="terms-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>中文</th>
                <th>English</th>
               <th>ภาษาไทย</th>
                <th>分类</th>
              </tr>
            </thead>
            <tbody>
              {terms.length === 0 ? (
                <tr>
                  <td colSpan={4} className="empty-cell">暂无术语</td>
                </tr>
              ) : (
                terms.map((term) => (
                  <tr key={term.id}>
                    <td className="term-cell">{term.zh}</td>
                    <td>{term.en}</td>
                    <td className="th-cell">{term.th}</td>
                    <td><span className="category-tag">{term.category}</span></td>
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