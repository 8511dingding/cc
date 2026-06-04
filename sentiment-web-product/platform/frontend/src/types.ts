export interface UserProfile {
  id: string;
  name: string;
  role: string;
  avatar: string;
}

export interface ProjectSummary {
  id: string;
  name: string;
  client: string;
  brand: string;
  label_schema: string;
  rule_version: string;
  report_template: string;
  status: string;
  progress: number;
  confirmed_count: number;
  total_count: number;
}

export interface LabelOption {
  value: string;
  label: string;
  color?: string | null;
  parent_value?: string | null;
}

export interface LabelField {
  key: string;
  name: string;
  type: 'single_select' | 'text' | 'boolean';
  options: LabelOption[];
  parent_key?: string | null;
  visible_in_grid: boolean;
}

export interface LabelSchema {
  id: string;
  name: string;
  version: string;
  fields: LabelField[];
}

export interface LabelValue {
  auto?: string | null;
  manual?: string | null;
  final?: string | null;
  confirmed: boolean;
  confirmed_by?: UserProfile | null;
  confirmed_at?: string | null;
  previous_value?: string | null;
}

export interface DataRecord {
  id: string;
  platform: string;
  publish_time: string;
  author: string;
  content: string;
  brand_detected: string;
  labels: Record<string, LabelValue>;
  report_candidate: boolean;
}

export interface RuleSuggestion {
  id: string;
  title: string;
  summary: string;
  suggestion_type: string;
  evidence_count: number;
  keywords: string[];
  status: 'pending' | 'accepted' | 'ignored';
}

export interface ReportBlock {
  id: string;
  title: string;
  block_type: 'text' | 'chart' | 'table' | 'samples';
  content: string;
}

export interface ReportVersion {
  id: string;
  project_id: string;
  title: string;
  version: string;
  status: string;
  blocks: ReportBlock[];
}

export interface DashboardResponse {
  user: UserProfile;
  projects: ProjectSummary[];
  active_project: ProjectSummary;
  label_schema: LabelSchema;
  records: DataRecord[];
  suggestions: RuleSuggestion[];
  report: ReportVersion;
}
