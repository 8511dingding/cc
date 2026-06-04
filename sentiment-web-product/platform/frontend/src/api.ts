import type { DashboardResponse, DataRecord } from './types';

const API_BASE = '/api/platform';

export async function fetchDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${API_BASE}/dashboard`);
  if (!response.ok) {
    throw new Error(`加载工作台失败：${response.status}`);
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
    throw new Error(`保存标签失败：${response.status}`);
  }
  return response.json();
}
