import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export interface Document {
  id?: number;
  title: string;
  content: string;
  content_en?: string;
  content_th?: string;
  template_id?: number;
  template_version_id?: number;
  category: string;
  status: string;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Template {
  id?: number;
  name: string;
  category?: string;
  content?: string;
  version_count?: number;
  latest_version?: number;
  latest_content?: string;
  created_at?: string;
}

export interface Term {
  id?: number;
  zh: string;
  en?: string;
  th?: string;
  category: string;
}

export interface Customer {
  id?: number;
  name: string;
  company_name?: string;
  company_name_th?: string;
  registration_number?: string;
  address?: string;
  address_th?: string;
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
  contact_phone_th?: string;
  notes?: string;
  source_document_id?: number;
  created_at?: string;
}

export interface UploadedFile {
  id?: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_type: string;
  file_size: number;
  parsed_content?: string;
  customer_id?: number;
  created_at?: string;
}

export interface Stats {
  total_documents: number;
  draft_documents: number;
  approved_documents: number;
  total_terms: number;
  total_templates: number;
  total_customers: number;
}

export const documentsApi = {
  getAll: (params?: { page?: number; limit?: number; category?: string; status?: string }) =>
    api.get<Document[]>('/documents', { params }),
  getOne: (id: number) => api.get<Document>(`/documents/${id}`),
  create: (data: Document) => api.post<Document>('/documents', data),
  update: (id: number, data: Document) => api.put<Document>(`/documents/${id}`, data),
  delete: (id: number) => api.delete(`/documents/${id}`),
};

export const templatesApi = {
  getAll: () => api.get<Template[]>('/templates'),
  create: (data: Template) => api.post<Template>('/templates', data),
  delete: (id: number) => api.delete(`/templates/${id}`),
};

export const termsApi = {
  getAll: (params?: { category?: string }) => api.get<Term[]>('/terms', { params }),
  create: (data: Term) => api.post<Term>('/terms', data),
  update: (id: number, data: Term) => api.put<Term>(`/terms/${id}`, data),
  delete: (id: number) => api.delete(`/terms/${id}`),
};

export const customersApi = {
  getAll: () => api.get<Customer[]>('/customers'),
  getOne: (id: number) => api.get<Customer>(`/customers/${id}`),
  create: (data: Customer) => api.post<Customer>('/customers', data),
  update: (id: number, data: Customer) => api.put<Customer>(`/customers/${id}`, data),
  delete: (id: number) => api.delete(`/customers/${id}`),
  getDocuments: (id: number) => api.get<Document[]>(`/customers/${id}/documents`),
  getFiles: (id: number) => api.get<UploadedFile[]>(`/customers/${id}/files`),
};

export const uploadApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<{ file_id: number; filename: string; original_filename: string }>(
      '/upload',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  },
  parse: (fileId: number) => api.post<{ content: string; customer_info: Customer }>(`/upload/${fileId}/parse`),
  getContent: (fileId: number) => api.get<{ content: string }>(`/upload/${fileId}/content`),
  getAll: () => api.get<UploadedFile[]>('/uploaded-files'),
  createCustomerFromFile: (fileId: number) => api.post<Customer>(`/customers/from-file/${fileId}`),
};

export const statsApi = {
  get: () => api.get<Stats>('/stats'),
};

export default api;