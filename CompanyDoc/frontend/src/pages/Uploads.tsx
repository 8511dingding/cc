import { useState, useEffect } from 'react';
import { Upload as UploadIcon, FileText, User, Trash2, Eye, RefreshCw } from 'lucide-react';
import { uploadApi, type UploadedFile, type Customer } from '../api';
import './Uploads.css';

export default function Uploads() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [parsedInfo, setParsedInfo] = useState<Customer | null>(null);
  const [parsedLoading, setParsedLoading] = useState(false);
  const [createCustomerLoading, setCreateCustomerLoading] = useState(false);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const res = await uploadApi.getAll();
      setFiles(res.data);
    } catch (err) {
      console.error('Failed to fetch files:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const res = await uploadApi.upload(file);
      const newFile: UploadedFile = {
        id: res.data.file_id,
        filename: res.data.filename,
        original_filename: res.data.original_filename,
        file_path: '',
        file_type: file.type,
        file_size: file.size,
      };
      setFiles([newFile, ...files]);
    } catch (err) {
      console.error('Failed to upload:', err);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleParse = async (fileId: number) => {
    setParsedLoading(true);
    setParsedInfo(null);
    try {
      const res = await uploadApi.parse(fileId);
      setParsedInfo(res.data.customer_info);
      // Update the file record with parsed content
      fetchFiles();
    } catch (err) {
      console.error('Failed to parse:', err);
    } finally {
      setParsedLoading(false);
    }
  };

  const handleCreateCustomer = async () => {
    if (!selectedFile?.id || !parsedInfo) return;
    setCreateCustomerLoading(true);
    try {
      await uploadApi.createCustomerFromFile(selectedFile.id);
      alert('客户创建成功！');
      setSelectedFile(null);
      setParsedInfo(null);
    } catch (err) {
      console.error('Failed to create customer:', err);
    } finally {
      setCreateCustomerLoading(false);
    }
  };

  const handleDelete = async (_id: number) => {
    if (!confirm('确定要删除这个文件吗？')) return;
    try {
      // Note: delete endpoint doesn't exist yet, would need to add it
      console.error('Delete not implemented');
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('zh-CN');
  };

  return (
    <div className="page">
      <header className="page-header">
        <h2 className="page-title">文档上传</h2>
      </header>

      <div className="upload-area">
        <label className="upload-label">
          <input
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          <div className={`upload-box ${uploading ? 'uploading' : ''}`}>
            <UploadIcon size={32} />
            <span>{uploading ? '上传中...' : '点击或拖拽文件到此处上传'}</span>
            <span className="upload-hint">支持 PDF、Word、TXT 格式</span>
          </div>
        </label>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : files.length === 0 ? (
        <div className="empty-state">
          <FileText size={48} />
          <p>暂无上传记录</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>文件名</th>
                <th>原始文件名</th>
                <th>大小</th>
                <th>上传时间</th>
                <th>解析状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {files.map((file) => (
                <tr key={file.id}>
                  <td className="title-cell">{file.filename}</td>
                  <td>{file.original_filename}</td>
                  <td>{formatSize(file.file_size)}</td>
                  <td>{formatDate(file.created_at || '')}</td>
                  <td>
                    {file.parsed_content ? (
                      <span className="status-badge success">已解析</span>
                    ) : (
                      <span className="status-badge pending">待解析</span>
                    )}
                  </td>
                  <td className="actions-cell">
                    {file.parsed_content ? (
                      <button
                        className="btn-icon"
                        title="查看解析结果"
                        onClick={() => { setSelectedFile(file); setParsedInfo(null); }}
                      >
                        <Eye size={16} />
                      </button>
                    ) : (
                      <button
                        className="btn-icon"
                        title="解析文档"
                        onClick={() => file.id && handleParse(file.id)}
                        disabled={parsedLoading}
                      >
                        <RefreshCw size={16} className={parsedLoading ? 'spinning' : ''} />
                      </button>
                    )}
                    <button
                      className="btn-icon danger"
                      title="删除"
                      onClick={() => file.id && handleDelete(file.id!)}
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedFile && (
        <div className="modal-overlay" onClick={() => { setSelectedFile(null); setParsedInfo(null); }}>
          <div className="modal modal-large" onClick={(e) => e.stopPropagation()}>
            <h3>文档解析结果</h3>
            {parsedInfo ? (
              <div className="parsed-result">
                <div className="parsed-section">
                  <h4><User size={16} /> 提取的客户信息</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <label>客户名称</label>
                      <span>{parsedInfo.name || '-'}</span>
                    </div>
                    <div className="detail-item">
                      <label>公司名称(英)</label>
                      <span>{parsedInfo.company_name || '-'}</span>
                    </div>
                    <div className="detail-item">
                      <label>公司名称(泰)</label>
                      <span>{parsedInfo.company_name_th || '-'}</span>
                    </div>
                    <div className="detail-item">
                      <label>注册号</label>
                      <span>{parsedInfo.registration_number || '-'}</span>
                    </div>
                    <div className="detail-item">
                      <label>联系人</label>
                      <span>{parsedInfo.contact_person || '-'}</span>
                    </div>
                    <div className="detail-item">
                      <label>邮箱</label>
                      <span>{parsedInfo.contact_email || '-'}</span>
                    </div>
                    <div className="detail-item">
                      <label>电话</label>
                      <span>{parsedInfo.contact_phone || '-'}</span>
                    </div>
                    <div className="detail-item">
                      <label>地址</label>
                      <span>{parsedInfo.address || '-'}</span>
                    </div>
                  </div>
                </div>
                <div className="modal-actions">
                  <button className="btn-secondary" onClick={() => { setSelectedFile(null); setParsedInfo(null); }}>
                    关闭
                  </button>
                  <button
                    className="btn-primary"
                    onClick={handleCreateCustomer}
                    disabled={createCustomerLoading}
                  >
                    {createCustomerLoading ? '创建中...' : '创建客户'}
                  </button>
                </div>
              </div>
            ) : parsedLoading ? (
              <div className="loading">正在解析文档...</div>
            ) : (
              <div className="parsed-content">
                <p>暂无解析内容</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}