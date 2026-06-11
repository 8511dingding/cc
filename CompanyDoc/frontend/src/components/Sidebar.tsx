import {
  FileText,
  Layout,
  BookOpen,
  Users,
  BarChart3,
  Upload,
} from 'lucide-react';
import './Sidebar.css';

interface SidebarProps {
  activeMenu: string;
  onMenuChange: (menu: string) => void;
}

const menuItems = [
  { id: 'documents', label: '文档管理', icon: FileText },
  { id: 'templates', label: '模板管理', icon: Layout },
  { id: 'terms', label: '术语库', icon: BookOpen },
  { id: 'customers', label: '客户管理', icon: Users },
  { id: 'uploads', label: '文档上传', icon: Upload },
  { id: 'statistics', label: '统计分析', icon: BarChart3 },
];

export default function Sidebar({ activeMenu, onMenuChange }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">CompanyDoc</h1>
        <span className="sidebar-subtitle">企业文档管理系统</span>
      </div>
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeMenu === item.id ? 'active' : ''}`}
            onClick={() => onMenuChange(item.id)}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}