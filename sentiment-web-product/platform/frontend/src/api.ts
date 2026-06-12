import type { DashboardResponse, DataRecord, ImportPreviewResponse, ImportUploadResponse, ProjectPayload, ProjectSummary, RuleImpactPreview } from './types';

const API_BASE = '/api/platform';

async function responseError(response: Response, fallback: string): Promise<Error> {
  try {
    const payload = await response.json();
    if (typeof payload.detail === 'string') {
      return new Error(payload.detail);
    }
  } catch {
    // Keep the fallback when the response body is not JSON.
  }
  return new Error(`${fallback}：${response.status}`);
}

export async function fetchDashboard(projectId?: string): Promise<DashboardResponse> {
  const query = projectId ? `?project_id=${encodeURIComponent(projectId)}` : '';
  const response = await fetch(`${API_BASE}/dashboard${query}`);
  if (!response.ok) {
    throw await responseError(response, '加载工作台失败');
  }
  return response.json();
}

export async function createProject(payload: ProjectPayload): Promise<ProjectSummary> {
  const response = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw await responseError(response, '创建项目失败');
  }
  return response.json();
}

export async function updateProject(projectId: string, payload: ProjectPayload): Promise<ProjectSummary> {
  const response = await fetch(`${API_BASE}/projects/${projectId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw await responseError(response, '保存项目失败');
  }
  return response.json();
}

export async function deleteProject(projectId: string): Promise<{ deleted: boolean }> {
  const response = await fetch(`${API_BASE}/projects/${projectId}`, {
    method: 'DELETE'
  });
  if (!response.ok) {
    throw await responseError(response, '删除项目失败');
  }
  return response.json();
}

export async function previewProjectRules(projectId: string, selectedRuleSetIds: string[]): Promise<RuleImpactPreview> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/rules/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ edited_by: 'u-001', selected_rule_set_ids: selectedRuleSetIds })
  });
  if (!response.ok) {
    throw await responseError(response, '预览规则影响失败');
  }
  return response.json();
}

export async function applyProjectRules(projectId: string, selectedRuleSetIds: string[]): Promise<RuleImpactPreview> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/rules/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ edited_by: 'u-001', selected_rule_set_ids: selectedRuleSetIds })
  });
  if (!response.ok) {
    throw await responseError(response, '应用规则失败');
  }
  return response.json();
}

export async function patchRecord(
  recordId: string,
  updates: Array<{ field_key: string; value: string | null; confirmed: boolean }>
): Promise<DataRecord> {
  const response = await fetch(`${API_BASE}/records/${recordId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ edited_by: 'u-001', updates })
  });
  if (!response.ok) {
    throw await responseError(response, '保存标签失败');
  }
  return response.json();
}

export async function patchReportCandidate(recordId: string, reportCandidate: boolean): Promise<DataRecord> {
  const response = await fetch(`${API_BASE}/records/${recordId}/report-candidate`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ edited_by: 'u-001', report_candidate: reportCandidate })
  });
  if (!response.ok) {
    throw await responseError(response, '保存报告候选失败');
  }
  return response.json();
}

export async function patchBrands(recordId: string, brands: string[]): Promise<DataRecord> {
  const response = await fetch(`${API_BASE}/records/${recordId}/brands`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ edited_by: 'u-001', brands: brands.slice(0, 5) })
  });
  if (!response.ok) {
    throw await responseError(response, '保存品牌标签失败');
  }
  return response.json();
}

export async function previewImportFile(file: File): Promise<ImportPreviewResponse> {
  const body = new FormData();
  body.append('file', file);
  const response = await fetch(`${API_BASE}/imports/preview`, {
    method: 'POST',
    body
  });
  if (!response.ok) {
    throw await responseError(response, '导入预览失败');
  }
  return response.json();
}

export async function uploadImportFile(projectId: string, file: File): Promise<ImportUploadResponse> {
  const body = new FormData();
  body.append('file', file);
  const response = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}/imports`, {
    method: 'POST',
    body
  });
  if (!response.ok) {
    throw await responseError(response, '导入数据失败');
  }
  return response.json();
}

export async function deleteImportFile(projectId: string, importId: string): Promise<{ deleted: boolean }> {
  const response = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}/imports/${encodeURIComponent(importId)}`, {
    method: 'DELETE'
  });
  if (!response.ok) {
    throw await responseError(response, '删除导入文件失败');
  }
  return response.json();
}

export async function revalidateImportFile(projectId: string, importId: string): Promise<ImportUploadResponse> {
  const response = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}/imports/${encodeURIComponent(importId)}/revalidate`, {
    method: 'POST'
  });
  if (!response.ok) {
    throw await responseError(response, '重新清洗校验失败');
  }
  return response.json();
}
