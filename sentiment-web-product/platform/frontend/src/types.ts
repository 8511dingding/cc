export interface UserProfile {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'active' | 'invited' | 'disabled';
}

export interface ProjectSummary {
  id: string;
  name: string;
  client: string;
  brand: string;
  description: string;
  objective: string;
  platforms: string[];
  created_at: string;
  date_range: string;
  delivery_due: string;
  updated_at: string;
  owner: UserProfile;
  label_schema: string;
  rule_version: string;
  report_template: string;
  export_pattern: string;
  selected_rule_set_ids: string[];
  applied_rule_set_ids: string[];
  priority: '高' | '中' | '低';
  status: string;
  progress: number;
  confirmed_count: number;
  total_count: number;
}

export interface ProjectPayload {
  name: string;
  client: string;
  brand: string;
  description: string;
  objective: string;
  platforms: string[];
  date_range: string;
  delivery_due: string;
  owner_id: string;
  label_schema: string;
  rule_version: string;
  report_template: string;
  export_pattern: string;
  selected_rule_set_ids: string[];
  priority: '高' | '中' | '低';
  status: string;
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
  comment_type: '长评论' | '提及竞品' | '普通内容' | '@他人' | '符号表情';
  engagement: {
    likes: number;
    replies: number;
  };
  brand_detected: string;
  brands: string[];
  matched_keywords: string[];
  source_content: {
    id?: string | null;
    url?: string | null;
    author?: string | null;
    publish_time?: string | null;
    title?: string | null;
    topics: string[];
    comments: number;
    likes: number;
    favorites: number;
    shares: number;
  };
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

export interface ImportJob {
  id: string;
  filename: string;
  status: 'mapped' | 'importing' | 'ready' | 'failed';
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  created_at: string;
  owner: UserProfile;
}

export interface ImportFieldMapping {
  source: string;
  target: string;
  required: boolean;
  confidence: number;
  sample: string;
}

export interface ImportQualityIssue {
  rule: string;
  count: number;
  description: string;
  action: string;
  enabled: boolean;
}

export interface ImportPreviewResponse {
  filename: string;
  sheet_name: string;
  total_rows: number;
  headers: string[];
  mappings: ImportFieldMapping[];
  quality_issues: ImportQualityIssue[];
  samples: Record<string, string>[];
  inferred_platform: string;
  duplicate_comment_ids: number;
  long_comments: number;
  brand_mentions: Record<string, number>;
}

export interface BrandRule {
  id: string;
  brand: string;
  category: string;
  aliases: string[];
  products: string[];
  typo_variants: string[];
  competitor: boolean;
  enabled: boolean;
}

export interface RuleSet {
  id: string;
  name: string;
  layer: string;
  version: string;
  rule_count: number;
  last_updated: string;
  category: string;
  description: string;
  shared: boolean;
  editable: boolean;
}

export interface RuleDefinition {
  id: string;
  rule_set_id: string;
  category: string;
  layer: string;
  label: string;
  stage: string;
  keywords: string[];
  priority: number;
  source: string;
  enabled: boolean;
  editable: boolean;
}

export interface ProjectRuleStatus {
  rule_set_id: string;
  selected: boolean;
  applied: boolean;
  pending_apply: boolean;
}

export interface RuleImpactSample {
  record_id: string;
  content: string;
  before: string;
  after: string;
  matched_rule: string;
}

export interface RuleImpactPreview {
  project_id: string;
  selected_rule_set_ids: string[];
  newly_selected_rule_set_ids: string[];
  already_applied_rule_set_ids: string[];
  protected_records: number;
  before_counts: Record<string, number>;
  after_counts: Record<string, number>;
  changed_records: number;
  sample_changes: RuleImpactSample[];
}

export interface ReportTemplate {
  id: string;
  name: string;
  version: string;
  sections: string[];
  formats: Array<'docx' | 'pdf' | 'pptx'>;
  updated_at: string;
}

export interface ExportPreset {
  id: string;
  name: string;
  pattern: string;
  formats: Array<'xlsx' | 'docx' | 'pdf' | 'pptx'>;
}

export interface ExportRecord {
  id: string;
  filename: string;
  format: 'xlsx' | 'docx' | 'pdf' | 'pptx';
  status: 'ready' | 'exporting' | 'failed';
  report_version: string;
  created_at: string;
  size: string;
  owner: UserProfile;
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
  users: UserProfile[];
  projects: ProjectSummary[];
  active_project: ProjectSummary;
  label_schema: LabelSchema;
  records: DataRecord[];
  imports: ImportJob[];
  brand_rules: BrandRule[];
  rule_sets: RuleSet[];
  rule_definitions: RuleDefinition[];
  project_rule_status: ProjectRuleStatus[];
  suggestions: RuleSuggestion[];
  report_templates: ReportTemplate[];
  export_presets: ExportPreset[];
  export_records: ExportRecord[];
  report: ReportVersion;
}
