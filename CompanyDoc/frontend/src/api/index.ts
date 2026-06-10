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
  content: string;
}

export interface Term {
  id?: number;
  zh: string;
  en?: string;
  th?: string;
  category: string;
}

export interface Stats {
  total_documents: number;
  draft_documents: number;
  approved_documents: number;
  total_terms: number;
  total_templates: number;
}

export const documentsApi = {
  getAll: (params?: { page?: number; limit?: number; category?: string; status?: string }) =>
    api.get<Document[]>('/documents', { params }),
  getOne: (id: number) => api.get<Document>(`/documents/${id}`),
  create: (data: Document) => api.post<Document>('/documents', data),
  update: (id: number, data: Document) => api.put<Document>(`/documents/${id}`, data),
  delete: (id: number) => api.delete(`/documents/${id}`),
  approve: (id: number, approver: string, comment?: string) =>
    api.post(`/documents/${id}/approve`, { approver, comment }),
  reject: (id: number, approver: string, comment?: string) =>
    api.post(`/documents/${id}/reject`, { approver, comment }),
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

export const statsApi = {
  get: () => api.get<Stats>('/stats'),
};

export default api;