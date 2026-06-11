import { useState, useEffect } from 'react';
import { Plus, Search, Edit2, Trash2, Eye, FileText, Building } from 'lucide-react';
import { customersApi, type Customer } from '../api';
import './Customers.css';

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const res = await customersApi.getAll();
      setCustomers(res.data);
    } catch (err) {
      console.error('Failed to fetch customers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个客户吗？')) return;
    try {
      await customersApi.delete(id);
      fetchCustomers();
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const filteredCustomers = customers.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    (c.company_name && c.company_name.toLowerCase().includes(search.toLowerCase())) ||
    (c.company_name_th && c.company_name_th.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="page">
      <header className="page-header">
        <h2 className="page-title">客户管理</h2>
        <button className="btn-primary" onClick={() => { setEditingCustomer(null); setShowModal(true); }}>
          <Plus size={18} />
          新建客户
        </button>
      </header>

      <div className="filters">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="搜索客户名称、公司名称..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>客户名称</th>
                <th>公司名称</th>
                <th>公司名称(泰)</th>
                <th>注册号</th>
                <th>联系方式</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredCustomers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="empty-cell">暂无客户</td>
                </tr>
              ) : (
                filteredCustomers.map((customer) => (
                  <tr key={customer.id}>
                    <td className="title-cell">{customer.name}</td>
                    <td>{customer.company_name || '-'}</td>
                    <td className="th-cell">{customer.company_name_th || '-'}</td>
                    <td>{customer.registration_number || '-'}</td>
                    <td>
                      {customer.contact_phone && <div>{customer.contact_phone}</div>}
                      {customer.contact_email && <div className="email">{customer.contact_email}</div>}
                    </td>
                    <td className="actions-cell">
                      <button className="btn-icon" title="查看详情" onClick={() => setSelectedCustomer(customer)}>
                        <Eye size={16} />
                      </button>
                      <button className="btn-icon" title="编辑" onClick={() => { setEditingCustomer(customer); setShowModal(true); }}>
                        <Edit2 size={16} />
                      </button>
                      <button className="btn-icon danger" title="删除" onClick={() => handleDelete(customer.id!)}>
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <CustomerModal
          customer={editingCustomer}
          onClose={() => setShowModal(false)}
          onSave={() => { setShowModal(false); fetchCustomers(); }}
        />
      )}

      {selectedCustomer && (
        <CustomerDetail
          customer={selectedCustomer}
          onClose={() => setSelectedCustomer(null)}
        />
      )}
    </div>
  );
}

function CustomerModal({ customer, onClose, onSave }: { customer: Customer | null; onClose: () => void; onSave: () => void }) {
  const [form, setForm] = useState<Customer>(customer || {
    name: '',
    company_name: '',
    company_name_th: '',
    registration_number: '',
    address: '',
    address_th: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    contact_phone_th: '',
    notes: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (customer?.id) {
        await customersApi.update(customer.id, form);
      } else {
        await customersApi.create(form);
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
      <div className="modal modal-large" onClick={(e) => e.stopPropagation()}>
        <h3>{customer?.id ? '编辑客户' : '新建客户'}</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>客户名称 *</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>联系人</label>
              <input value={form.contact_person || ''} onChange={(e) => setForm({ ...form, contact_person: e.target.value })} />
            </div>
            <div className="form-group">
              <label>公司名称(英文)</label>
              <input value={form.company_name || ''} onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
            </div>
            <div className="form-group">
              <label>公司名称(泰文)</label>
              <input value={form.company_name_th || ''} onChange={(e) => setForm({ ...form, company_name_th: e.target.value })} />
            </div>
            <div className="form-group">
              <label>注册号</label>
              <input value={form.registration_number || ''} onChange={(e) => setForm({ ...form, registration_number: e.target.value })} />
            </div>
            <div className="form-group">
              <label>邮箱</label>
              <input type="email" value={form.contact_email || ''} onChange={(e) => setForm({ ...form, contact_email: e.target.value })} />
            </div>
            <div className="form-group">
              <label>电话</label>
              <input value={form.contact_phone || ''} onChange={(e) => setForm({ ...form, contact_phone: e.target.value })} />
            </div>
            <div className="form-group">
              <label>电话(泰)</label>
              <input value={form.contact_phone_th || ''} onChange={(e) => setForm({ ...form, contact_phone_th: e.target.value })} />
            </div>
          </div>
          <div className="form-group">
            <label>地址(英文)</label>
            <textarea value={form.address || ''} onChange={(e) => setForm({ ...form, address: e.target.value })} rows={2} />
          </div>
          <div className="form-group">
            <label>地址(泰文)</label>
            <textarea value={form.address_th || ''} onChange={(e) => setForm({ ...form, address_th: e.target.value })} rows={2} />
          </div>
          <div className="form-group">
            <label>备注</label>
            <textarea value={form.notes || ''} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={2} />
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

function CustomerDetail({ customer, onClose }: { customer: Customer; onClose: () => void }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-large" onClick={(e) => e.stopPropagation()}>
        <h3>客户详情</h3>
        <div className="customer-detail">
          <div className="detail-section">
            <h4><Building size={16} /> 基本信息</h4>
            <div className="detail-grid">
              <div className="detail-item"><label>客户名称</label><span>{customer.name}</span></div>
              <div className="detail-item"><label>公司名称</label><span>{customer.company_name || '-'}</span></div>
              <div className="detail-item"><label>公司名称(泰)</label><span>{customer.company_name_th || '-'}</span></div>
              <div className="detail-item"><label>注册号</label><span>{customer.registration_number || '-'}</span></div>
            </div>
          </div>
          <div className="detail-section">
            <h4><FileText size={16} /> 联系信息</h4>
            <div className="detail-grid">
              <div className="detail-item"><label>联系人</label><span>{customer.contact_person || '-'}</span></div>
              <div className="detail-item"><label>邮箱</label><span>{customer.contact_email || '-'}</span></div>
              <div className="detail-item"><label>电话</label><span>{customer.contact_phone || '-'}</span></div>
              <div className="detail-item"><label>电话(泰)</label><span>{customer.contact_phone_th || '-'}</span></div>
            </div>
          </div>
          {customer.address && (
            <div className="detail-section">
              <h4>地址</h4>
              <p>{customer.address}</p>
              {customer.address_th && <p className="th-text">{customer.address_th}</p>}
            </div>
          )}
          {customer.notes && (
            <div className="detail-section">
              <h4>备注</h4>
              <p>{customer.notes}</p>
            </div>
          )}
        </div>
        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
}