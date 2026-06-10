import './StatusBadge.css';

interface StatusBadgeProps {
  status: 'draft' | 'approved' | 'rejected';
}

const statusMap = {
  draft: { label: '草稿', className: 'draft' },
  approved: { label: '已审批', className: 'approved' },
  rejected: { label: '已驳回', className: 'rejected' },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const { label, className } = statusMap[status] || statusMap.draft;
  return <span className={`status-badge ${className}`}>{label}</span>;
}