import { useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import api from '../api';
import './AIPanel.css';

interface AIPanelProps {
  currentContent: string;
  onInsert: (content: string) => void;
}

const actions = [
  { id: 'expand', label: '续写扩写', prompt: '请续写以下内容，使其更加详细完整：' },
  { id: 'translate_en', label: '翻译英文', prompt: '请翻译为英文：' },
  { id: 'translate_th', label: '翻译泰文', prompt: '请翻译为泰文：' },
  { id: 'polish', label: '优化润色', prompt: '请优化以下内容的语言表达，使其更加专业流畅：' },
  { id: 'summarize', label: '生成摘要', prompt: '请为以下内容生成简洁摘要：' },
];

export default function AIPanel({ currentContent, onInsert }: AIPanelProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');

  const handleAI = async (action: string) => {
    if (!currentContent.trim()) {
      setError('请先输入内容');
      return;
    }

    setLoading(true);
    setError('');
    setResult('');

    try {
      const res = await api.post('/ai/complete', {
        content: currentContent,
        action,
        max_tokens: 4096,
      });
      setResult(res.data.result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'AI 服务错误';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-panel">
      <div className="ai-header">
        <Sparkles size={18} />
        <span>AI 协作助手</span>
      </div>

      <div className="ai-actions">
        {actions.map((action) => (
          <button
            key={action.id}
            className="ai-action-btn"
            onClick={() => handleAI(action.id)}
            disabled={loading}
          >
            {action.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="ai-loading">
          <Loader2 size={20} className="spin" />
          <span>AI 思考中...</span>
        </div>
      )}

      {error && <div className="ai-error">{error}</div>}

      {result && (
        <div className="ai-result">
          <div className="ai-result-header">
            <span>AI 生成内容</span>
            <button onClick={() => onInsert(result)} className="insert-btn">
              插入文档
            </button>
          </div>
          <div className="ai-result-content">{result}</div>
        </div>
      )}
    </div>
  );
}