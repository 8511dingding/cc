import React from 'react';
import { createRoot } from 'react-dom/client';
import {
  BookOpen,
  Brain,
  CheckCircle2,
  ChevronDown,
  Cloud,
  Copy,
  Download,
  FileSpreadsheet,
  FileText,
  FolderKanban,
  LogOut,
  Menu,
  Lightbulb,
  Palette,
  Plus,
  RefreshCw,
  Save,
  Search,
  Settings,
  SlidersHorizontal,
  Sparkles,
  Type,
  Trash2,
  UploadCloud,
  Users
} from 'lucide-react';
import {
  applyProjectRules,
  createProject,
  deleteImportFile,
  deleteProject,
  fetchDashboard,
  patchBrands,
  patchRecord,
  patchReportCandidate,
  previewProjectRules,
  revalidateImportFile,
  uploadImportFile,
  updateProject
} from './api';
import type {
  DashboardResponse,
  DataRecord,
  ImportPreviewResponse,
  LabelField,
  LabelOption,
  LabelSchema,
  LabelValue,
  ProjectPayload,
  ProjectSummary,
  BrandRule,
  RuleDefinition,
  RuleImpactPreview
} from './types';
import './styles.css';

type ViewFilter = 'all' | 'unconfirmed' | 'negative' | 'conflict' | 'report';
type SortKey =
  | 'none'
  | 'comment_likes'
  | 'comment_replies'
  | 'comment_total'
  | 'comment_publish_time'
  | 'source_publish_time'
  | 'source_comments'
  | 'source_likes'
  | 'source_favorites'
  | 'source_shares';
type SortDirection = 'desc' | 'asc';
type ImportStage = 'upload' | 'mapping' | 'cleaning' | 'preview' | 'history';
type WordCloudSource = 'comments' | 'videos' | 'mixed' | 'report_candidates' | 'negative_comments';
type WordCloudShape = 'cloud' | 'circle' | 'rounded' | 'diamond' | 'trapezoid' | 'leaf' | 'pill' | 'drop' | 'heart' | 'star';
type WordCloudPalette =
  | 'brand'
  | 'fresh'
  | 'warm'
  | 'mono'
  | 'contrast'
  | 'magenta_mint'
  | 'plum_lime'
  | 'a2_report'
  | 'ocean'
  | 'sunset'
  | 'forest'
  | 'berry'
  | 'candy'
  | 'royal'
  | 'earth'
  | 'ice'
  | 'fire'
  | 'pastel'
  | 'ink'
  | 'neon';
type WordCloudLayoutMode = 'balanced' | 'dense' | 'airy';

interface WordCloudWordOverride {
  frequency?: number;
  size?: number;
  color?: string;
  repeat?: boolean;
}

interface WordCloudSettings {
  source: WordCloudSource;
  shape: WordCloudShape;
  palette: WordCloudPalette;
  layout: WordCloudLayoutMode;
  fontFamily: string;
  textScale: number;
  minFontSize: number;
  maxFontSize: number;
  spacing: number;
  maxWords: number;
  minFrequency: number;
  rotate: boolean;
  weightByEngagement: boolean;
  stopWords: string;
  customWords: string;
  templateName: string;
  wordOverrides: Record<string, WordCloudWordOverride>;
  layoutSeed: number;
}

interface WordCloudTemplate {
  id: string;
  client: string;
  brand: string;
  name: string;
  updated_at: string;
  settings: WordCloudSettings;
}

interface WordCloudTerm {
  text: string;
  value: number;
  frequency: number;
  engagement: number;
  weight: number;
  x: number;
  y: number;
  rotate: number;
  color: string;
  repeat: boolean;
}

interface WordCloudTermEditor {
  sourceText: string;
  text: string;
  frequency: number;
  size: number;
  color: string;
  repeat: boolean;
  left: number;
  top: number;
}

interface EvidenceSample {
  id: string;
  record_id: string;
  content: string;
  source_rule_set_id: string;
  source_rule_name: string;
  label_before: string;
  label_after: string;
  keyword_count: number;
  created_at: string;
}

type ImportedDataJob = DashboardResponse['imports'][number] & {
  included: boolean;
  imported_rows: number;
  duplicate_rows: number;
  file_size_label: string;
  download_url?: string;
  note: string;
};

interface AdvancedFilters {
  platform: string;
  commentType: string;
  minLikes: string;
  minReplies: string;
  sentimentPolarity: string;
  cognition: string;
  sentimentType: string;
  action: string;
  brand: string;
  reportStatus: string;
}

const defaultAdvancedFilters: AdvancedFilters = {
  platform: '',
  commentType: '',
  minLikes: '',
  minReplies: '',
  sentimentPolarity: '',
  cognition: '',
  sentimentType: '',
  action: '',
  brand: '',
  reportStatus: ''
};

const navItems = [
  { key: 'projects', label: '项目管理', icon: FolderKanban },
  { key: 'import', label: '数据导入', icon: FileSpreadsheet },
  { key: 'learning', label: '规则学习', icon: Brain },
  { key: 'auto', label: '自动打标', icon: Sparkles },
  { key: 'labeling', label: '人工标注', icon: CheckCircle2 },
  { key: 'wordcloud', label: '词云编辑', icon: Cloud },
  { key: 'report', label: '在线报告', icon: BookOpen },
  { key: 'users', label: '用户权限', icon: Users }
];

const defaultWordCloudSettings: WordCloudSettings = {
  source: 'comments',
  shape: 'cloud',
  palette: 'brand',
  layout: 'balanced',
  fontFamily: 'system',
  textScale: 100,
  minFontSize: 14,
  maxFontSize: 76,
  spacing: 100,
  maxWords: 70,
  minFrequency: 1,
  rotate: true,
  weightByEngagement: true,
  stopWords: '这个,那个,就是,因为,所以,还是,已经,没有,不是,可以,一个,我们,你们,他们,宝宝,孩子,奶粉,感觉,真的,现在,什么,怎么',
  customWords: '',
  templateName: '默认词云模板',
  wordOverrides: {},
  layoutSeed: 1
};

const extraCommonStopWords = '啊,呀,呢,吧,啦,嘛,哦,噢,哈,哈哈,哈哈哈,呵呵,嘿嘿,呜呜,哇,哎,唉,诶,额,嗯,呃,喔,哟,啧,呐,emmm,emm,omg,哈哈哈哈';

const wordCloudSourceOptions: Array<{ value: WordCloudSource; label: string; description: string }> = [
  { value: 'comments', label: '评论内容', description: '默认来源，适合看消费者真实表达。' },
  { value: 'videos', label: '视频内容', description: '使用内容标题、话题和发布者信息生成词云。' },
  { value: 'mixed', label: '评论 + 视频', description: '同时观察评论讨论和内容语境。' },
  { value: 'report_candidates', label: '报告候选评论', description: '只使用已勾选纳入报告统计的评论。' },
  { value: 'negative_comments', label: '负面评论', description: '聚焦负面情绪一级下的高频表达。' }
];

const wordCloudShapeOptions: Array<{ value: WordCloudShape; label: string }> = [
  { value: 'cloud', label: '云形' },
  { value: 'circle', label: '圆形' },
  { value: 'rounded', label: '圆角方形' },
  { value: 'diamond', label: '菱形' },
  { value: 'trapezoid', label: '梯形' },
  { value: 'leaf', label: '叶片' },
  { value: 'pill', label: '胶囊' },
  { value: 'drop', label: '水滴' },
  { value: 'heart', label: '心形' },
  { value: 'star', label: '星形' }
];

const wordCloudFontOptions: Array<{ value: string; label: string; family: string }> = [
  { value: 'system', label: '现代黑体', family: '"PingFang SC", "Microsoft YaHei", Helvetica, Arial, sans-serif' },
  { value: 'alipuhui', label: '阿里普惠体', family: '"Alibaba PuHuiTi Local", "Alibaba PuHuiTi", "PingFang SC", "Microsoft YaHei", sans-serif' },
  { value: 'dingtalk', label: '钉钉进步体', family: '"DingTalk JinBuTi Local", "DingTalk JinBuTi", "PingFang SC", "Microsoft YaHei", sans-serif' },
  { value: 'sourcehan', label: '思源黑体', family: '"Source Han Sans SC Local", "Source Han Sans SC", "Noto Sans CJK SC", "PingFang SC", sans-serif' },
  { value: 'smiley', label: '得意黑', family: '"Smiley Sans Local", "Smiley Sans", "PingFang SC", "Microsoft YaHei", sans-serif' },
  { value: 'songti', label: '宋体报告', family: '"Songti SC", STSong, SimSun, serif' },
  { value: 'kaiti', label: '楷体', family: '"Kaiti SC", KaiTi, STKaiti, serif' },
  { value: 'rounded', label: '圆体', family: '"Arial Rounded MT Bold", "PingFang SC", "Microsoft YaHei", sans-serif' },
  { value: 'condensed', label: '标题窄黑', family: 'Impact, Haettenschweiler, "Arial Narrow", "PingFang SC", sans-serif' },
  { value: 'light', label: '轻盈细体', family: '"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif' }
];

const wordCloudPaletteOptions: Array<{ value: WordCloudPalette; label: string; colors: string[] }> = [
  { value: 'brand', label: '品牌绿黄', colors: ['#126c43', '#1e8a55', '#edd156', '#7d6a12', '#20332a'] },
  { value: 'fresh', label: '清新绿蓝', colors: ['#0f766e', '#16a34a', '#38bdf8', '#84cc16', '#134e4a'] },
  { value: 'warm', label: '暖调提醒', colors: ['#9a3412', '#d97706', '#edd156', '#be123c', '#7c2d12'] },
  { value: 'mono', label: '专业单色', colors: ['#12251c', '#2c493b', '#52675d', '#7a8b83', '#9cac9f'] },
  { value: 'contrast', label: '高对比', colors: ['#0f172a', '#047857', '#f59e0b', '#dc2626', '#2563eb'] },
  { value: 'magenta_mint', label: '玫红薄荷', colors: ['#d400c6', '#5a3a72', '#1fed80', '#bf2f91', '#8d7f94'] },
  { value: 'plum_lime', label: '紫李青柠', colors: ['#4b2f63', '#74f78a', '#d737c8', '#7b6b92', '#32d56b'] },
  { value: 'a2_report', label: 'A2 报告色', colors: ['#c72bb5', '#4e3b65', '#43e87b', '#9477a5', '#e76bcf'] },
  { value: 'ocean', label: '海盐蓝', colors: ['#075985', '#0284c7', '#38bdf8', '#0f766e', '#a7f3d0'] },
  { value: 'sunset', label: '日落橙粉', colors: ['#7c2d12', '#ea580c', '#f97316', '#fb7185', '#be123c'] },
  { value: 'forest', label: '森林绿', colors: ['#14532d', '#166534', '#22c55e', '#84cc16', '#365314'] },
  { value: 'berry', label: '浆果紫', colors: ['#581c87', '#7e22ce', '#c026d3', '#e879f9', '#4c1d95'] },
  { value: 'candy', label: '糖果亮色', colors: ['#ec4899', '#22c55e', '#06b6d4', '#facc15', '#a855f7'] },
  { value: 'royal', label: '皇家蓝紫', colors: ['#1e3a8a', '#3730a3', '#6d28d9', '#9333ea', '#0f172a'] },
  { value: 'earth', label: '大地暖棕', colors: ['#7c2d12', '#92400e', '#a16207', '#4d7c0f', '#57534e'] },
  { value: 'ice', label: '冰川浅色', colors: ['#0e7490', '#67e8f9', '#bae6fd', '#e0f2fe', '#64748b'] },
  { value: 'fire', label: '火焰警示', colors: ['#7f1d1d', '#dc2626', '#f97316', '#facc15', '#991b1b'] },
  { value: 'pastel', label: '柔和彩色', colors: ['#f9a8d4', '#c4b5fd', '#93c5fd', '#86efac', '#fde68a'] },
  { value: 'ink', label: '水墨灰绿', colors: ['#111827', '#374151', '#6b7280', '#166534', '#9ca3af'] },
  { value: 'neon', label: '霓虹高亮', colors: ['#22d3ee', '#a3e635', '#f0abfc', '#fb7185', '#818cf8'] }
];

const projectPlatformOptions = [
  { name: '小红书', enabled: true, description: '当前支持字段映射和导入预览' },
  { name: '抖音', enabled: true, description: '当前支持字段映射和导入预览' },
  { name: '微博', enabled: false, description: '后续开放' },
  { name: 'B站', enabled: false, description: '后续开放' },
  { name: '公众号', enabled: false, description: '后续开放' },
  { name: '视频号', enabled: false, description: '后续开放' },
  { name: '快手', enabled: false, description: '后续开放' },
  { name: '知乎', enabled: false, description: '后续开放' }
];

const labelSchemaOptions = [
  {
    name: 'A2 三层标签体系',
    description: '情绪一级/二级、认知、行动，适合 A2 舆情事件复盘。'
  },
  {
    name: '风险等级 + 议题类型',
    description: '更适合周度监测，突出高风险样本、异常议题和处理优先级。'
  },
  {
    name: '正负向 + 议题 + 品牌识别',
    description: '适合多品牌竞品分析，关注态度、讨论主题和品牌关系。'
  }
];

function optionLabel(schema: LabelSchema, fieldKey: string, value?: string | null): string {
  if (!value) return '未选择';
  const field = schema.fields.find(item => item.key === fieldKey);
  return field?.options.find(item => item.value === value)?.label ?? value;
}

function filteredOptions(field: LabelField, record: DataRecord): LabelOption[] {
  if (!field.parent_key) return field.options;
  const parentValue = record.labels[field.parent_key]?.final;
  return field.options.filter(option => option.parent_value === parentValue);
}

function labelTooltip(label: LabelValue | undefined, schema: LabelSchema, fieldKey: string): string {
  if (!label?.confirmed || !label.confirmed_by) return '未人工确认';
  const from = optionLabel(schema, fieldKey, label.previous_value);
  const to = optionLabel(schema, fieldKey, label.final);
  return `${label.confirmed_by.name}（${label.confirmed_by.role}）确认\n${label.confirmed_at ?? ''}\n${from} -> ${to}`;
}

function priorityRank(priority: ProjectSummary['priority']): number {
  return priority === '高' ? 3 : priority === '中' ? 2 : 1;
}

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

function parseDateRange(value: string): [string, string] {
  const parts = value.split(/\s*(?:至|到|~|-{2,}|—|–)\s*/).map(item => item.trim()).filter(Boolean);
  return [parts[0] ?? todayISO(), parts[1] ?? parts[0] ?? todayISO()];
}

function joinDateRange(start: string, end: string): string {
  if (!start && !end) return '';
  if (!end) return start;
  if (!start) return end;
  return `${start} 至 ${end}`;
}

function readableRuleSetNames(project: ProjectSummary, dashboard: DashboardResponse): string[] {
  return project.selected_rule_set_ids
    .map(ruleSetId => dashboard.rule_sets.find(ruleSet => ruleSet.id === ruleSetId)?.name)
    .filter((name): name is string => Boolean(name));
}

function formatRuleStage(stage: string): string {
  const stageMap: Record<string, string> = {
    s1: '一级判断',
    s2: '二级细分',
    global: '全局规则',
    brand: '品牌识别',
    all: '全阶段'
  };
  return stageMap[stage] ?? (stage || '全阶段');
}

function formatFileSize(size: number): string {
  if (!Number.isFinite(size) || size <= 0) return '未知';
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`;
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${size} B`;
}

function toImportedDataJob(job: DashboardResponse['imports'][number]): ImportedDataJob {
  return {
    ...job,
    included: true,
    imported_rows: job.valid_rows,
    duplicate_rows: job.duplicate_rows ?? Math.max(job.total_rows - job.valid_rows - job.invalid_rows, 0),
    file_size_label: job.file_size_label ?? '历史记录',
    download_url: job.download_url ?? undefined,
    note: job.note || '历史导入记录'
  };
}

function wordCloudStorageKey(client: string): string {
  return `sentiment-wordcloud-templates:${client || 'default-client'}`;
}

function loadWordCloudTemplates(client: string): WordCloudTemplate[] {
  try {
    const raw = window.localStorage.getItem(wordCloudStorageKey(client));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.map(item => ({
      ...item,
      settings: normalizeWordCloudSettings(item.settings, item.name ?? defaultWordCloudSettings.templateName)
    })).sort((left, right) => wordCloudTemplateTime(right) - wordCloudTemplateTime(left));
  } catch {
    return [];
  }
}

function saveWordCloudTemplates(client: string, templates: WordCloudTemplate[]): void {
  window.localStorage.setItem(wordCloudStorageKey(client), JSON.stringify([...templates].sort((left, right) => wordCloudTemplateTime(right) - wordCloudTemplateTime(left))));
}

function hashText(value: string): number {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) >>> 0;
  }
  return hash;
}

function formatMonthDay(date = new Date()): string {
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${month}${day}`;
}

function defaultWordCloudTemplateName(client: string, projectName: string): string {
  return `${formatMonthDay()}-${client || '客户'}-${projectName || '项目'}-v0.1`;
}

function nextWordCloudSeed(): number {
  return Date.now() % 1000000000;
}

function wordCloudTemplateTime(template: Pick<WordCloudTemplate, 'id' | 'updated_at'>): number {
  const idTime = Number(template.id.replace(/^wc-/, ''));
  if (Number.isFinite(idTime) && idTime > 0) return idTime;
  const parsed = Date.parse(template.updated_at);
  return Number.isFinite(parsed) ? parsed : 0;
}

function stopWordSet(settings: WordCloudSettings): Set<string> {
  return new Set(settings.stopWords.split(/[,，\s、]+/).map(item => item.trim()).filter(Boolean));
}

function recordMatchesNegative(record: DataRecord): boolean {
  return record.labels.sentiment_polarity?.final === 'negative' || record.labels.sentiment_type?.final === 'panic' || record.labels.sentiment_type?.final === 'anger';
}

function sourceTextsForWordCloud(records: DataRecord[], source: WordCloudSource): Array<{ text: string; engagement: number }> {
  const selectedRecords = records.filter(record => {
    if (source === 'report_candidates') return record.report_candidate;
    if (source === 'negative_comments') return recordMatchesNegative(record);
    return true;
  });

  return selectedRecords.flatMap(record => {
    const engagement = Math.max(1, record.engagement.likes + record.engagement.replies + 1);
    const videoText = [
      record.source_content.title,
      record.source_content.author,
      record.source_content.topics.join(' ')
    ].filter(Boolean).join(' ');

    if (source === 'videos') return [{ text: videoText, engagement }];
    if (source === 'mixed') return [{ text: record.content, engagement }, { text: videoText, engagement }];
    return [{ text: record.content, engagement }];
  }).filter(item => item.text.trim());
}

function tokenizeForWordCloud(text: string): string[] {
  const normalized = text
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/[@#][\w\u4e00-\u9fa5-]+/g, match => ` ${match.replace(/^[@#]/, '')} `)
    .replace(/[^\w\u4e00-\u9fa5]+/g, ' ');
  const tokens: string[] = [];
  const parts = normalized.split(/\s+/).map(item => item.trim()).filter(Boolean);

  parts.forEach(part => {
    if (/^[a-zA-Z][\w-]{1,}$/i.test(part)) {
      tokens.push(part.toLowerCase());
      return;
    }
    const chineseParts = part.match(/[\u4e00-\u9fa5]{2,}/g) ?? [];
    chineseParts.forEach(chunk => {
      if (chunk.length <= 6) {
        tokens.push(chunk);
        return;
      }
      for (let index = 0; index <= chunk.length - 2; index += 2) {
        tokens.push(chunk.slice(index, Math.min(index + 4, chunk.length)));
      }
    });
  });

  return tokens;
}

function countWordCloudOccurrences(text: string, keyword: string): number {
  const needle = keyword.trim().toLowerCase();
  if (needle.length < 2) return 0;
  const haystack = text.toLowerCase();
  let count = 0;
  let index = haystack.indexOf(needle);
  while (index >= 0) {
    count += 1;
    index = haystack.indexOf(needle, index + needle.length);
  }
  return count;
}

function paletteColors(palette: WordCloudPalette): string[] {
  return wordCloudPaletteOptions.find(option => option.value === palette)?.colors ?? wordCloudPaletteOptions[0].colors;
}

function wordCloudFontFamily(fontFamily: string): string {
  return wordCloudFontOptions.find(option => option.value === fontFamily)?.family ?? wordCloudFontOptions[0].family;
}

function normalizeWordCloudSettings(settings?: Partial<WordCloudSettings>, fallbackName = defaultWordCloudSettings.templateName): WordCloudSettings {
  const nextSettings = {
    ...defaultWordCloudSettings,
    ...(settings ?? {}),
    templateName: settings?.templateName ?? fallbackName,
    wordOverrides: settings?.wordOverrides ?? {},
    layoutSeed: settings?.layoutSeed ?? defaultWordCloudSettings.layoutSeed
  };
  if ((nextSettings.shape as string) === 'square') {
    nextSettings.shape = 'circle';
  }
  if (!wordCloudShapeOptions.some(option => option.value === nextSettings.shape)) {
    nextSettings.shape = 'cloud';
  }
  if (!wordCloudFontOptions.some(option => option.value === nextSettings.fontFamily)) {
    nextSettings.fontFamily = 'system';
  }
  return nextSettings;
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function splitWordCloudWords(value: string): string[] {
  return value.split(/[\n,，、;\t]+/).map(item => item.trim()).filter(Boolean);
}

function cleanImportedWord(raw: string, removeNumbers: boolean, removeCommonWords: boolean): string | null {
  const cleaned = raw
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/@\S+/g, ' ')
    .replace(/[#＃]/g, ' ')
    .replace(/[~\-]+/g, ' ')
    .replace(/[^\w\u4e00-\u9fa5]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  if (!cleaned) return null;
  if (removeNumbers && /^[\d\s.]+$/.test(cleaned)) return null;
  if (!/[\u4e00-\u9fa5a-zA-Z]/.test(cleaned)) return null;
  if (removeCommonWords && defaultWordCloudSettings.stopWords.split(/[,，\s、]+/).includes(cleaned)) return null;
  return cleaned;
}

function mergeWordCloudWords(existing: string, additions: string[]): string {
  return Array.from(new Set([...splitWordCloudWords(existing), ...additions])).join('，');
}

function wordRowDomId(text: string): string {
  return `word-row-${hashText(text)}`;
}

function seededNoise(seed: number, index: number): number {
  const value = Math.sin(seed * 12.9898 + index * 78.233) * 43758.5453;
  return value - Math.floor(value);
}

function insideWordCloudShape(x: number, y: number, shape: WordCloudShape): boolean {
  const nx = (x - 50) / 42;
  const ny = (y - 50) / 36;
  const absX = Math.abs(nx);
  const absY = Math.abs(ny);

  if (shape === 'circle') return ((x - 50) / 34) ** 2 + ((y - 50) / 34) ** 2 <= 1;
  if (shape === 'rounded') return absX <= 0.96 && absY <= 0.82;
  if (shape === 'diamond') return absX + absY <= 1.05;
  if (shape === 'trapezoid') {
    const topWidth = 48;
    const bottomWidth = 82;
    const halfWidth = (topWidth + ((y - 18) / 64) * (bottomWidth - topWidth)) / 2;
    return y >= 18 && y <= 82 && Math.abs(x - 50) <= halfWidth;
  }
  if (shape === 'pill') return absY <= 0.54 && (absX <= 0.58 || (absX - 0.58) ** 2 + absY ** 2 <= 0.3);
  if (shape === 'leaf') {
    const rx = (x - 51) / 36;
    const ry = (y - 50) / 24;
    return rx * rx + ry * ry <= 1 && x + y > 52 && x + y < 148;
  }
  if (shape === 'drop') {
    const top = ((x - 50) / 26) ** 2 + ((y - 44) / 26) ** 2 <= 1;
    const bottom = Math.abs((x - 50) / 28) + Math.max(0, (y - 52) / 34) <= 1;
    return top || bottom;
  }
  if (shape === 'star') {
    const angle = Math.atan2(ny, nx);
    const distance = Math.sqrt(nx * nx + ny * ny);
    const edge = 0.72 + 0.28 * Math.cos(5 * angle);
    return distance <= edge;
  }
  if (shape === 'heart') {
    const hx = (x - 50) / 30;
    const hy = -(y - 54) / 30;
    return (hx * hx + hy * hy - 1) ** 3 - hx * hx * hy ** 3 <= 0;
  }

  const cloudCircles = [
    [33, 56, 18],
    [46, 43, 21],
    [62, 47, 18],
    [69, 59, 16],
    [49, 61, 25]
  ];
  return cloudCircles.some(([cx, cy, radius]) => ((x - cx) ** 2 + (y - cy) ** 2) <= radius ** 2);
}

function wordCloudPoint(index: number, total: number, shape: WordCloudShape, density: number): { x: number; y: number } {
  const spiralStep = 0.32;
  for (let attempt = 0; attempt < 260; attempt += 1) {
    const angle = attempt * spiralStep + index * 0.55;
    const radius = Math.sqrt(attempt) * 2.35 * clamp(density, 0.72, 1.28);
    const x = 50 + Math.cos(angle) * radius;
    const y = 50 + Math.sin(angle) * radius * 0.78;
    if (insideWordCloudShape(x, y, shape)) return { x: clamp(x, 6, 94), y: clamp(y, 8, 92) };
  }
  const fallbackAngle = (index / Math.max(total, 1)) * Math.PI * 2;
  return {
    x: clamp(50 + Math.cos(fallbackAngle) * 16, 6, 94),
    y: clamp(50 + Math.sin(fallbackAngle) * 13, 8, 92)
  };
}

function wordVisualUnits(text: string): number {
  return Array.from(text).reduce((sum, char) => {
    if (/[\u4e00-\u9fa5]/.test(char)) return sum + 1;
    if (/[A-Z]/.test(char)) return sum + 0.72;
    if (/[a-z0-9]/.test(char)) return sum + 0.56;
    return sum + 0.42;
  }, 0);
}

function wordBox(term: Pick<WordCloudTerm, 'text' | 'weight' | 'x' | 'y'>): { x0: number; y0: number; x1: number; y1: number } {
  const width = clamp(wordVisualUnits(term.text) * term.weight * 0.145, 4.2, 76);
  const height = clamp(term.weight * 0.2, 3.2, 17);
  return {
    x0: term.x - width / 2,
    x1: term.x + width / 2,
    y0: term.y - height / 2,
    y1: term.y + height / 2
  };
}

function boxesOverlap(left: { x0: number; y0: number; x1: number; y1: number }, right: { x0: number; y0: number; x1: number; y1: number }, padding: number): boolean {
  return left.x0 < right.x1 + padding && left.x1 + padding > right.x0 && left.y0 < right.y1 + padding && left.y1 + padding > right.y0;
}

function wordBoxInsideShape(box: { x0: number; y0: number; x1: number; y1: number }, shape: WordCloudShape): boolean {
  const inset = 1.2;
  const points = [
    [box.x0 + inset, box.y0 + inset],
    [box.x1 - inset, box.y0 + inset],
    [box.x0 + inset, box.y1 - inset],
    [box.x1 - inset, box.y1 - inset],
    [(box.x0 + box.x1) / 2, box.y0 + inset],
    [(box.x0 + box.x1) / 2, box.y1 - inset]
  ];
  return points.every(([x, y]) => insideWordCloudShape(x, y, shape));
}

function placeWordCloudTerms(terms: WordCloudTerm[], shape: WordCloudShape, layout: WordCloudLayoutMode, spacing: number, seed: number): WordCloudTerm[] {
  const density = clamp(spacing / 100, 0, 2);
  const layoutFactor = layout === 'dense' ? 0.52 : layout === 'airy' ? 1.78 : 1;
  const averageWeight = terms.reduce((sum, term) => sum + term.weight, 0) / Math.max(terms.length, 1);
  const fontFactor = clamp(averageWeight / 42, 0.48, 1.16);
  const padding = (0.35 + density * 1.65) * layoutFactor * fontFactor;
  const spread = (0.58 + density * 0.72) * Math.sqrt(layoutFactor);

  const placeWithScale = (fontScale: number) => {
    const placedBoxes: Array<{ x0: number; y0: number; x1: number; y1: number }> = [];
    const placed: WordCloudTerm[] = [];

    terms.forEach((originalTerm, index) => {
      const term = { ...originalTerm, weight: Math.max(9, Math.round(originalTerm.weight * fontScale)) };
      const angleOffset = seededNoise(seed, index) * Math.PI * 2;
      const direction = seededNoise(seed + 17, index) > 0.5 ? 1 : -1;
      for (let attempt = 0; attempt < 1100; attempt += 1) {
        const angle = angleOffset + direction * attempt * 0.34 + index * 0.19;
        const radius = Math.sqrt(attempt + seededNoise(seed + 31, index) * 6) * spread;
        const candidate = {
          x: clamp(50 + Math.cos(angle) * radius, 3, 97),
          y: clamp(50 + Math.sin(angle) * radius * 0.74, 5, 95)
        };
        if (!insideWordCloudShape(candidate.x, candidate.y, shape)) continue;
        const candidateBox = wordBox({ ...term, ...candidate });
        if (wordBoxInsideShape(candidateBox, shape) && placedBoxes.every(box => !boxesOverlap(candidateBox, box, padding))) {
          placedBoxes.push(candidateBox);
          placed.push({ ...term, ...candidate });
          return;
        }
      }
    });

    return placed;
  };

  let bestPlaced: WordCloudTerm[] = [];
  for (const scale of [1, 0.92, 0.84, 0.76, 0.68, 0.6, 0.52]) {
    const placed = placeWithScale(scale);
    if (placed.length > bestPlaced.length) bestPlaced = placed;
    if (placed.length >= Math.min(terms.length, Math.ceil(terms.length * 0.72))) return placed;
  }

  return bestPlaced;
}

function buildWordCloudTerms(records: DataRecord[], settings: WordCloudSettings, dictionaryWords: string[] = []): WordCloudTerm[] {
  const stops = stopWordSet(settings);
  const weightedCounts = new Map<string, number>();
  const frequencies = new Map<string, number>();
  const engagements = new Map<string, number>();
  const sources = sourceTextsForWordCloud(records, settings.source);
  const dictionary = Array.from(new Set([
    ...dictionaryWords,
    ...splitWordCloudWords(settings.customWords)
  ].map(word => word.trim()).filter(word => word.length >= 2 && !stops.has(word))));
  sources.forEach(item => {
    dictionary.forEach(keyword => {
      const hitCount = countWordCloudOccurrences(item.text, keyword);
      if (hitCount <= 0) return;
      const value = (settings.weightByEngagement ? Math.log2(item.engagement + 1) : 1) * hitCount;
      weightedCounts.set(keyword, (weightedCounts.get(keyword) ?? 0) + value);
      frequencies.set(keyword, (frequencies.get(keyword) ?? 0) + hitCount);
      engagements.set(keyword, (engagements.get(keyword) ?? 0) + item.engagement);
    });
    const engagedTokens = new Set<string>();
    tokenizeForWordCloud(item.text).forEach(token => {
      if (token.length < 2 || stops.has(token)) return;
      const value = settings.weightByEngagement ? Math.log2(item.engagement + 1) : 1;
      weightedCounts.set(token, (weightedCounts.get(token) ?? 0) + value);
      frequencies.set(token, (frequencies.get(token) ?? 0) + 1);
      engagedTokens.add(token);
    });
    engagedTokens.forEach(token => {
      engagements.set(token, (engagements.get(token) ?? 0) + item.engagement);
    });
  });

  splitWordCloudWords(settings.customWords).forEach(token => {
    weightedCounts.set(token, Math.max(weightedCounts.get(token) ?? 0, 3));
    frequencies.set(token, Math.max(frequencies.get(token) ?? 0, 1));
    engagements.set(token, Math.max(engagements.get(token) ?? 0, 0));
  });

  const rawTerms = Array.from(weightedCounts.entries())
    .map(([text, value]) => [text, value, settings.wordOverrides[text]?.frequency ?? (frequencies.get(text) ?? 0)] as const)
    .filter(([, , frequency]) => frequency >= settings.minFrequency)
    .sort((left, right) => right[2] - left[2] || right[1] - left[1])
    .slice(0, settings.maxWords);
  const maxFrequency = Math.max(...rawTerms.map(([, , frequency]) => frequency), 1);
  const colors = paletteColors(settings.palette);
  const minFont = Math.min(settings.minFontSize, settings.maxFontSize);
  const maxFont = Math.max(settings.minFontSize, settings.maxFontSize);

  const rankedTerms = rawTerms.map(([text, value, frequency], index) => {
    const override = settings.wordOverrides[text] ?? {};
    return {
      text,
      value,
      frequency,
      engagement: engagements.get(text) ?? 0,
      weight: override.size ?? Math.round(minFont + (frequency / maxFrequency) * (maxFont - minFont)),
      x: 50,
      y: 50,
      rotate: 0,
      color: override.color ?? colors[index % colors.length],
      repeat: override.repeat ?? true
    };
  });

  return placeWordCloudTerms(rankedTerms, settings.shape, settings.layout, settings.spacing, settings.layoutSeed);
}

function buildWordCloudClip(ctx: CanvasRenderingContext2D, shape: WordCloudShape, width: number, height: number): void {
  const cx = width / 2;
  const cy = height / 2;
  const size = Math.min(width * 0.72, height * 0.82);
  const left = cx - size / 2;
  const top = cy - size / 2;
  ctx.beginPath();
  if (shape === 'circle') {
    ctx.ellipse(cx, cy, size / 2, size / 2, 0, 0, Math.PI * 2);
    return;
  }
  if (shape === 'trapezoid') {
    ctx.moveTo(cx - size * 0.24, top);
    ctx.lineTo(cx + size * 0.24, top);
    ctx.lineTo(cx + size * 0.44, top + size);
    ctx.lineTo(cx - size * 0.44, top + size);
    ctx.closePath();
    return;
  }
  if (shape === 'rounded') {
    const radius = 72;
    ctx.moveTo(left + radius, top);
    ctx.lineTo(left + size - radius, top);
    ctx.quadraticCurveTo(left + size, top, left + size, top + radius);
    ctx.lineTo(left + size, top + size - radius);
    ctx.quadraticCurveTo(left + size, top + size, left + size - radius, top + size);
    ctx.lineTo(left + radius, top + size);
    ctx.quadraticCurveTo(left, top + size, left, top + size - radius);
    ctx.lineTo(left, top + radius);
    ctx.quadraticCurveTo(left, top, left + radius, top);
    return;
  }
  if (shape === 'heart') {
    const scale = size / 2.8;
    ctx.moveTo(cx, cy + scale * 0.62);
    ctx.bezierCurveTo(cx - scale * 1.55, cy - scale * 0.18, cx - scale * 1.0, cy - scale * 1.14, cx, cy - scale * 0.56);
    ctx.bezierCurveTo(cx + scale * 1.0, cy - scale * 1.14, cx + scale * 1.55, cy - scale * 0.18, cx, cy + scale * 0.62);
    return;
  }
  ctx.moveTo(cx - size * 0.44, cy + size * 0.14);
  ctx.bezierCurveTo(cx - size * 0.55, cy - size * 0.04, cx - size * 0.34, cy - size * 0.26, cx - size * 0.16, cy - size * 0.18);
  ctx.bezierCurveTo(cx - size * 0.1, cy - size * 0.42, cx + size * 0.24, cy - size * 0.44, cx + size * 0.34, cy - size * 0.18);
  ctx.bezierCurveTo(cx + size * 0.55, cy - size * 0.14, cx + size * 0.57, cy + size * 0.16, cx + size * 0.34, cy + size * 0.22);
  ctx.lineTo(cx - size * 0.28, cy + size * 0.22);
  ctx.bezierCurveTo(cx - size * 0.36, cy + size * 0.22, cx - size * 0.42, cy + size * 0.19, cx - size * 0.44, cy + size * 0.14);
}

function App() {
  const [dashboard, setDashboard] = React.useState<DashboardResponse | null>(null);
  const [activeView, setActiveView] = React.useState('labeling');
  const [activeFilter, setActiveFilter] = React.useState<ViewFilter>('all');
  const [error, setError] = React.useState<string | null>(null);
  const [saveError, setSaveError] = React.useState<string | null>(null);
  const [saving, setSaving] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedRecordId, setSelectedRecordId] = React.useState<string | null>(null);
  const [sidebarPinned, setSidebarPinned] = React.useState(false);
  const [userMenuOpen, setUserMenuOpen] = React.useState(false);
  const [projectMenuOpen, setProjectMenuOpen] = React.useState(false);
  const [activeProjectId, setActiveProjectId] = React.useState<string | undefined>(undefined);
  const [advancedFilters, setAdvancedFilters] = React.useState<AdvancedFilters>(defaultAdvancedFilters);
  const [sortKey, setSortKey] = React.useState<SortKey>('none');
  const [sortDirection, setSortDirection] = React.useState<SortDirection>('desc');
  const [evidenceSamples, setEvidenceSamples] = React.useState<EvidenceSample[]>([]);
  const [evidenceNotice, setEvidenceNotice] = React.useState<string | null>(null);
  const [labelWorkflowNotice, setLabelWorkflowNotice] = React.useState<string | null>(null);

  React.useEffect(() => {
    fetchDashboard(activeProjectId)
      .then(data => {
        setDashboard(data);
        setActiveProjectId(data.active_project.id);
        setSelectedRecordId(null);
        setActiveFilter('all');
        setAdvancedFilters(defaultAdvancedFilters);
      })
      .catch(err => setError(err instanceof Error ? err.message : '加载失败'));
  }, [activeProjectId]);

  React.useEffect(() => {
    if (!dashboard || evidenceSamples.length > 0) return;
    setEvidenceSamples(buildInitialEvidenceSamples(dashboard));
  }, [dashboard, evidenceSamples.length]);

  const refreshDashboard = React.useCallback(async (projectId?: string) => {
    const targetProjectId = projectId ?? activeProjectId ?? dashboard?.active_project.id;
    const refreshed = await fetchDashboard(targetProjectId);
    setDashboard(refreshed);
    setActiveProjectId(refreshed.active_project.id);
    return refreshed;
  }, [activeProjectId, dashboard?.active_project.id]);

  const switchProject = (projectId: string) => {
    setProjectMenuOpen(false);
    setActiveProjectId(projectId);
    setActiveView('projects');
  };

  const addProject = async (payload: ProjectPayload) => {
    setSaveError(null);
    const created = await createProject(payload);
    setDashboard(current => current ? {
      ...current,
      projects: [created, ...current.projects],
      active_project: created,
      records: [],
      imports: [],
      export_records: [],
      report: {
        ...current.report,
        id: `report-${created.id}`,
        project_id: created.id,
        title: '在线舆情分析报告',
        version: 'v00',
        status: '待生成',
        blocks: [{
          id: `${created.id}-empty-summary`,
          title: '项目摘要',
          block_type: 'text',
          content: '项目创建后，请先完成数据导入、规则学习与自动打标，再生成在线报告。'
        }]
      }
    } : current);
    setActiveProjectId(created.id);
    setActiveView('projects');
    return created;
  };

  const editProject = async (projectId: string, payload: ProjectPayload) => {
    setSaveError(null);
    const updated = await updateProject(projectId, payload);
    setDashboard(current => current ? {
      ...current,
      projects: current.projects.map(project => (project.id === updated.id ? updated : project)),
      active_project: current.active_project.id === updated.id ? updated : current.active_project
    } : current);
    return updated;
  };

  const previewRulesForProject = async (projectId: string, selectedRuleSetIds: string[]) => {
    return previewProjectRules(projectId, selectedRuleSetIds);
  };

  const applyRulesForProject = async (projectId: string, selectedRuleSetIds: string[]) => {
    const preview = await applyProjectRules(projectId, selectedRuleSetIds);
    const refreshed = await fetchDashboard(projectId);
    setDashboard(refreshed);
    setActiveProjectId(projectId);
    return preview;
  };

  const removeProject = async (projectId: string) => {
    if (!dashboard) return;
    setSaveError(null);
    const remaining = dashboard.projects.filter(project => project.id !== projectId);
    await deleteProject(projectId);
    const nextActive = dashboard.active_project.id === projectId ? remaining[0] : dashboard.active_project;
    setDashboard({
      ...dashboard,
      projects: remaining,
      active_project: nextActive
    });
    if (nextActive?.id && nextActive.id !== dashboard.active_project.id) {
      setActiveProjectId(nextActive.id);
    }
  };

  const updateLabel = async (record: DataRecord, field: LabelField, value: string) => {
    if (!dashboard) return;
    setSaving(true);
    setSaveError(null);
    try {
      const updated = await patchRecord(record.id, [
        { field_key: field.key, value, confirmed: true }
      ]);
      setDashboard(current => current ? {
        ...current,
        records: current.records.map(item => (item.id === updated.id ? updated : item))
      } : current);
      setLabelWorkflowNotice('人工标注已保存，并已同步给规则学习。建议查看规则学习建议，预览后可重新自动打标。');
      await refreshDashboard(dashboard.active_project.id);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const updateReportCandidate = async (record: DataRecord, reportCandidate: boolean) => {
    if (!dashboard) return;
    setSaving(true);
    setSaveError(null);
    try {
      const updated = await patchReportCandidate(record.id, reportCandidate);
      setDashboard({
        ...dashboard,
        records: dashboard.records.map(item => (item.id === updated.id ? updated : item))
      });
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const updateBrands = async (record: DataRecord, brands: string[]) => {
    if (!dashboard) return;
    setSaving(true);
    setSaveError(null);
    try {
      const updated = await patchBrands(record.id, brands);
      setDashboard(current => current ? {
        ...current,
        records: current.records.map(item => (item.id === updated.id ? updated : item))
      } : current);
      setLabelWorkflowNotice('品牌人工标注已保存，并已同步给规则学习。');
      await refreshDashboard(dashboard.active_project.id);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const addEvidenceSample = (record: DataRecord) => {
    if (!dashboard) return;
    const latestRule = dashboard.rule_sets.find(rule => dashboard.active_project.selected_rule_set_ids.includes(rule.id))
      ?? dashboard.rule_sets[0];
    const nextSample: EvidenceSample = {
      id: `ev-${Date.now()}`,
      record_id: record.id,
      content: record.content,
      source_rule_set_id: latestRule?.id ?? 'rules-manual',
      source_rule_name: latestRule ? `${latestRule.name} ${latestRule.version}` : '人工新增规则证据',
      label_before: optionLabel(dashboard.label_schema, 'sentiment_type', record.labels.sentiment_type?.auto),
      label_after: optionLabel(dashboard.label_schema, 'sentiment_type', record.labels.sentiment_type?.final),
      keyword_count: record.matched_keywords.length,
      created_at: new Date().toLocaleString('zh-CN', { hour12: false })
    };
    setEvidenceSamples(current => [nextSample, ...current.filter(sample => sample.record_id !== record.id)]);
    setEvidenceNotice(`已加入证据样本，并默认归类到「${nextSample.source_rule_name}」。`);
  };

  const updateEvidenceSample = (sampleId: string, patch: Partial<EvidenceSample>) => {
    setEvidenceSamples(current => current.map(sample => sample.id === sampleId ? { ...sample, ...patch } : sample));
  };

  const deleteEvidenceSample = (sampleId: string) => {
    setEvidenceSamples(current => current.filter(sample => sample.id !== sampleId));
  };

  if (error) {
    return <div className="error-screen">{error}</div>;
  }

  if (!dashboard) {
    return <div className="loading-screen">正在加载舆情标注平台...</div>;
  }

  const baseRecords = dashboard.records
    .filter(record => {
      if (activeFilter === 'unconfirmed') {
        return !Object.values(record.labels).some(label => label.confirmed);
      }
      if (activeFilter === 'negative') {
        return record.labels.sentiment_polarity?.final === 'negative';
      }
      if (activeFilter === 'conflict') {
        return Object.values(record.labels).some(label => label.manual && label.manual !== label.auto);
      }
      if (activeFilter === 'report') {
        return record.report_candidate;
      }
      return true;
    })
    .filter(record => {
      const term = searchTerm.trim();
      if (!term) return true;
      return record.content.includes(term) || record.platform.includes(term) || record.author.includes(term);
    });
  const filteredRecords = applyAdvancedFilters(baseRecords, advancedFilters);
  const visibleRecords = sortRecords(filteredRecords, sortKey, sortDirection);
  const tableStats = buildTableStats(filteredRecords, dashboard.label_schema);
  const platformOptions = uniqueOptions(dashboard.records.map(record => record.platform));
  const brandOptions = uniqueOptions([
    ...dashboard.brand_rules.map(rule => rule.brand),
    ...dashboard.records.flatMap(record => record.brands)
  ]);
  const selectedRecord = visibleRecords.find(record => record.id === selectedRecordId) ?? visibleRecords[0];
  const labelingProjectCount = dashboard.projects.filter(project => project.status === '标注中').length;
  const activeProjectCount = dashboard.projects.filter(project => project.status !== '已交付').length;
  const totalProjectRows = dashboard.projects.reduce((total, project) => total + project.total_count, 0);
  const dueProjectCount = dashboard.projects.filter(project => project.delivery_due && project.status !== '已交付').length;

  return (
    <div className={`platform-shell ${activeView === 'labeling' ? 'is-labeling' : ''} ${sidebarPinned ? 'sidebar-pinned' : ''}`}>
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark" />
          <div>
            <strong>舆情标注平台</strong>
            <span>Sentiment Lab</span>
          </div>
        </div>
        <button
          type="button"
          className="sidebar-toggle"
          aria-pressed={sidebarPinned}
          aria-label={sidebarPinned ? '收起侧边导航' : '展开侧边导航'}
          title={sidebarPinned ? '收起侧边导航' : '展开侧边导航'}
          onClick={() => setSidebarPinned(value => !value)}
        >
          <Menu size={17} />
          <span>{sidebarPinned ? '收起导航' : '展开导航'}</span>
        </button>
        <nav className="nav-list">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                type="button"
                key={item.key}
                className={activeView === item.key ? 'active' : ''}
                onClick={() => setActiveView(item.key)}
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="workspace">
        <header className="workspace-header">
          <div className="project-title-wrap">
            <p className="eyebrow">当前项目 / {dashboard.active_project.rule_version}</p>
            <div className="project-title-row">
              <h1>{dashboard.active_project.name}</h1>
              <div className="project-switch-wrap">
                <button
                  type="button"
                  className="project-switch"
                  aria-expanded={projectMenuOpen}
                  onClick={() => setProjectMenuOpen(value => !value)}
                >
                  切换项目
                  <ChevronDown size={15} />
                </button>
                {projectMenuOpen && (
                  <div className="project-menu" role="menu">
                    {dashboard.projects.map(project => (
                      <button
                        key={project.id}
                        type="button"
                        role="menuitem"
                        className={project.id === dashboard.active_project.id ? 'active' : ''}
                        onClick={() => switchProject(project.id)}
                      >
                        <strong>{project.name}</strong>
                        <span>{project.date_range} / {project.status}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <p className="header-copy">
              {dashboard.active_project.date_range} / 更新于 {dashboard.active_project.updated_at} / 负责人 {dashboard.active_project.owner.name}
            </p>
          </div>
          <div className="user-menu-wrap">
            <button
              type="button"
              className="user-card"
              aria-expanded={userMenuOpen}
              onClick={() => setUserMenuOpen(value => !value)}
            >
              <div className="avatar">{dashboard.user.avatar}</div>
              <div>
                <strong>{dashboard.user.name}</strong>
                <span>{dashboard.user.role}</span>
              </div>
              <ChevronDown size={15} />
            </button>
            {userMenuOpen && (
              <div className="user-menu" role="menu">
                <button type="button" role="menuitem" onClick={() => { setActiveView('users'); setUserMenuOpen(false); }}>
                  <Users size={16} />
                  <span>用户与权限</span>
                </button>
                <button type="button" role="menuitem" onClick={() => setUserMenuOpen(false)}>
                  <Settings size={16} />
                  <span>偏好设置</span>
                </button>
                <button type="button" role="menuitem" onClick={() => setUserMenuOpen(false)}>
                  <LogOut size={16} />
                  <span>退出登录</span>
                </button>
              </div>
            )}
          </div>
        </header>

        <section className="metric-grid">
          {activeView === 'projects' ? (
            <>
              <QuickMetricCard icon={FolderKanban} label="项目管理" value={`${dashboard.projects.length.toLocaleString()} 个`} detail={`${activeProjectCount.toLocaleString()} 个项目仍在推进`} onClick={() => setActiveView('projects')} />
              <QuickMetricCard icon={CheckCircle2} label="人工标注" value={`${labelingProjectCount.toLocaleString()} 个`} detail="点击进入标注工作台" onClick={() => setActiveView('labeling')} />
              <QuickMetricCard icon={UploadCloud} label="数据导入" value={totalProjectRows.toLocaleString()} detail="所有项目累计评论行数" onClick={() => setActiveView('import')} />
              <QuickMetricCard icon={FileText} label="交付跟踪" value={`${dueProjectCount.toLocaleString()} 个`} detail="按项目交付日期跟踪" onClick={() => setActiveView('report')} warning />
            </>
          ) : (
            <>
              <QuickMetricCard icon={FolderKanban} label="项目进度" value={`${dashboard.active_project.progress}%`} detail={`已确认 ${dashboard.active_project.confirmed_count.toLocaleString()} / ${dashboard.active_project.total_count.toLocaleString()}`} onClick={() => setActiveView('projects')} progress={dashboard.active_project.progress} />
              <QuickMetricCard icon={Sparkles} label="自动打标" value={dashboard.label_schema.name} detail={`${dashboard.label_schema.fields.length} 个动态标签字段`} onClick={() => setActiveView('auto')} />
              <QuickMetricCard icon={Lightbulb} label="规则学习" value={`${dashboard.suggestions.length} 条`} detail="来自本轮人工修改差异" onClick={() => setActiveView('learning')} warning />
              <QuickMetricCard icon={BookOpen} label="在线报告" value={dashboard.report.status} detail={`${dashboard.report.version} / 可在线确认`} onClick={() => setActiveView('report')} />
            </>
          )}
        </section>

        {activeView !== 'labeling' && (
          <WorkbenchView
            view={activeView}
            dashboard={dashboard}
            onNavigate={setActiveView}
            onProjectSwitch={switchProject}
            onProjectCreate={addProject}
            onProjectUpdate={editProject}
            onProjectDelete={removeProject}
            onRulePreview={previewRulesForProject}
            onRuleApply={applyRulesForProject}
            onDashboardRefresh={refreshDashboard}
            evidenceSamples={evidenceSamples}
            onEvidenceUpdate={updateEvidenceSample}
            onEvidenceDelete={deleteEvidenceSample}
          />
        )}

        {activeView === 'labeling' && (
          <section className="labeling-layout">
            <div className="labeling-top">
              <div>
                <h2>人工标注工作台</h2>
                <p>表格区域已优先铺开，适合连续下拉选择、批量校正和横向比对。</p>
                <div className="label-progress-pill">
                  <span>{dashboard.active_project.status}</span>
                  <div className="progress-chip"><i style={{ width: `${dashboard.active_project.progress}%` }} /></div>
                  <strong>{dashboard.active_project.progress}%</strong>
                </div>
              </div>
              <LabelingInsights dashboard={dashboard} onNavigate={setActiveView} />
            </div>
            <div className="labeling-main">
              <div className="table-toolbar">
                <div className="view-tabs">
                  <button type="button" className={activeFilter === 'all' ? 'active' : ''} onClick={() => setActiveFilter('all')}>全部</button>
                  <button type="button" className={activeFilter === 'unconfirmed' ? 'active' : ''} onClick={() => setActiveFilter('unconfirmed')}>未确认</button>
                  <button type="button" className={activeFilter === 'negative' ? 'active' : ''} onClick={() => setActiveFilter('negative')}>负面</button>
                  <button type="button" className={activeFilter === 'conflict' ? 'active' : ''} onClick={() => setActiveFilter('conflict')}>规则冲突</button>
                  <button type="button" className={activeFilter === 'report' ? 'active' : ''} onClick={() => setActiveFilter('report')}>报告候选</button>
                </div>
                <div className="search-box">
                  <Search size={16} />
                  <input value={searchTerm} onChange={event => setSearchTerm(event.target.value)} placeholder="搜索内容、平台、作者" />
                </div>
              </div>
              <TableFilters
                filters={advancedFilters}
                onChange={setAdvancedFilters}
                schema={dashboard.label_schema}
                platformOptions={platformOptions}
                brandOptions={brandOptions}
                sortKey={sortKey}
                sortDirection={sortDirection}
                onSortKeyChange={setSortKey}
                onSortDirectionChange={setSortDirection}
              />
              <TableStats stats={tableStats} />
              <div className="save-strip">
                <span className={saving ? 'status-saving' : 'status-saved'}>
                  {saving ? '自动保存中...' : saveError ? '保存失败' : '已保存'}
                </span>
                <span>{saveError ?? '人工确认以黄色点标记，后续规则重跑不会覆盖。'}</span>
                <button type="button" onClick={() => setActiveView('auto')}><RefreshCw size={16} /> 重新打标未确认数据</button>
                {selectedRecord && <span className="selected-record">当前：{selectedRecord.author} / {selectedRecord.platform}</span>}
              </div>
              {labelWorkflowNotice && (
                <div className="import-notice workflow-notice">
                  <span>{labelWorkflowNotice}</span>
                  <button type="button" className="tiny-action" onClick={() => setActiveView('learning')}>查看规则学习</button>
                  <button type="button" className="tiny-action" onClick={() => setActiveView('auto')}>继续自动打标</button>
                  <button type="button" className="tiny-action" onClick={() => setActiveView('report')}>进入报告</button>
                </div>
              )}
              <LabelGrid
                records={visibleRecords}
                schema={dashboard.label_schema}
                onChange={updateLabel}
                onReportCandidateChange={updateReportCandidate}
                onBrandsChange={updateBrands}
                onEvidenceAdd={addEvidenceSample}
                brandOptions={brandOptions}
                selectedRecordId={selectedRecord?.id ?? null}
                onSelect={setSelectedRecordId}
              />
              {evidenceNotice && <div className="evidence-toast">{evidenceNotice}</div>}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function LabelingInsights({
  dashboard,
  onNavigate
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
}) {
  const topSuggestion = dashboard.suggestions[0];

  return (
    <div className="insight-strip" aria-label="标注辅助信息">
      {topSuggestion && (
        <button type="button" className="mini-insight warning" onClick={() => onNavigate('learning')}>
          <div>
            <h3><Lightbulb size={16} /> 规则学习建议</h3>
            <strong>{topSuggestion.title}</strong>
            <span>{topSuggestion.evidence_count} 条证据</span>
          </div>
          <em>查看</em>
        </button>
      )}
      <button type="button" className="mini-insight" onClick={() => onNavigate('wordcloud')}>
        <div>
          <h3><Cloud size={16} /> 生成词云</h3>
          <strong>评论内容 / 视频内容</strong>
          <span>按客户保存跨项目模板</span>
        </div>
        <em>生成</em>
      </button>
    </div>
  );
}

function TableFilters({
  filters,
  onChange,
  schema,
  platformOptions,
  brandOptions,
  sortKey,
  sortDirection,
  onSortKeyChange,
  onSortDirectionChange
}: {
  filters: AdvancedFilters;
  onChange: (filters: AdvancedFilters) => void;
  schema: LabelSchema;
  platformOptions: string[];
  brandOptions: string[];
  sortKey: SortKey;
  sortDirection: SortDirection;
  onSortKeyChange: (key: SortKey) => void;
  onSortDirectionChange: (direction: SortDirection) => void;
}) {
  const update = (key: keyof AdvancedFilters, value: string) => onChange({ ...filters, [key]: value });

  return (
    <div className="filter-panel">
      <label>
        <span>平台</span>
        <select value={filters.platform} onChange={event => update('platform', event.target.value)}>
          <option value="">全部平台</option>
          {platformOptions.map(platform => <option key={platform} value={platform}>{platform}</option>)}
        </select>
      </label>
      <label>
        <span>点赞 ≥</span>
        <input inputMode="numeric" value={filters.minLikes} onChange={event => update('minLikes', event.target.value)} placeholder="不限" />
      </label>
      <label>
        <span>回复 ≥</span>
        <input inputMode="numeric" value={filters.minReplies} onChange={event => update('minReplies', event.target.value)} placeholder="不限" />
      </label>
      <label>
        <span>评论类型</span>
        <select value={filters.commentType} onChange={event => update('commentType', event.target.value)}>
          <option value="">全部类型</option>
          {['长评论', '提及竞品', '普通内容', '@他人', '符号表情'].map(type => <option key={type} value={type}>{type}</option>)}
        </select>
      </label>
      <FilterSelect label="正负面" fieldKey="sentiment_polarity" schema={schema} value={filters.sentimentPolarity} onChange={value => update('sentimentPolarity', value)} />
      <FilterSelect label="认知" fieldKey="cognition" schema={schema} value={filters.cognition} onChange={value => update('cognition', value)} />
      <FilterSelect label="情绪" fieldKey="sentiment_type" schema={schema} value={filters.sentimentType} onChange={value => update('sentimentType', value)} />
      <FilterSelect label="行动" fieldKey="action" schema={schema} value={filters.action} onChange={value => update('action', value)} />
      <label>
        <span>品牌</span>
        <select value={filters.brand} onChange={event => update('brand', event.target.value)}>
          <option value="">全部品牌</option>
          {brandOptions.map(brand => <option key={brand} value={brand}>{brand}</option>)}
        </select>
      </label>
      <label>
        <span>报告统计</span>
        <select value={filters.reportStatus} onChange={event => update('reportStatus', event.target.value)}>
          <option value="">全部</option>
          <option value="included">纳入</option>
          <option value="excluded">排除</option>
        </select>
      </label>
      <label className="sort-control">
        <span>排序</span>
        <select value={sortKey} onChange={event => onSortKeyChange(event.target.value as SortKey)}>
          <option value="none">默认顺序</option>
          <option value="comment_total">评论互动合计</option>
          <option value="comment_likes">评论点赞</option>
          <option value="comment_replies">评论回复</option>
          <option value="comment_publish_time">评论发布时间</option>
          <option value="source_publish_time">内容发布时间</option>
          <option value="source_comments">内容评论数</option>
          <option value="source_likes">内容点赞数</option>
          <option value="source_favorites">内容收藏数</option>
          <option value="source_shares">内容分享数</option>
        </select>
      </label>
      <label>
        <span>方向</span>
        <select value={sortDirection} onChange={event => onSortDirectionChange(event.target.value as SortDirection)}>
          <option value="desc">从高到低 / 新到旧</option>
          <option value="asc">从低到高 / 旧到新</option>
        </select>
      </label>
      <button type="button" className="clear-filters" onClick={() => onChange(defaultAdvancedFilters)}>清空筛选</button>
    </div>
  );
}

function FilterSelect({
  label,
  fieldKey,
  schema,
  value,
  onChange
}: {
  label: string;
  fieldKey: string;
  schema: LabelSchema;
  value: string;
  onChange: (value: string) => void;
}) {
  const field = schema.fields.find(item => item.key === fieldKey);
  return (
    <label>
      <span>{label}</span>
      <select value={value} onChange={event => onChange(event.target.value)}>
        <option value="">全部</option>
        {field?.options.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
    </label>
  );
}

function TableStats({ stats }: { stats: ReturnType<typeof buildTableStats> }) {
  return (
    <div className="table-stats">
      <StatBlock title="当前结果" value={stats.total.toLocaleString()} detail={`纳入 ${stats.reportIncluded.toLocaleString()} / 排除 ${stats.reportExcluded.toLocaleString()}`} />
      <StatBlock title="正负面" value={stats.topSentiment} detail={stats.sentimentSummary} />
      <StatBlock title="认知" value={stats.topCognition} detail={stats.cognitionSummary} />
      <StatBlock title="情绪" value={stats.topEmotion} detail={stats.emotionSummary} />
      <StatBlock title="行动" value={stats.topAction} detail={stats.actionSummary} />
    </div>
  );
}

function StatBlock({ title, value, detail }: { title: string; value: string; detail: string }) {
  return (
    <div className="stat-block">
      <span>{title}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function QuickMetricCard({
  icon: Icon,
  label,
  value,
  detail,
  onClick,
  warning = false,
  progress
}: {
  icon: React.ComponentType<React.SVGProps<SVGSVGElement> & { size?: number }>;
  label: string;
  value: string;
  detail: string;
  onClick: () => void;
  warning?: boolean;
  progress?: number;
}) {
  return (
    <button type="button" className={`metric-card ${warning ? 'warning' : ''}`} onClick={onClick}>
      <Icon className="metric-bg-icon" size={54} />
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
      {typeof progress === 'number' && <div className="mini-progress"><i style={{ width: `${progress}%` }} /></div>}
    </button>
  );
}

function LabelGrid({
  records,
  schema,
  onChange,
  onReportCandidateChange,
  onBrandsChange,
  onEvidenceAdd,
  brandOptions,
  selectedRecordId,
  onSelect
}: {
  records: DataRecord[];
  schema: LabelSchema;
  onChange: (record: DataRecord, field: LabelField, value: string) => void;
  onReportCandidateChange: (record: DataRecord, reportCandidate: boolean) => void;
  onBrandsChange: (record: DataRecord, brands: string[]) => void;
  onEvidenceAdd: (record: DataRecord) => void;
  brandOptions: string[];
  selectedRecordId: string | null;
  onSelect: (recordId: string) => void;
}) {
  const [expandedRecordIds, setExpandedRecordIds] = React.useState<Set<string>>(new Set());

  const toggleExpanded = (recordId: string) => {
    setExpandedRecordIds(previous => {
      const next = new Set(previous);
      if (next.has(recordId)) {
        next.delete(recordId);
      } else {
        next.add(recordId);
      }
      return next;
    });
  };

  if (records.length === 0) {
    return (
      <div className="empty-state">
        <strong>没有匹配的数据</strong>
        <span>调整筛选条件或搜索词后再试。</span>
      </div>
    );
  }

  return (
    <div className="grid-frame">
      <table className="label-grid">
        <thead>
          <tr>
            <th className="id-col">评论ID</th>
            <th>平台</th>
            <th className="sticky-col content-col">内容</th>
            <th>互动数据</th>
            <th>正负面</th>
            <th>认知</th>
            <th>情绪</th>
            <th>行动</th>
            <th>品牌</th>
            <th>报告统计</th>
            <th className="source-col">内容数据</th>
          </tr>
        </thead>
        <tbody>
          {records.map(record => {
            const isLongContent = record.content.length > 100;
            const isExpanded = expandedRecordIds.has(record.id);
            const typeTags = commentTypeTags(record);
            return (
              <tr
                key={record.id}
                className={selectedRecordId === record.id ? 'selected-row' : ''}
                onClick={() => onSelect(record.id)}
              >
                <td className="id-col">
                  {Object.values(record.labels).some(label => label.confirmed) ? (
                    <span className="manual-dot" title="本行包含人工确认标签" />
                  ) : (
                    <span className="empty-dot" />
                  )}
                  <strong>{tailId(record.id, 6)}</strong>
                  <small>{Object.values(record.labels).some(label => label.confirmed) ? '已确认' : '待确认'}</small>
                </td>
                <td>{record.platform}</td>
                <td className="sticky-col content-col">
                  <div className="comment-meta">
                    <strong>{record.author}</strong>
                    <span>{record.publish_time}</span>
                  </div>
                  <div className="comment-types">
                    {typeTags.map(tag => <em key={tag}>{tag}</em>)}
                  </div>
                  <p className={isLongContent && !isExpanded ? 'long-comment' : ''}>
                    <HighlightedText text={record.content} keywords={record.matched_keywords} />
                  </p>
                  {isLongContent && (
                    <button
                      type="button"
                      className="content-toggle"
                      onClick={event => {
                        event.stopPropagation();
                        toggleExpanded(record.id);
                      }}
                    >
                      {isExpanded ? '收起长文' : '展开长文'}
                    </button>
                  )}
                </td>
                <td>
                  <strong>{record.engagement.likes.toLocaleString()}</strong>
                  <small>点赞</small>
                  <small>{record.engagement.replies.toLocaleString()} 回复</small>
                </td>
                <LabelCell record={record} schema={schema} fieldKey="sentiment_polarity" onChange={onChange} />
                <LabelCell record={record} schema={schema} fieldKey="cognition" onChange={onChange} />
                <LabelCell record={record} schema={schema} fieldKey="sentiment_type" onChange={onChange} />
                <LabelCell record={record} schema={schema} fieldKey="action" onChange={onChange} />
                <td>
                  <BrandEditor record={record} brandOptions={brandOptions} onChange={onBrandsChange} />
                </td>
                <td>
                  <label className="report-check" onClick={event => event.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={record.report_candidate}
                      onChange={event => onReportCandidateChange(record, event.target.checked)}
                    />
                    <span>{record.report_candidate ? '纳入' : '排除'}</span>
                  </label>
                  <button
                    type="button"
                    className="evidence-add"
                    onClick={event => {
                      event.stopPropagation();
                      onEvidenceAdd(record);
                    }}
                  >
                    <Plus size={13} /> 证据
                  </button>
                </td>
                <td className="source-col">
                  <strong>{record.source_content.id ? tailId(record.source_content.id, 4) : '-'}</strong>
                  {record.source_content.url && (
                    <a href={record.source_content.url} target="_blank" rel="noreferrer" onClick={event => event.stopPropagation()}>
                      内容链接
                    </a>
                  )}
                  <small>话题：{formatTopics(record.source_content.topics).join('、') || '-'}</small>
                  <small>发布者：{record.source_content.author ?? '-'}</small>
                  <small>发布时间：{record.source_content.publish_time ?? '-'}</small>
                  <small>评论 {record.source_content.comments.toLocaleString()} / 点赞 {record.source_content.likes.toLocaleString()} / 收藏 {record.source_content.favorites.toLocaleString()} / 分享 {record.source_content.shares.toLocaleString()}</small>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function commentTypeTags(record: DataRecord): string[] {
  const tags = new Set<string>();
  if (record.content.length > 100) tags.add('长评论');
  if (record.brands.length > 1) tags.add('提及竞品');
  if (record.content.includes('@')) tags.add('@他人');
  if (/[\u{1F300}-\u{1FAFF}]/u.test(record.content) || /^[\p{P}\p{S}\s]+$/u.test(record.content)) tags.add('符号表情');
  if (record.comment_type !== '普通内容' || tags.size === 0) tags.add(record.comment_type);
  if (tags.size === 0) tags.add('普通内容');
  return Array.from(tags);
}

function BrandEditor({
  record,
  brandOptions,
  onChange
}: {
  record: DataRecord;
  brandOptions: string[];
  onChange: (record: DataRecord, brands: string[]) => void;
}) {
  const [draft, setDraft] = React.useState('');
  const canAdd = record.brands.length < 5;

  const addBrand = (brand: string) => {
    const normalized = brand.trim();
    if (!normalized || record.brands.includes(normalized) || !canAdd) return;
    onChange(record, [...record.brands, normalized].slice(0, 5));
    setDraft('');
  };

  const removeBrand = (brand: string) => {
    onChange(record, record.brands.filter(item => item !== brand));
  };

  return (
    <div className="brand-editor" onClick={event => event.stopPropagation()}>
      <div className="brand-tags editable">
        {record.brands.slice(0, 5).map(brand => (
          <button type="button" key={brand} title="移除品牌" onClick={() => removeBrand(brand)}>
            <span>{brand}</span>
            <b>×</b>
          </button>
        ))}
      </div>
      <div className="brand-input-row">
        <input
          list={`brand-options-${record.id}`}
          value={draft}
          disabled={!canAdd}
          placeholder={canAdd ? '添加品牌' : '最多5个'}
          onChange={event => setDraft(event.target.value)}
          onKeyDown={event => {
            if (event.key === 'Enter') {
              event.preventDefault();
              addBrand(draft);
            }
          }}
          onBlur={() => addBrand(draft)}
        />
        <datalist id={`brand-options-${record.id}`}>
          {brandOptions.map(brand => <option key={brand} value={brand} />)}
        </datalist>
      </div>
      <small>{record.brands.length}/5</small>
    </div>
  );
}

function LabelCell({
  record,
  schema,
  fieldKey,
  onChange
}: {
  record: DataRecord;
  schema: LabelSchema;
  fieldKey: string;
  onChange: (record: DataRecord, field: LabelField, value: string) => void;
}) {
  const field = schema.fields.find(item => item.key === fieldKey);
  if (!field) return <td>-</td>;
  const label = record.labels[field.key];
  const options = filteredOptions(field, record);
  return (
    <td>
      <div className="cell-editor" title={labelTooltip(label, schema, field.key)}>
        {label?.confirmed && <span className="manual-dot" />}
        <select
          value={label?.final ?? ''}
          onClick={event => event.stopPropagation()}
          onChange={event => onChange(record, field, event.target.value)}
        >
          <option value="">未选择</option>
          {options.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
        <ChevronDown size={14} />
      </div>
      <small>自动：{optionLabel(schema, field.key, label?.auto)}</small>
    </td>
  );
}

function HighlightedText({ text, keywords }: { text: string; keywords: string[] }) {
  const safeKeywords = keywords.filter(Boolean).sort((a, b) => b.length - a.length);
  if (!safeKeywords.length) return <>{text}</>;
  const pattern = new RegExp(`(${safeKeywords.map(escapeRegExp).join('|')})`, 'g');
  return (
    <>
      {text.split(pattern).map((part, index) => (
        safeKeywords.includes(part) ? <mark key={`${part}-${index}`}>{part}</mark> : <React.Fragment key={`${part}-${index}`}>{part}</React.Fragment>
      ))}
    </>
  );
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function WorkbenchView({
  view,
  dashboard,
  onNavigate,
  onProjectSwitch,
  onProjectCreate,
  onProjectUpdate,
  onProjectDelete,
  onRulePreview,
  onRuleApply,
  onDashboardRefresh,
  evidenceSamples,
  onEvidenceUpdate,
  onEvidenceDelete
}: {
  view: string;
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
  onProjectSwitch: (projectId: string) => void;
  onProjectCreate: (payload: ProjectPayload) => Promise<ProjectSummary>;
  onProjectUpdate: (projectId: string, payload: ProjectPayload) => Promise<ProjectSummary>;
  onProjectDelete: (projectId: string) => Promise<void>;
  onRulePreview: (projectId: string, selectedRuleSetIds: string[]) => Promise<RuleImpactPreview>;
  onRuleApply: (projectId: string, selectedRuleSetIds: string[]) => Promise<RuleImpactPreview>;
  onDashboardRefresh: (projectId?: string) => Promise<DashboardResponse>;
  evidenceSamples: EvidenceSample[];
  onEvidenceUpdate: (sampleId: string, patch: Partial<EvidenceSample>) => void;
  onEvidenceDelete: (sampleId: string) => void;
}) {
  if (view === 'projects') {
    return (
      <ProjectsView
        dashboard={dashboard}
        onNavigate={onNavigate}
        onProjectSwitch={onProjectSwitch}
        onProjectCreate={onProjectCreate}
        onProjectUpdate={onProjectUpdate}
        onProjectDelete={onProjectDelete}
        onRulePreview={onRulePreview}
        onRuleApply={onRuleApply}
      />
    );
  }
  if (view === 'import') return <ImportView dashboard={dashboard} onNavigate={onNavigate} onDashboardRefresh={onDashboardRefresh} />;
  if (view === 'auto') {
    return (
      <AutoLabelView
        dashboard={dashboard}
        onNavigate={onNavigate}
        onRulePreview={onRulePreview}
        onRuleApply={onRuleApply}
        onDashboardRefresh={onDashboardRefresh}
      />
    );
  }
  if (view === 'learning') {
    return (
      <RuleLearningView
        dashboard={dashboard}
        evidenceSamples={evidenceSamples}
        onRulePreview={onRulePreview}
        onRuleApply={onRuleApply}
        onEvidenceUpdate={onEvidenceUpdate}
        onEvidenceDelete={onEvidenceDelete}
      />
    );
  }
  if (view === 'wordcloud') return <WordCloudView dashboard={dashboard} />;
  if (view === 'report') return <ReportView dashboard={dashboard} />;
  if (view === 'users') return <UsersView dashboard={dashboard} />;
  return null;
}

function ProjectsView({
  dashboard,
  onNavigate,
  onProjectSwitch,
  onProjectCreate,
  onProjectUpdate,
  onProjectDelete,
  onRulePreview,
  onRuleApply
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
  onProjectSwitch: (projectId: string) => void;
  onProjectCreate: (payload: ProjectPayload) => Promise<ProjectSummary>;
  onProjectUpdate: (projectId: string, payload: ProjectPayload) => Promise<ProjectSummary>;
  onProjectDelete: (projectId: string) => Promise<void>;
  onRulePreview: (projectId: string, selectedRuleSetIds: string[]) => Promise<RuleImpactPreview>;
  onRuleApply: (projectId: string, selectedRuleSetIds: string[]) => Promise<RuleImpactPreview>;
}) {
  const activeProject = dashboard.active_project;
  const enabledPlatformNames = projectPlatformOptions.filter(platform => platform.enabled).map(platform => platform.name);
  const defaultRuleSetIds = dashboard.rule_sets.slice(0, 1).map(ruleSet => ruleSet.id);
  const blankDraft: ProjectPayload = {
    name: '',
    client: '',
    brand: '',
    description: '',
    objective: '',
    platforms: ['抖音'],
    date_range: joinDateRange(todayISO(), todayISO()),
    delivery_due: '',
    owner_id: dashboard.user.id,
    label_schema: labelSchemaOptions[0]?.name ?? 'A2 三层标签体系',
    rule_version: defaultRuleSetIds
      .map(id => dashboard.rule_sets.find(ruleSet => ruleSet.id === id)?.name)
      .filter(Boolean)
      .join(' + '),
    report_template: '默认报告模板',
    export_pattern: activeProject.export_pattern || dashboard.export_presets[0]?.pattern || '{project}_{date}_{version}_{format}',
    selected_rule_set_ids: defaultRuleSetIds,
    priority: '中',
    status: '待导入数据'
  };
  const [projectStatusFilter, setProjectStatusFilter] = React.useState('全部');
  const [projectOwnerFilter, setProjectOwnerFilter] = React.useState('全部');
  const [projectSearch, setProjectSearch] = React.useState('');
  const [projectSort, setProjectSort] = React.useState('updated_desc');
  const [editingProjectId, setEditingProjectId] = React.useState<string | null>(null);
  const [draft, setDraft] = React.useState<ProjectPayload>(blankDraft);
  const [projectModalOpen, setProjectModalOpen] = React.useState(false);
  const [projectActionError, setProjectActionError] = React.useState<string | null>(null);
  const [projectSaving, setProjectSaving] = React.useState(false);
  void onRulePreview;
  void onRuleApply;
  const statusOptions = ['全部', ...Array.from(new Set(dashboard.projects.map(project => project.status)))];
  const reportTemplateOptions = Array.from(new Set([
    draft.report_template,
    ...dashboard.report_templates.map(template => template.name),
    '默认报告模板'
  ].filter(Boolean)));
  const ownerOptions = ['全部', ...dashboard.users.map(user => user.id)];
  const visibleProjects = dashboard.projects
    .filter(project => {
      const term = projectSearch.trim().toLowerCase();
      const searchable = [
        project.name,
        project.client,
        project.brand,
        project.description,
        project.objective,
        project.owner.name,
        project.status,
        project.platforms.join(' ')
      ].join(' ').toLowerCase();
      if (projectStatusFilter !== '全部' && project.status !== projectStatusFilter) return false;
      if (projectOwnerFilter !== '全部' && project.owner.id !== projectOwnerFilter) return false;
      if (term && !searchable.includes(term)) return false;
      return true;
    })
    .sort((left, right) => {
      if (projectSort === 'progress_desc') return right.progress - left.progress;
      if (projectSort === 'progress_asc') return left.progress - right.progress;
      if (projectSort === 'due_asc') return (left.delivery_due || '9999-99-99').localeCompare(right.delivery_due || '9999-99-99');
      if (projectSort === 'priority') return priorityRank(right.priority) - priorityRank(left.priority);
      return right.updated_at.localeCompare(left.updated_at);
    });
  const editingProject = dashboard.projects.find(project => project.id === editingProjectId) ?? null;
  const totalProjectRows = dashboard.projects.reduce((total, project) => total + project.total_count, 0);
  const totalConfirmedRows = dashboard.projects.reduce((total, project) => total + project.confirmed_count, 0);
  const highPriorityCount = dashboard.projects.filter(project => project.priority === '高').length;
  const dueSoonCount = dashboard.projects.filter(project => project.delivery_due && project.delivery_due <= '2026-06-10' && project.status !== '已交付').length;
  const resetProjectFilters = () => {
    setProjectSearch('');
    setProjectStatusFilter('全部');
    setProjectOwnerFilter('全部');
    setProjectSort('updated_desc');
  };

  const projectToPayload = (project: ProjectSummary): ProjectPayload => ({
    name: project.name,
    client: project.client,
    brand: project.brand,
    description: project.description,
    objective: project.objective,
    platforms: project.platforms,
    date_range: project.date_range,
    delivery_due: project.delivery_due,
    owner_id: project.owner.id,
    label_schema: project.label_schema,
    rule_version: project.rule_version,
    report_template: project.report_template,
    export_pattern: project.export_pattern,
    selected_rule_set_ids: project.selected_rule_set_ids,
    priority: project.priority,
    status: project.status
  });

  const changeDraft = (key: keyof ProjectPayload, value: string | string[]) => {
    setDraft(current => ({ ...current, [key]: value }));
  };

  const toggleDraftPlatform = (platform: string) => {
    setDraft(current => {
      const nextPlatforms = current.platforms.includes(platform)
        ? current.platforms.filter(item => item !== platform)
        : [...current.platforms, platform];
      return { ...current, platforms: nextPlatforms };
    });
  };

  const toggleDraftRuleSet = (ruleSetId: string) => {
    setDraft(current => {
      const nextRuleSetIds = current.selected_rule_set_ids.includes(ruleSetId)
        ? current.selected_rule_set_ids.filter(item => item !== ruleSetId)
        : [...current.selected_rule_set_ids, ruleSetId];
      return {
        ...current,
        selected_rule_set_ids: nextRuleSetIds,
        rule_version: nextRuleSetIds
          .map(id => dashboard.rule_sets.find(ruleSet => ruleSet.id === id)?.name)
          .filter(Boolean)
          .join(' + ')
      };
    });
  };

  const startCreate = () => {
    setEditingProjectId(null);
    setDraft(blankDraft);
    setProjectActionError(null);
    setProjectModalOpen(true);
  };

  const startEdit = (project: ProjectSummary) => {
    setEditingProjectId(project.id);
    setDraft(projectToPayload(project));
    setProjectActionError(null);
    setProjectModalOpen(true);
  };

  const copyProject = (project: ProjectSummary) => {
    setEditingProjectId(null);
    setDraft({
      ...projectToPayload(project),
      name: `${project.name} 副本`,
      status: '项目配置中'
    });
    setProjectActionError(null);
    setProjectModalOpen(true);
  };

  const submitProject = async () => {
    setProjectSaving(true);
    setProjectActionError(null);
    try {
      if (!draft.platforms.length) {
        throw new Error('至少选择一个数据平台');
      }
      let savedProject: ProjectSummary;
      if (editingProjectId) {
        savedProject = await onProjectUpdate(editingProjectId, draft);
      } else {
        savedProject = await onProjectCreate(draft);
      }
      setEditingProjectId(null);
      setDraft(blankDraft);
      setProjectModalOpen(false);
      if (!editingProjectId && savedProject.total_count === 0) {
        window.setTimeout(() => {
          if (window.confirm('这个项目还没有导入数据，是否现在进入数据导入？')) {
            onNavigate('import');
          }
        }, 100);
      }
    } catch (err) {
      setProjectActionError(err instanceof Error ? err.message : '项目保存失败');
    } finally {
      setProjectSaving(false);
    }
  };

  const deleteProject = async (project: ProjectSummary) => {
    if (dashboard.projects.length <= 1) {
      setProjectActionError('至少需要保留一个项目');
      return;
    }
    if (!window.confirm(`确认删除「${project.name}」吗？这个操作会从项目列表移除它。`)) {
      return;
    }
    setProjectSaving(true);
    setProjectActionError(null);
    try {
      await onProjectDelete(project.id);
      if (editingProjectId === project.id) startCreate();
    } catch (err) {
      setProjectActionError(err instanceof Error ? err.message : '项目删除失败');
    } finally {
      setProjectSaving(false);
    }
  };

  return (
    <section className="workbench-view">
      <ViewHeader
        title="项目管理"
        copy="这里管理所有舆情项目。项目配置、切换、复制和删除都从项目列表进入。"
        action="新建项目"
        onAction={startCreate}
      />
      <div className="project-management-grid">
        <div className="data-table-card">
          <div className="table-card-head">
            <h3>项目列表</h3>
            <span>共有 {dashboard.projects.length.toLocaleString()} 个项目，当前显示 {visibleProjects.length.toLocaleString()} 个</span>
          </div>
          <div className="project-overview-strip">
            <StatBlock title="项目总数" value={dashboard.projects.length.toLocaleString()} detail={`${visibleProjects.length} 个符合筛选`} />
            <StatBlock title="总数据量" value={totalProjectRows.toLocaleString()} detail="所有项目累计行数" />
            <StatBlock title="确认总量" value={totalConfirmedRows.toLocaleString()} detail="人工确认累计" />
            <StatBlock title="高优先级" value={highPriorityCount.toLocaleString()} detail={`${dueSoonCount} 个近期交付`} />
          </div>
          <div className="project-list-toolbar">
            <div className="project-search-box">
              <Search size={15} />
              <input value={projectSearch} onChange={event => setProjectSearch(event.target.value)} placeholder="搜索项目、客户、品牌、负责人" />
            </div>
            <div className="project-filter-tabs">
              {statusOptions.map(status => (
                <button
                  key={status}
                  type="button"
                  className={projectStatusFilter === status ? 'active' : ''}
                  onClick={() => setProjectStatusFilter(status)}
                >
                  {status}
                </button>
              ))}
            </div>
            <div className="project-list-controls">
              <select value={projectOwnerFilter} onChange={event => setProjectOwnerFilter(event.target.value)}>
                {ownerOptions.map(ownerId => (
                  <option key={ownerId} value={ownerId}>
                    {ownerId === '全部' ? '全部负责人' : dashboard.users.find(user => user.id === ownerId)?.name ?? ownerId}
                  </option>
                ))}
              </select>
              <select value={projectSort} onChange={event => setProjectSort(event.target.value)}>
                <option value="updated_desc">最近更新</option>
                <option value="priority">优先级最高</option>
                <option value="due_asc">交付日最近</option>
                <option value="progress_desc">进度最高</option>
                <option value="progress_asc">进度最低</option>
              </select>
              <button type="button" className="secondary-action" onClick={resetProjectFilters}>重置筛选</button>
              <button type="button" className="primary-action" onClick={startCreate}>新建项目</button>
            </div>
          </div>
          <table className="simple-table">
            <thead>
              <tr><th>项目</th><th>客户/品牌</th><th>平台</th><th>负责人</th><th>交付/优先级</th><th>状态</th><th>进度</th><th>操作</th></tr>
            </thead>
            <tbody>
              {visibleProjects.length > 0 ? visibleProjects.map(project => (
                <tr key={project.id} className={project.id === activeProject.id ? 'active-row' : ''}>
                  <td><strong>{project.name}</strong><small>{project.created_at} 创建 / 更新 {project.updated_at}</small></td>
                  <td className="project-client-cell">
                    <strong>{project.client || '未填写客户'} / {project.brand || '未填写品牌'}</strong>
                    <small>{readableRuleSetNames(project, dashboard).join('、') || '未选择规则库'}</small>
                  </td>
                  <td><div className="project-mini-tags">{project.platforms.map(platform => <span key={platform}>{platform}</span>)}</div></td>
                  <td>{project.owner.name}</td>
                  <td>{project.delivery_due || '待定'}<small>{project.priority}优先级</small></td>
                  <td><span className="status-pill">{project.status}</span></td>
                  <td>{project.progress}%</td>
                  <td>
                    <div className="project-row-actions">
                      <button type="button" className="tiny-action" onClick={() => onProjectSwitch(project.id)}>打开</button>
                      <button type="button" className="tiny-action" onClick={() => startEdit(project)}>配置</button>
                      <button type="button" className="tiny-action" onClick={() => onNavigate('labeling')}>标注</button>
                      <button type="button" className="tiny-action" onClick={() => copyProject(project)}>复制</button>
                      <button
                        type="button"
                        className="tiny-action danger-action"
                        disabled={dashboard.projects.length <= 1 || projectSaving}
                        onClick={() => deleteProject(project)}
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={8}>
                    <div className="project-empty-state">
                      <strong>没有符合条件的项目</strong>
                      <span>可以重置筛选查看全部项目，或直接新建一个项目。</span>
                      <div>
                        <button type="button" className="secondary-action" onClick={resetProjectFilters}>重置筛选</button>
                        <button type="button" className="primary-action" onClick={startCreate}>新建项目</button>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      {projectModalOpen && (
        <div className="modal-backdrop" role="presentation" onMouseDown={() => setProjectModalOpen(false)}>
          <div className="project-modal" role="dialog" aria-modal="true" aria-label={editingProject ? '编辑项目' : '新建项目'} onMouseDown={event => event.stopPropagation()}>
            <div className="modal-head">
              <div>
                <span>项目配置</span>
                <h3>{editingProject ? '编辑项目' : '新建项目'}</h3>
              </div>
              <button type="button" className="icon-button" aria-label="关闭" onClick={() => setProjectModalOpen(false)}>×</button>
            </div>
        <div className="new-project-panel">
          <h3>{editingProject ? '编辑项目' : '新建项目'}</h3>
          <div className="form-section">
            <h4>项目相关信息</h4>
          <label><span>项目名称</span><input value={draft.name} onChange={event => changeDraft('name', event.target.value)} placeholder="例如：某品牌舆情分析项目" /></label>
          <label><span>客户</span><input value={draft.client} onChange={event => changeDraft('client', event.target.value)} placeholder="客户名" /></label>
          <label><span>品牌</span><input value={draft.brand} onChange={event => changeDraft('brand', event.target.value)} placeholder="品牌或多品牌" /></label>
          <label><span>项目说明</span><textarea value={draft.description} onChange={event => changeDraft('description', event.target.value)} placeholder="这次项目的背景、范围、需要注意的问题" /></label>
          <label><span>分析目标</span><textarea value={draft.objective} onChange={event => changeDraft('objective', event.target.value)} placeholder="例如：识别正负向、竞品提及、风险行动倾向" /></label>
          </div>
          <div className="form-section">
            <h4>数据相关信息</h4>
          <div className="platform-check-grid">
            <span>数据平台</span>
            <div>
              {projectPlatformOptions.map(platform => (
                <label key={platform.name} className={!platform.enabled ? 'disabled-option' : ''} title={platform.description}>
                  <input type="checkbox" disabled={!platform.enabled} checked={draft.platforms.includes(platform.name)} onChange={() => toggleDraftPlatform(platform.name)} />
                  <span>{platform.name}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="date-range-grid">
            <span>数据周期</span>
            <label>
              <small>开始日期</small>
              <input
                type="date"
                value={parseDateRange(draft.date_range)[0]}
                onChange={event => changeDraft('date_range', joinDateRange(event.target.value, parseDateRange(draft.date_range)[1]))}
              />
            </label>
            <label>
              <small>结束日期</small>
              <input
                type="date"
                value={parseDateRange(draft.date_range)[1]}
                onChange={event => changeDraft('date_range', joinDateRange(parseDateRange(draft.date_range)[0], event.target.value))}
              />
            </label>
          </div>
          <label><span>交付日期</span><input type="date" value={draft.delivery_due} onChange={event => changeDraft('delivery_due', event.target.value)} /></label>
          </div>
          <div className="form-section">
            <h4>团队与标签信息</h4>
          <label>
            <span>优先级</span>
            <select value={draft.priority} onChange={event => changeDraft('priority', event.target.value as ProjectPayload['priority'])}>
              <option>高</option>
              <option>中</option>
              <option>低</option>
            </select>
          </label>
          <label>
            <span>负责人</span>
            <select value={draft.owner_id} onChange={event => changeDraft('owner_id', event.target.value)}>
              {dashboard.users.map(user => <option key={user.id} value={user.id}>{user.name} / {user.role}</option>)}
            </select>
          </label>
          <div className="schema-check-grid">
            <span>标签体系</span>
            {labelSchemaOptions.map(schemaOption => {
              const selectedSchemas = splitSchemaNames(draft.label_schema);
              const selected = selectedSchemas.includes(schemaOption.name);
              return (
                <label key={schemaOption.name} className={selected ? 'selected' : ''}>
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={() => changeDraft('label_schema', toggleListValue(selectedSchemas, schemaOption.name).join(' + '))}
                  />
                  <strong>{schemaOption.name}</strong>
                  <small>{schemaOption.description}</small>
                </label>
              );
            })}
          </div>
          <div className="project-rule-picker">
            <div className="rule-picker-head">
              <span>规则库</span>
            </div>
            {dashboard.rule_sets.map(ruleSet => {
              const selected = draft.selected_rule_set_ids.includes(ruleSet.id);
              const applied = editingProject ? editingProject.applied_rule_set_ids.includes(ruleSet.id) : false;
              return (
                <label key={ruleSet.id} className={selected ? 'rule-option selected' : 'rule-option'}>
                  <input type="checkbox" checked={selected} onChange={() => toggleDraftRuleSet(ruleSet.id)} />
                  <span>
                    <strong>{ruleSet.name}</strong>
                    <small>{ruleSet.category} / {ruleSet.version} / {applied ? '已应用' : '未应用'}</small>
                  </span>
                </label>
              );
            })}
          </div>
          </div>
          <div className="form-section">
            <h4>导出和文件要求</h4>
          <label>
            <span>报告模板</span>
            <select value={draft.report_template} onChange={event => changeDraft('report_template', event.target.value)}>
              {reportTemplateOptions.map(templateName => <option key={templateName} value={templateName}>{templateName}</option>)}
            </select>
          </label>
          <label><span>导出命名</span><input value={draft.export_pattern} onChange={event => changeDraft('export_pattern', event.target.value)} placeholder="{project}_{date}_{version}_{format}" /></label>
          </div>
          {projectActionError && <div className="form-error">{projectActionError}</div>}
          <div className="project-form-actions">
            <button type="button" className="primary-action" disabled={projectSaving} onClick={submitProject}>
              {projectSaving ? '保存中...' : editingProject ? '保存项目' : '创建项目'}
            </button>
            <button type="button" className="secondary-action" onClick={() => setProjectModalOpen(false)}>取消</button>
          </div>
        </div>
          </div>
        </div>
      )}
    </section>
  );
}

function ImportView({
  dashboard,
  onNavigate,
  onDashboardRefresh
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
  onDashboardRefresh: (projectId?: string) => Promise<DashboardResponse>;
}) {
  const [activeStage, setActiveStage] = React.useState<ImportStage>('upload');
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);
  const [selectedFileName, setSelectedFileName] = React.useState(dashboard.imports[0]?.filename ?? '');
  const [importPreview, setImportPreview] = React.useState<ImportPreviewResponse | null>(null);
  const [importPreviewError, setImportPreviewError] = React.useState<string | null>(null);
  const [importNotice, setImportNotice] = React.useState<string | null>(null);
  const [importPreviewing, setImportPreviewing] = React.useState(false);
  const [busyImportId, setBusyImportId] = React.useState<string | null>(null);
  const [importedJobs, setImportedJobs] = React.useState<ImportedDataJob[]>(() => dashboard.imports.map(toImportedDataJob));
  React.useEffect(() => {
    setImportedJobs(dashboard.imports.map(toImportedDataJob));
    setSelectedFileName(dashboard.imports[0]?.filename ?? '');
  }, [dashboard.active_project.id, dashboard.imports]);
  const activeImport = dashboard.imports[0];
  const legacyPreviewInvalidRows = importPreview
    ? importPreview.quality_issues
      .filter(issue => issue.action === '排除')
      .reduce((total, issue) => total + issue.count, 0)
    : undefined;
  const previewInvalidRows = importPreview?.invalid_content_rows ?? legacyPreviewInvalidRows ?? activeImport?.invalid_rows ?? 0;
  const previewTotalRows = importPreview?.total_rows ?? activeImport?.total_rows ?? 0;
  const previewUsableRows = importPreview?.effective_rows ?? Math.max(previewTotalRows - previewInvalidRows, 0);
  const activeImportStats = importPreview
    ? { total_rows: importPreview.total_rows, valid_rows: previewUsableRows, invalid_rows: previewInvalidRows }
    : activeImport;
  const uploadedFileCount = importedJobs.length;

  const toggleImportedJob = (jobId: string) => {
    setImportedJobs(current => current.map(job => job.id === jobId ? { ...job, included: !job.included } : job));
  };

  const handleImportFile = async (file: File | undefined) => {
    if (!file) return;
    if (!/\.(xlsx|csv)$/i.test(file.name)) {
      setImportPreviewError('当前支持上传 .xlsx 或 .csv 文件');
      return;
    }
    setSelectedFileName(file.name);
    setImportPreviewing(true);
    setImportPreviewError(null);
    setImportNotice(null);
    try {
      const uploaded = await uploadImportFile(dashboard.active_project.id, file);
      const preview = uploaded.preview;
      setImportPreview(preview);
      const invalidRows = preview.invalid_content_rows ?? preview.quality_issues
        .filter(issue => issue.action === '排除')
        .reduce((total, issue) => total + issue.count, 0);
      const duplicateRows = preview.duplicate_comment_ids;
      const importedRows = preview.effective_rows ?? Math.max(preview.total_rows - invalidRows, 0);
      const uploadedJob = toImportedDataJob(uploaded.job);
      setImportedJobs(current => [{
        ...uploadedJob,
        invalid_rows: invalidRows,
        imported_rows: importedRows,
        duplicate_rows: duplicateRows,
        file_size_label: uploadedJob.file_size_label || formatFileSize(file.size),
        note: uploadedJob.note || (duplicateRows > 0
          ? `检测到 ${duplicateRows.toLocaleString()} 条疑似重复数据；预计有效数据仍只按内容列是否可用统计。`
          : `已扫描 ${(preview.sheet_count ?? 1).toLocaleString()} 个 sheet，预计有效数据按内容列非空且非乱码统计。`)
      }, ...current]);
      if (duplicateRows > 0) {
        setImportNotice(`检测到 ${duplicateRows.toLocaleString()} 条疑似重复数据，本次只会导入之前库里没有的数据。`);
      } else {
        setImportNotice(`已导入 ${importedRows.toLocaleString()} 条预计有效数据，并已同步到自动打标与人工标注工作台。`);
      }
      setActiveStage('cleaning');
      await onDashboardRefresh(dashboard.active_project.id);
    } catch (err) {
      setImportPreviewError(err instanceof Error ? err.message : '导入预览失败');
    } finally {
      setImportPreviewing(false);
    }
  };

  const deleteImportedJob = async (jobId: string) => {
    const job = importedJobs.find(item => item.id === jobId);
    if (!job) return;
    if (!window.confirm(`确认删除「${job.filename}」吗？这会同时移除这次导入生成的标注样本。`)) return;
    setBusyImportId(jobId);
    setImportPreviewError(null);
    try {
      await deleteImportFile(dashboard.active_project.id, jobId);
      setImportedJobs(current => current.filter(item => item.id !== jobId));
      setImportNotice(`已删除「${job.filename}」，并同步更新当前项目数据。`);
      await onDashboardRefresh(dashboard.active_project.id);
    } catch (err) {
      setImportPreviewError(err instanceof Error ? err.message : '删除导入文件失败');
    } finally {
      setBusyImportId(null);
    }
  };

  const revalidateImportedJob = async (jobId: string) => {
    setBusyImportId(jobId);
    setImportPreviewError(null);
    setImportNotice(null);
    try {
      const result = await revalidateImportFile(dashboard.active_project.id, jobId);
      setImportPreview(result.preview);
      setImportedJobs(current => current.map(item => item.id === jobId ? toImportedDataJob(result.job) : item));
      setImportNotice(`已重新清洗校验「${result.job.filename}」，有效数据 ${result.job.valid_rows.toLocaleString()} 条已重新同步到标注流程。`);
      await onDashboardRefresh(dashboard.active_project.id);
      setActiveStage('cleaning');
    } catch (err) {
      setImportPreviewError(err instanceof Error ? err.message : '重新清洗校验失败');
    } finally {
      setBusyImportId(null);
    }
  };

  return (
    <section className="workbench-view">
      <ViewHeader
        title="数据导入与清洗报告"
        copy="支持按项目导入 Excel 或 CSV，上传后生成数据整理报告，确认有效数据后进入自动打标签。"
        action="导入数据"
        onAction={() => fileInputRef.current?.click()}
      />
      <div className="import-stage-nav" aria-label="数据导入流程">
        {[
          ['upload', '上传文件', '进入上传列表'],
          ['mapping', '字段映射', '查看字段匹配'],
          ['cleaning', '清洗校验', '查看内容质量'],
          ['preview', '数据预览', '抽样确认结果'],
          ['history', '导入历史', '查看日志记录']
        ].map(([stage, title, copy], index) => (
          <button
            key={stage}
            type="button"
            className={`stage-step ${activeStage === stage ? 'active' : ''}`}
            onClick={() => setActiveStage(stage as ImportStage)}
          >
            <span>{index + 1}</span>
            <strong>{title}</strong>
            <small>{copy}</small>
          </button>
        ))}
      </div>
      {importPreviewError && <div className="import-error">{importPreviewError}</div>}
      {importNotice && <div className="import-notice">{importNotice}</div>}
      <input
        ref={fileInputRef}
        className="hidden-file-input"
        type="file"
        accept=".xlsx,.csv"
        onChange={event => {
          handleImportFile(event.target.files?.[0]);
          event.currentTarget.value = '';
        }}
      />
      {importPreview && (
        <ImportDataReadinessReport
          preview={importPreview}
          uploadedFileName={selectedFileName}
          effectiveRows={previewUsableRows}
          invalidRows={previewInvalidRows}
          onAutoLabel={() => onNavigate('auto')}
        />
      )}
      {activeStage === 'upload' && (
        <ImportUploadWorkspace
          jobs={importedJobs}
          uploadedFileCount={uploadedFileCount}
          batchLimit="100,000"
          previewUsableRows={importPreview ? previewUsableRows : activeImport?.valid_rows ?? 0}
          previewInvalidRows={previewInvalidRows}
          importing={importPreviewing}
          selectedFileName={selectedFileName}
          onPickFile={() => fileInputRef.current?.click()}
          onFile={handleImportFile}
          onToggle={toggleImportedJob}
          onDelete={deleteImportedJob}
          onRevalidate={revalidateImportedJob}
          busyImportId={busyImportId}
        />
      )}
      {activeStage === 'mapping' && <ImportMappingPanel preview={importPreview} />}
      {(activeStage === 'cleaning' || activeStage === 'preview') && (
        <div className="validation-preview-stack">
          <ImportCleaningPanel activeImport={activeImportStats} preview={importPreview} />
          <DataPreviewPanel dashboard={dashboard} preview={importPreview} />
        </div>
      )}
      {activeStage !== 'upload' && (
        <ImportedDataList
          jobs={importedJobs}
          onToggle={toggleImportedJob}
          onDelete={deleteImportedJob}
          onRevalidate={revalidateImportedJob}
          busyImportId={busyImportId}
        />
      )}
      {activeStage === 'history' && <ImportHistoryPanel jobs={importedJobs} onNavigate={onNavigate} />}
      <div className="import-next-strip">
        <span>{importPreview ? `${previewUsableRows.toLocaleString()} 条有效数据将参与下一步自动打标签。` : '上传数据后，系统会生成导入数据报告，并告诉你有多少有效数据进入下一步。'}</span>
        <button type="button" className="primary-action" disabled={!importPreview || previewUsableRows === 0} onClick={() => onNavigate('auto')}>进入自动打标签</button>
      </div>
    </section>
  );
}

function AutoLabelView({
  dashboard,
  onNavigate,
  onRulePreview,
  onRuleApply,
  onDashboardRefresh
}: {
  dashboard: DashboardResponse;
  onNavigate: (view: string) => void;
  onRulePreview: (projectId: string, selectedRuleSetIds: string[]) => Promise<RuleImpactPreview>;
  onRuleApply: (projectId: string, selectedRuleSetIds: string[]) => Promise<RuleImpactPreview>;
  onDashboardRefresh: (projectId?: string) => Promise<DashboardResponse>;
}) {
  const protectedCount = dashboard.records.filter(record => Object.values(record.labels).some(label => label.confirmed)).length;
  const [rulePreviewOpen, setRulePreviewOpen] = React.useState(false);
  const [rulePreview, setRulePreview] = React.useState<RuleImpactPreview | null>(null);
  const [rulePreviewing, setRulePreviewing] = React.useState(false);
  const [ruleApplying, setRuleApplying] = React.useState(false);
  const [ruleActionError, setRuleActionError] = React.useState<string | null>(null);
  const [autoNotice, setAutoNotice] = React.useState<string | null>(null);
  const previewCurrentRules = async () => {
    setRulePreviewOpen(true);
    setRulePreviewing(true);
    setRuleActionError(null);
    try {
      setRulePreview(await onRulePreview(dashboard.active_project.id, dashboard.active_project.selected_rule_set_ids));
    } catch (err) {
      setRuleActionError(err instanceof Error ? err.message : '规则影响预览失败');
    } finally {
      setRulePreviewing(false);
    }
  };
  const applyCurrentRules = async () => {
    setRuleApplying(true);
    setRuleActionError(null);
    try {
      const appliedPreview = await onRuleApply(dashboard.active_project.id, dashboard.active_project.selected_rule_set_ids);
      setRulePreview(appliedPreview);
      const refreshed = await onDashboardRefresh(dashboard.active_project.id);
      setRulePreviewOpen(false);
      setAutoNotice(`自动打标已完成，${refreshed.records.length.toLocaleString()} 条当前项目数据已同步到人工标注工作台。`);
    } catch (err) {
      setRuleActionError(err instanceof Error ? err.message : '应用规则失败');
    } finally {
      setRuleApplying(false);
    }
  };
  return (
    <section className="workbench-view">
      <ViewHeader
        title="自动打标"
        copy="按当前规则版本识别品牌、竞品、情绪、认知和行动标签。人工确认过的标签不会被规则重跑覆盖。"
        action="预览规则影响"
        onAction={previewCurrentRules}
      />
      <div className="auto-console">
        <div className="run-panel">
          <Sparkles size={24} />
          <h3>规则重跑范围</h3>
          <p>本轮会处理未确认标签，保留所有人工确认黄点。运行后可直接进入人工标注页复核冲突项。</p>
          <div className="run-stats">
            <StatBlock title="待处理样本" value={dashboard.records.length.toLocaleString()} detail="当前预览数据" />
            <StatBlock title="人工保护" value={protectedCount.toLocaleString()} detail="不会被自动规则覆盖" />
            <StatBlock title="规则版本" value={dashboard.active_project.rule_version} detail="项目当前版本" />
          </div>
          <div className="auto-run-actions">
            <button type="button" className="secondary-action" onClick={previewCurrentRules}>预览影响</button>
            <button type="button" className="primary-action" onClick={applyCurrentRules} disabled={ruleApplying}>
              {ruleApplying ? '应用中...' : '运行并应用规则'}
            </button>
            <button type="button" className="secondary-action" onClick={() => onNavigate('labeling')}>查看标注结果</button>
          </div>
          {autoNotice && (
            <div className="import-notice workflow-notice">
              <span>{autoNotice}</span>
              <button type="button" className="tiny-action" onClick={() => onNavigate('labeling')}>进入人工标注</button>
              <button type="button" className="tiny-action" onClick={() => onNavigate('report')}>查看统计报告</button>
            </div>
          )}
        </div>
        <div className="auto-samples">
          <h3>最近样本预判</h3>
          {dashboard.records.map(record => (
            <button key={record.id} type="button" onClick={() => onNavigate('labeling')}>
              <strong>{record.content}</strong>
              <span>{optionLabel(dashboard.label_schema, 'sentiment_polarity', record.labels.sentiment_polarity?.final)} / {record.brands.join('、') || '未识别品牌'}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="entity-grid">
        {dashboard.rule_sets.map(ruleSet => (
          <button key={ruleSet.id} type="button" className="entity-card" onClick={() => onNavigate('learning')}>
            <div className="entity-head">
              <Sparkles size={20} />
              <span>{ruleSet.version}</span>
            </div>
            <strong>{ruleSet.name}</strong>
            <p>{ruleSet.layer} / {ruleSet.rule_count} 条规则</p>
            <small>更新于 {ruleSet.last_updated}</small>
          </button>
        ))}
      </div>
      <BrandRuleList dashboard={dashboard} />
      <RuleRunChecklist dashboard={dashboard} />
      {rulePreviewOpen && (
        <RuleImpactModal
          preview={rulePreview}
          loading={rulePreviewing}
          error={ruleActionError}
          applying={ruleApplying}
          onApply={applyCurrentRules}
          onClose={() => setRulePreviewOpen(false)}
        />
      )}
    </section>
  );
}

function RuleImpactModal({
  preview,
  loading,
  error,
  applying,
  onApply,
  onClose
}: {
  preview: RuleImpactPreview | null;
  loading: boolean;
  error: string | null;
  applying: boolean;
  onApply: () => void;
  onClose: () => void;
}) {
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <div className="rule-impact-modal" role="dialog" aria-modal="true" aria-label="规则影响预览" onMouseDown={event => event.stopPropagation()}>
        <div className="modal-head">
          <div>
            <span>自动打标</span>
            <h3>规则影响预览</h3>
          </div>
          <button type="button" className="icon-button" aria-label="关闭" onClick={onClose}>×</button>
        </div>
        {loading && <div className="import-notice">正在计算应用前后的变化...</div>}
        {error && <div className="form-error">{error}</div>}
        {preview && (
          <div className="rule-compare-panel modal-compare">
            <p>新增选择 {preview.newly_selected_rule_set_ids.length} 个规则集，预计影响 {preview.changed_records} 条未人工确认样本；{preview.protected_records} 条人工确认样本不会被覆盖。</p>
            <div className="rule-compare-stats">
              <StatBlock title="应用前" value={formatRuleCounts(preview.before_counts)} detail="当前情绪分布" />
              <StatBlock title="应用后" value={formatRuleCounts(preview.after_counts)} detail="规则重跑后的预计分布" />
              <StatBlock title="人工保护" value={preview.protected_records.toLocaleString()} detail="不会被自动覆盖" />
            </div>
            {preview.sample_changes.length > 0 && (
              <table className="simple-table compact-rule-table">
                <thead><tr><th>样本</th><th>应用前</th><th>应用后</th><th>命中规则</th></tr></thead>
                <tbody>
                  {preview.sample_changes.map(sample => (
                    <tr key={sample.record_id}>
                      <td>{sample.content}</td>
                      <td>{sample.before}</td>
                      <td>{sample.after}</td>
                      <td>{sample.matched_rule}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
        <div className="project-form-actions">
          <button type="button" className="confirm-action" disabled={applying || loading || !preview} onClick={onApply}>
            {applying ? '应用中...' : '确认应用规则'}
          </button>
          <button type="button" className="secondary-action" onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
}

function RuleLearningView({
  dashboard,
  evidenceSamples,
  onRulePreview,
  onRuleApply,
  onEvidenceUpdate,
  onEvidenceDelete
}: {
  dashboard: DashboardResponse;
  evidenceSamples: EvidenceSample[];
  onRulePreview: (projectId: string, selectedRuleSetIds: string[]) => Promise<RuleImpactPreview>;
  onRuleApply: (projectId: string, selectedRuleSetIds: string[]) => Promise<RuleImpactPreview>;
  onEvidenceUpdate: (sampleId: string, patch: Partial<EvidenceSample>) => void;
  onEvidenceDelete: (sampleId: string) => void;
}) {
  const [selectedRuleSetIds, setSelectedRuleSetIds] = React.useState(dashboard.active_project.selected_rule_set_ids);
  const [ruleDefinitions, setRuleDefinitions] = React.useState<RuleDefinition[]>(dashboard.rule_definitions);
  const [ruleActionError, setRuleActionError] = React.useState<string | null>(null);
  const [ruleApplying, setRuleApplying] = React.useState(false);
  const [dirtyRuleIds, setDirtyRuleIds] = React.useState<Set<string>>(new Set());
  const [editingRuleId, setEditingRuleId] = React.useState<string | null>(null);
  void onRulePreview;
  React.useEffect(() => {
    setSelectedRuleSetIds(dashboard.active_project.selected_rule_set_ids);
    setRuleDefinitions(dashboard.rule_definitions);
    setRuleActionError(null);
    setDirtyRuleIds(new Set());
    setEditingRuleId(null);
  }, [dashboard.active_project.id, dashboard.active_project.selected_rule_set_ids, dashboard.rule_definitions]);
  const ruleStatus = new Map(dashboard.project_rule_status.map(status => [status.rule_set_id, status]));
  const visibleDefinitions = ruleDefinitions.filter(definition => selectedRuleSetIds.includes(definition.rule_set_id));
  const categoryOptions = uniqueOptions([...dashboard.rule_sets.map(ruleSet => ruleSet.category), ...ruleDefinitions.map(rule => rule.category), '标签规则', '品牌规则']);
  const layerOptions = uniqueOptions([...dashboard.rule_sets.map(ruleSet => ruleSet.layer), ...ruleDefinitions.map(rule => rule.layer), '情绪一级', '情绪二级', '认知', '行动', '品牌']);
  const brandLabelOptions = uniqueOptions([...dashboard.brand_rules.map(rule => rule.brand), ...ruleDefinitions.map(rule => rule.label)]);
  const toggleRuleSet = (ruleSetId: string) => {
    setSelectedRuleSetIds(current => (
      current.includes(ruleSetId)
        ? current.filter(item => item !== ruleSetId)
        : [...current, ruleSetId]
    ));
  };
  const applyRules = async () => {
    setRuleApplying(true);
    setRuleActionError(null);
    try {
      await onRuleApply(dashboard.active_project.id, selectedRuleSetIds);
    } catch (err) {
      setRuleActionError(err instanceof Error ? err.message : '应用规则失败');
    } finally {
      setRuleApplying(false);
    }
  };
  const addRuleDefinition = () => {
    const targetRuleSetId = selectedRuleSetIds[0] ?? dashboard.rule_sets[0]?.id ?? 'rules-custom';
    const targetRuleSet = dashboard.rule_sets.find(rule => rule.id === targetRuleSetId);
    const newRuleId = `rule-custom-${Date.now()}`;
    setRuleDefinitions(current => [{
      id: newRuleId,
      rule_set_id: targetRuleSetId,
      category: targetRuleSet?.category ?? '标签规则',
      layer: targetRuleSet?.layer ?? '自定义',
      label: '新规则',
      stage: 'global',
      keywords: ['待补充'],
      priority: 1,
      source: '人工新建',
      enabled: true,
      editable: true
    }, ...current]);
    setEditingRuleId(newRuleId);
    setDirtyRuleIds(current => new Set(current).add(newRuleId));
  };
  const updateRuleDefinition = (ruleId: string, patch: Partial<RuleDefinition>) => {
    setRuleDefinitions(current => current.map(rule => rule.id === ruleId ? { ...rule, ...patch } : rule));
    setDirtyRuleIds(current => new Set(current).add(ruleId));
  };
  const saveRuleDefinition = (ruleId: string) => {
    setDirtyRuleIds(current => {
      const next = new Set(current);
      next.delete(ruleId);
      return next;
    });
  };
  const copyRuleDefinition = (rule: RuleDefinition) => {
    const copyId = `rule-copy-${Date.now()}`;
    setRuleDefinitions(current => [{
      ...rule,
      id: copyId,
      label: `${rule.label} 副本`,
      source: '复制规则'
    }, ...current]);
    setEditingRuleId(copyId);
    setDirtyRuleIds(current => new Set(current).add(copyId));
  };
  const deleteRuleDefinition = (ruleId: string) => {
    const target = ruleDefinitions.find(rule => rule.id === ruleId);
    if (!window.confirm(`确认删除「${target?.label ?? '这条规则'}」吗？删除后本页会立刻移除。`)) {
      return;
    }
    setRuleDefinitions(current => current.filter(rule => rule.id !== ruleId));
    setDirtyRuleIds(current => {
      const next = new Set(current);
      next.delete(ruleId);
      return next;
    });
  };
  return (
    <section className="workbench-view">
      <ViewHeader
        title="全局规则中心"
        copy="这里的规则对所有项目共享。项目可以选择使用，也可以不使用；新增或改选规则后，需要预览并应用到当前项目。"
        action="应用所选规则"
        onAction={applyRules}
      />
      {ruleActionError && <div className="form-error">{ruleActionError}</div>}
      <div className="rule-library-grid">
        {dashboard.rule_sets.map(ruleSet => {
          const status = ruleStatus.get(ruleSet.id);
          const selected = selectedRuleSetIds.includes(ruleSet.id);
          return (
            <button
              key={ruleSet.id}
              type="button"
              className={`rule-set-card ${selected ? 'selected' : 'unused'} ${status?.pending_apply ? 'pending' : ''}`}
              onClick={() => toggleRuleSet(ruleSet.id)}
            >
              <b className="rule-set-check">{selected ? '✓' : ''}</b>
              <span>{ruleSet.category}</span>
              <strong>{ruleSet.name}</strong>
              <p>{ruleSet.description}</p>
              <small>{ruleSet.layer} / {ruleSet.rule_count} 条 / {ruleSet.version}</small>
              <em>{status?.applied ? '当前项目已应用' : selected ? '已选择，待应用' : '当前项目未使用'}</em>
            </button>
          );
        })}
      </div>
      {ruleApplying && <div className="import-notice">正在把所选规则应用到当前项目，人工确认过的数据不会被覆盖。</div>}
      <div className="data-table-card">
        <div className="table-card-head">
          <h3>规则明细</h3>
          <span>当前展示已选择规则集的明细，可新增、复制、修改和删除。</span>
          <button type="button" className="primary-action" onClick={addRuleDefinition}><Plus size={14} /> 新建规则</button>
        </div>
        <table className="simple-table">
          <thead>
            <tr><th>分类</th><th>层级</th><th>标签/品牌</th><th>关键词</th><th>优先级</th><th>来源</th><th>状态</th><th>操作</th></tr>
          </thead>
          <tbody>
            {visibleDefinitions.map(rule => (
              <tr key={rule.id} className={editingRuleId === rule.id ? 'editing-rule-row' : ''} onClick={() => setEditingRuleId(rule.id)}>
                <td>
                  <select value={rule.category} onChange={event => updateRuleDefinition(rule.id, { category: event.target.value })}>
                    {categoryOptions.map(category => <option key={category} value={category}>{category}</option>)}
                  </select>
                </td>
                <td>
                  <select value={rule.layer} onChange={event => updateRuleDefinition(rule.id, { layer: event.target.value })}>
                    {layerOptions.map(layer => <option key={layer} value={layer}>{layer}</option>)}
                  </select>
                </td>
                <td>
                  <input
                    className="table-input rule-label-input"
                    list="rule-label-options"
                    value={rule.label}
                    onFocus={() => setEditingRuleId(rule.id)}
                    onChange={event => updateRuleDefinition(rule.id, { label: event.target.value })}
                  />
                  <datalist id="rule-label-options">
                    {brandLabelOptions.map(label => <option key={label} value={label} />)}
                  </datalist>
                  <small>{formatRuleStage(rule.stage)}</small>
                </td>
                <td><textarea className="table-textarea" value={rule.keywords.join('、')} onFocus={() => setEditingRuleId(rule.id)} onChange={event => updateRuleDefinition(rule.id, { keywords: splitTokenList(event.target.value) })} /></td>
                <td><input className="table-input narrow" inputMode="numeric" value={rule.priority} onChange={event => updateRuleDefinition(rule.id, { priority: Number(event.target.value) || 0 })} /></td>
                <td>{rule.source}</td>
                <td><button type="button" className={`toggle-status ${rule.enabled ? 'enabled' : 'disabled'}`} onClick={() => updateRuleDefinition(rule.id, { enabled: !rule.enabled })}>{rule.enabled ? '启用' : '停用'}</button></td>
                <td>
                  <div className="row-icon-actions">
                    {dirtyRuleIds.has(rule.id) && <button type="button" className="confirm-action" onClick={() => saveRuleDefinition(rule.id)}>保存</button>}
                    <button type="button" title="复制" onClick={() => copyRuleDefinition(rule)}><Copy size={14} /></button>
                    <button type="button" title="删除" onClick={() => deleteRuleDefinition(rule.id)}><Trash2 size={14} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="learning-layout">
        <div className="suggestion-board">
          {dashboard.suggestions.map(suggestion => (
            <article key={suggestion.id} className="suggestion-card warning-card">
              <div className="entity-head">
                <Lightbulb size={20} />
                <span>{suggestion.evidence_count} 条证据</span>
              </div>
              <strong>{suggestion.title}</strong>
              <p>{suggestion.summary}</p>
              <div className="keyword-row">
                {suggestion.keywords.map(keyword => <span key={keyword}>{keyword}</span>)}
              </div>
              <div className="suggestion-actions">
                <button type="button">采纳为规则</button>
                <button type="button">查看样本</button>
                <button type="button">暂不处理</button>
              </div>
            </article>
          ))}
        </div>
        <aside className="rule-editor-panel">
          <h3>规则编辑器</h3>
          {dashboard.rule_sets.map(ruleSet => (
            <button key={ruleSet.id} type="button">
              <strong>{ruleSet.name}</strong>
              <span>{ruleSet.layer} / {ruleSet.rule_count} 条 / {ruleSet.version}</span>
            </button>
          ))}
        </aside>
      </div>
      <BrandRuleList dashboard={dashboard} />
      <RuleEvidenceTable samples={evidenceSamples} onUpdate={onEvidenceUpdate} onDelete={onEvidenceDelete} />
    </section>
  );
}

function WordCloudView({ dashboard }: { dashboard: DashboardResponse }) {
  const clientName = dashboard.active_project.client || '默认客户';
  const [settings, setSettings] = React.useState<WordCloudSettings>(() => ({
    ...defaultWordCloudSettings,
    templateName: `${clientName} 词云模板`
  }));
  const [templates, setTemplates] = React.useState<WordCloudTemplate[]>(() => loadWordCloudTemplates(clientName));
  const [selectedTemplateId, setSelectedTemplateId] = React.useState('');
  const [mode, setMode] = React.useState<'gallery' | 'editor'>('gallery');
  const [search, setSearch] = React.useState('');
  const [newWord, setNewWord] = React.useState('');
  const [bulkImportOpen, setBulkImportOpen] = React.useState(false);
  const [bulkText, setBulkText] = React.useState('');
  const [removeCommonOnImport, setRemoveCommonOnImport] = React.useState(true);
  const [removeNumbersOnImport, setRemoveNumbersOnImport] = React.useState(true);
  const [csvImportMode, setCsvImportMode] = React.useState(false);
  const [editorCollapsed, setEditorCollapsed] = React.useState(false);
  const [notice, setNotice] = React.useState<string | null>(null);
  const [termEditor, setTermEditor] = React.useState<WordCloudTermEditor | null>(null);
  const [savedSettingsSnapshot, setSavedSettingsSnapshot] = React.useState('');

  React.useEffect(() => {
    const loaded = loadWordCloudTemplates(clientName);
    setTemplates(loaded);
    setSelectedTemplateId('');
    const nextSettings = normalizeWordCloudSettings(loaded[0]?.settings, loaded[0]?.name ?? defaultWordCloudTemplateName(clientName, dashboard.active_project.name));
    setSettings(nextSettings);
    setSavedSettingsSnapshot(JSON.stringify(nextSettings));
    setMode('gallery');
  }, [clientName, dashboard.active_project.id]);

  const wordCloudDictionary = React.useMemo(() => Array.from(new Set([
    ...dashboard.rule_definitions.filter(rule => rule.enabled).flatMap(rule => [rule.label, ...rule.keywords]),
    ...dashboard.brand_rules.filter(rule => rule.enabled).flatMap(rule => [rule.brand, ...rule.aliases, ...rule.products, ...rule.typo_variants]),
    ...dashboard.records.flatMap(record => record.matched_keywords),
    ...splitWordCloudWords(settings.customWords)
  ].map(word => word.trim()).filter(word => word.length >= 2))).slice(0, 800), [
    dashboard.rule_definitions,
    dashboard.brand_rules,
    dashboard.records,
    settings.customWords
  ]);
  const terms = React.useMemo(() => buildWordCloudTerms(dashboard.records, settings, wordCloudDictionary), [dashboard.records, settings, wordCloudDictionary]);
  const availableTermCount = React.useMemo(
    () => buildWordCloudTerms(dashboard.records, { ...settings, maxWords: 1000 }, wordCloudDictionary).length,
    [dashboard.records, settings, wordCloudDictionary]
  );
  const selectedPalette = wordCloudPaletteOptions.find(option => option.value === settings.palette) ?? wordCloudPaletteOptions[0];
  const sourceCount = sourceTextsForWordCloud(dashboard.records, settings.source).length;
  const templateCountForClient = templates.length;
  const draftSettings = React.useMemo(
    () => normalizeWordCloudSettings(undefined, defaultWordCloudTemplateName(clientName, dashboard.active_project.name)),
    [clientName, dashboard.active_project.name]
  );
  const filteredTemplates = templates.filter(template => {
    const keyword = search.trim().toLowerCase();
    if (!keyword) return true;
    return `${template.name} ${template.brand} ${template.updated_at}`.toLowerCase().includes(keyword);
  });
  const allTermsRepeated = terms.length > 0 && terms.every(term => settings.wordOverrides[term.text]?.repeat ?? true);
  const repeatedTerms = terms.filter(term => term.repeat);
  const visibleSummaryTerms = repeatedTerms.slice(0, Math.max(1, Math.ceil(repeatedTerms.length * 0.6)));
  const maxWordsLimit = Math.max(20, availableTermCount, settings.maxWords);
  const hasUnsavedChanges = mode === 'editor' && JSON.stringify(settings) !== savedSettingsSnapshot;

  const updateSettings = <K extends keyof WordCloudSettings>(key: K, value: WordCloudSettings[K]) => {
    setSettings(current => ({ ...current, [key]: value }));
  };

  const updateWordOverride = (text: string, patch: WordCloudWordOverride) => {
    setSettings(current => ({
      ...current,
      layoutSeed: nextWordCloudSeed(),
      wordOverrides: {
        ...current.wordOverrides,
        [text]: {
          ...(current.wordOverrides[text] ?? {}),
          ...patch
        }
      }
    }));
  };

  const renameWord = (oldText: string, nextText: string) => {
    const cleaned = cleanImportedWord(nextText, false, false);
    if (!cleaned || cleaned === oldText) return;
    setSettings(current => {
      const oldOverride = current.wordOverrides[oldText] ?? {};
      return {
        ...current,
        layoutSeed: nextWordCloudSeed(),
        customWords: mergeWordCloudWords(current.customWords, [cleaned]),
        wordOverrides: {
          ...current.wordOverrides,
          [oldText]: { ...oldOverride, repeat: false },
          [cleaned]: {
            ...oldOverride,
            repeat: oldOverride.repeat ?? true
          }
        }
      };
    });
  };

  const toggleAllRepeat = (checked: boolean) => {
    setSettings(current => ({
      ...current,
      layoutSeed: nextWordCloudSeed(),
      wordOverrides: terms.reduce<Record<string, WordCloudWordOverride>>((acc, term) => {
        acc[term.text] = {
          ...(current.wordOverrides[term.text] ?? {}),
          repeat: checked
        };
        return acc;
      }, { ...current.wordOverrides })
    }));
  };

  const appendCommonStopWords = () => {
    setSettings(current => ({
      ...current,
      layoutSeed: nextWordCloudSeed(),
      stopWords: mergeWordCloudWords(current.stopWords, splitWordCloudWords(extraCommonStopWords))
    }));
    setNotice('已追加常见停用词和拟声词。');
  };

  const focusWordRow = (text: string) => {
    setEditorCollapsed(true);
    window.requestAnimationFrame(() => {
      const row = document.getElementById(wordRowDomId(text));
      row?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      const input = row?.querySelector<HTMLInputElement>('.word-text-input');
      input?.focus();
    });
  };

  const createTemplate = () => {
    setSelectedTemplateId('');
    const nextSettings = { ...draftSettings, layoutSeed: nextWordCloudSeed() };
    setSettings(nextSettings);
    setSavedSettingsSnapshot(JSON.stringify(nextSettings));
    setMode('editor');
    setNotice('已创建新词云，编辑后点击保存。');
  };

  const saveTemplate = (forceNew = false, overrideSettings = settings) => {
    const name = overrideSettings.templateName.trim() || `${clientName} 词云模板`;
    const now = new Date().toLocaleString('zh-CN', { hour12: false });
    const template: WordCloudTemplate = {
      id: forceNew || !selectedTemplateId ? `wc-${Date.now()}` : selectedTemplateId,
      client: clientName,
      brand: dashboard.active_project.brand,
      name,
      updated_at: now,
      settings: { ...overrideSettings, templateName: name }
    };
    const nextTemplates = selectedTemplateId && !forceNew
      ? templates.map(item => item.id === selectedTemplateId ? template : item)
      : [template, ...templates];
    const sortedTemplates = [...nextTemplates].sort((left, right) => wordCloudTemplateTime(right) - wordCloudTemplateTime(left));
    setTemplates(sortedTemplates);
    setSelectedTemplateId(template.id);
    setSavedSettingsSnapshot(JSON.stringify(template.settings));
    saveWordCloudTemplates(clientName, sortedTemplates);
    setNotice(`${forceNew ? '已另存为' : '已保存'}「${name}」，归属客户：${clientName}`);
  };

  const applyTemplate = (template: WordCloudTemplate) => {
    setSelectedTemplateId(template.id);
    const nextSettings = normalizeWordCloudSettings(template.settings, template.name);
    setSettings(nextSettings);
    setSavedSettingsSnapshot(JSON.stringify(nextSettings));
    setMode('editor');
    setNotice(`已应用模板：${template.name}`);
  };

  const saveAsTemplate = () => {
    const nextSettings = { ...settings, templateName: `${settings.templateName} 副本` };
    setSettings(nextSettings);
    saveTemplate(true, nextSettings);
  };

  const deleteTemplate = (templateId: string) => {
    const target = templates.find(template => template.id === templateId);
    if (!window.confirm(`确认删除「${target?.name ?? '这个词云模板'}」吗？`)) return;
    const nextTemplates = templates.filter(template => template.id !== templateId);
    setTemplates(nextTemplates);
    saveWordCloudTemplates(clientName, nextTemplates);
    if (selectedTemplateId === templateId) {
      setSelectedTemplateId('');
      const nextSettings = { ...defaultWordCloudSettings, templateName: defaultWordCloudTemplateName(clientName, dashboard.active_project.name), layoutSeed: nextWordCloudSeed() };
      setSettings(nextSettings);
      setSavedSettingsSnapshot(JSON.stringify(nextSettings));
    }
    setNotice('模板已删除。');
  };

  const addForcedWord = () => {
    const word = cleanImportedWord(newWord, true, true);
    if (!word) return;
    setSettings(current => ({
      ...current,
      layoutSeed: nextWordCloudSeed(),
      customWords: mergeWordCloudWords(current.customWords, [word]),
      wordOverrides: {
        ...current.wordOverrides,
        [word]: {
          size: 42,
          color: paletteColors(current.palette)[0],
          repeat: true
        }
      }
    }));
    setNewWord('');
  };

  const importBulkWords = () => {
    const rawItems = csvImportMode
      ? bulkText.split(/[\n,，;\t]+/)
      : bulkText.split(/\n+/).flatMap(line => splitWordCloudWords(line));
    const cleanedWords = rawItems
      .map(item => cleanImportedWord(item, removeNumbersOnImport, removeCommonOnImport))
      .filter((item): item is string => Boolean(item));
    const uniqueWords = Array.from(new Set(cleanedWords));
    if (uniqueWords.length === 0) {
      setNotice('没有识别到可导入的有效词语。');
      return;
    }
    setSettings(current => ({
      ...current,
      layoutSeed: nextWordCloudSeed(),
      customWords: mergeWordCloudWords(current.customWords, uniqueWords),
      wordOverrides: uniqueWords.reduce<Record<string, WordCloudWordOverride>>((acc, word, index) => {
        const colors = paletteColors(current.palette);
        acc[word] = {
          ...(current.wordOverrides[word] ?? {}),
          size: current.wordOverrides[word]?.size ?? clamp(current.maxFontSize - index * 2, current.minFontSize, current.maxFontSize),
          color: current.wordOverrides[word]?.color ?? colors[index % colors.length],
          repeat: current.wordOverrides[word]?.repeat ?? true
        };
        return acc;
      }, { ...current.wordOverrides })
    }));
    setBulkImportOpen(false);
    setBulkText('');
    setNotice(`已导入 ${uniqueWords.length} 个有效词语，已自动去除无效内容。`);
  };

  const reshuffleWordCloud = () => {
    setTermEditor(null);
    updateSettings('layoutSeed', nextWordCloudSeed());
  };

  const exportWords = () => {
    const escapeHtml = (value: string | number) => String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
    const sortedTerms = [...terms].sort((left, right) => right.frequency - left.frequency || right.engagement - left.engagement);
    const rows = [
      ['词语', '词频', '互动', '字号', '颜色', '权重'].map(cell => `<th>${escapeHtml(cell)}</th>`).join(''),
      ...sortedTerms.map(term => [term.text, term.frequency, term.engagement, term.weight, term.color, Math.round(term.value * 100) / 100]
        .map(cell => `<td>${escapeHtml(cell)}</td>`)
        .join(''))
    ].map(row => `<tr>${row}</tr>`).join('');
    const html = `\ufeff<html><head><meta charset="utf-8" /></head><body><table>${rows}</table></body></html>`;
    const blob = new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${dashboard.active_project.client}_${dashboard.active_project.name}_词云词频.xls`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const downloadPng = () => {
    const canvas = document.createElement('canvas');
    const width = 1920;
    const height = 1080;
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.fillStyle = '#fffef8';
    ctx.fillRect(0, 0, width, height);
    terms.filter(term => term.repeat).forEach(term => {
      ctx.save();
      ctx.translate((term.x / 100) * width, (term.y / 100) * height);
      ctx.fillStyle = term.color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = `900 ${Math.round(term.weight * 1.85)}px ${wordCloudFontFamily(settings.fontFamily)}`;
      ctx.fillText(term.text, 0, 0);
      ctx.restore();
    });
    const link = document.createElement('a');
    link.download = `${settings.templateName || dashboard.active_project.name}_1920x1080.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  };

  const collapseEditor = () => setEditorCollapsed(true);

  const openTermEditor = (term: WordCloudTerm, event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect();
    setTermEditor({
      sourceText: term.text,
      text: term.text,
      frequency: settings.wordOverrides[term.text]?.frequency ?? term.frequency,
      size: settings.wordOverrides[term.text]?.size ?? term.weight,
      color: settings.wordOverrides[term.text]?.color ?? term.color,
      repeat: settings.wordOverrides[term.text]?.repeat ?? true,
      left: clamp(rect.left + rect.width / 2, 160, window.innerWidth - 260),
      top: clamp(rect.top + rect.height + 10, 90, window.innerHeight - 150)
    });
  };

  const applyTermEditor = () => {
    if (!termEditor) return;
    const cleaned = cleanImportedWord(termEditor.text, false, false);
    if (!cleaned) {
      setNotice('词语不能为空，也不能是纯符号。');
      return;
    }
    const nextFrequency = Math.max(0, Math.round(termEditor.frequency));
    const nextSize = clamp(Math.round(termEditor.size), 8, 128);
    setSettings(current => {
      const sourceOverride = current.wordOverrides[termEditor.sourceText] ?? {};
      if (cleaned === termEditor.sourceText) {
        return {
          ...current,
          layoutSeed: nextWordCloudSeed(),
          wordOverrides: {
            ...current.wordOverrides,
            [cleaned]: {
              ...sourceOverride,
              frequency: nextFrequency,
              size: nextSize,
              color: termEditor.color,
              repeat: termEditor.repeat
            }
          }
        };
      }
      return {
        ...current,
        layoutSeed: nextWordCloudSeed(),
        customWords: mergeWordCloudWords(current.customWords, [cleaned]),
        wordOverrides: {
          ...current.wordOverrides,
          [termEditor.sourceText]: {
            ...sourceOverride,
            repeat: false
          },
          [cleaned]: {
            ...sourceOverride,
            frequency: nextFrequency,
            size: nextSize,
            color: termEditor.color,
            repeat: termEditor.repeat
          }
        }
      };
    });
    setTermEditor(null);
  };

  const renderCanvas = (previewTerms: WordCloudTerm[], previewSettings: WordCloudSettings, compact = false) => (
    <div className={`wordcloud-canvas shape-${previewSettings.shape} ${compact ? 'is-compact' : ''}`}>
      {previewTerms.filter(term => term.repeat).length > 0 ? previewTerms.filter(term => term.repeat).map(term => (
        compact ? (
          <span
            key={term.text}
            style={{
              left: `${term.x}%`,
              top: `${term.y}%`,
              color: term.color,
              fontSize: `${Math.max(9, term.weight * 0.42)}px`,
              transform: `translate(-50%, -50%) rotate(${term.rotate}deg)`,
              fontFamily: wordCloudFontFamily(previewSettings.fontFamily)
            }}
          >
            {term.text}
          </span>
        ) : (
          <button
            key={term.text}
            type="button"
            onClick={event => openTermEditor(term, event)}
            style={{
              left: `${term.x}%`,
              top: `${term.y}%`,
              color: term.color,
              fontSize: `${term.weight}px`,
              transform: `translate(-50%, -50%) rotate(${term.rotate}deg)`,
              fontFamily: wordCloudFontFamily(previewSettings.fontFamily)
            }}
          >
            {term.text}
          </button>
        )
      )) : (
        <div className="wordcloud-empty">
          <Cloud size={compact ? 22 : 42} />
          <strong>暂无可生成词云的数据</strong>
          {!compact && <p>请切换数据来源，或降低最小词频。</p>}
        </div>
      )}
    </div>
  );

  if (mode === 'gallery') {
    return (
      <section className="workbench-view wordcloud-workbench">
        <ViewHeader
          title="词云作品库"
          copy="按客户保存词云作品，点击卡片即可进入编辑；作品模板跨项目复用。"
          action="新建词云"
          onAction={createTemplate}
        />
        {notice && <div className="import-notice">{notice}</div>}
        <div className="wordcloud-dashboard">
          <aside className="wordcloud-filter-panel">
            <h3>筛选</h3>
            <button type="button" className="active"><Cloud size={15} /> 全部 <b>{templateCountForClient}</b></button>
            <button type="button"><Save size={15} /> 当前客户 <b>{templateCountForClient}</b></button>
            <button type="button"><Trash2 size={15} /> 回收站 <b>0</b></button>
            <div className="wordcloud-folder-block">
              <span>客户</span>
              <strong>{clientName}</strong>
              <p>{dashboard.active_project.brand} / {dashboard.active_project.name}</p>
            </div>
          </aside>
          <div className="wordcloud-gallery-panel">
            <div className="wordcloud-gallery-toolbar">
              <div className="search-box wordcloud-search">
                <Search size={16} />
                <input value={search} onChange={event => setSearch(event.target.value)} placeholder="搜索词云名称、品牌或日期" />
              </div>
            </div>
            <div className="wordcloud-gallery-grid">
              {filteredTemplates.map(template => {
                const templateSettings = normalizeWordCloudSettings(template.settings, template.name);
                const previewTerms = buildWordCloudTerms(dashboard.records, templateSettings, wordCloudDictionary).slice(0, 42);
                return (
                  <button key={template.id} type="button" className="wordcloud-card" onClick={() => applyTemplate(template)}>
                    {renderCanvas(previewTerms, templateSettings, true)}
                    <div className="wordcloud-card-meta">
                      <strong>{template.name}</strong>
                      <span>{template.updated_at}</span>
                      <i onClick={event => { event.stopPropagation(); deleteTemplate(template.id); }}><Trash2 size={14} /></i>
                    </div>
                  </button>
                );
              })}
              {templates.length > 0 && filteredTemplates.length === 0 && (
                <div className="wordcloud-empty-gallery">
                  <Cloud size={44} />
                  <strong>没有匹配的词云</strong>
                  <p>换一个关键词搜索，或点击右上角新建。</p>
                </div>
              )}
              {templates.length === 0 && (
                <div className="wordcloud-empty-gallery">
                  <Cloud size={44} />
                  <strong>还没有保存词云作品</strong>
                  <p>点击右上角新建词云，编辑后保存到当前客户。</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="workbench-view wordcloud-workbench">
      <div className="wordcloud-editor-topbar">
        <button type="button" onClick={() => setMode('gallery')}>返回作品库</button>
        <input value={settings.templateName} onChange={event => updateSettings('templateName', event.target.value)} aria-label="词云名称" />
        <button type="button" className={`confirm-action ${hasUnsavedChanges ? 'save-attention' : ''}`} onClick={() => saveTemplate()}><Save size={15} /> 保存</button>
        <button type="button" onClick={saveAsTemplate}><Copy size={15} /> 另存为</button>
        <button type="button" onClick={downloadPng}><Download size={15} /> 下载 PNG</button>
        <button type="button" onClick={exportWords}><Download size={15} /> 导出词频</button>
      </div>
      {notice && <div className="import-notice">{notice}</div>}
      <div className={`wordcloud-layout ${editorCollapsed ? 'settings-collapsed' : ''}`}>
        <aside className="wordcloud-panel" onFocusCapture={collapseEditor} onClick={collapseEditor}>
          <div className="panel-title-row">
            <div>
              <span>WORDS</span>
              <h3>词语编辑</h3>
            </div>
            <div className="wordcloud-word-actions">
              <button type="button" className="tiny-action" onClick={() => setBulkImportOpen(true)}><UploadCloud size={13} /> 批量导入</button>
            </div>
          </div>
          <div className="wordcloud-add-row">
            <input value={newWord} onChange={event => setNewWord(event.target.value)} placeholder="输入新词" />
            <button type="button" onClick={addForcedWord}>加入</button>
          </div>
          <div className={`wordcloud-word-table ${settings.weightByEngagement ? 'show-engagement' : ''}`}>
            <div className="wordcloud-word-head">
              <label><input type="checkbox" checked={allTermsRepeated} onChange={event => toggleAllRepeat(event.target.checked)} /> 选</label>
              <span>文本</span>
              <span>词频</span>
              {settings.weightByEngagement && <span>互动</span>}
              <span>字号</span>
              <span>颜色</span>
            </div>
            {terms.map(term => (
              <div key={term.text} id={wordRowDomId(term.text)} className="wordcloud-word-row">
                <input
                  type="checkbox"
                  checked={settings.wordOverrides[term.text]?.repeat ?? true}
                  onChange={event => updateWordOverride(term.text, { repeat: event.target.checked })}
                />
                <input
                  className="word-text-input"
                  defaultValue={term.text}
                  title="点击修改词语"
                  onBlur={event => renameWord(term.text, event.target.value)}
                  onKeyDown={event => {
                    if (event.key === 'Enter') event.currentTarget.blur();
                  }}
                />
                <input
                  type="number"
                  min={0}
                  value={settings.wordOverrides[term.text]?.frequency ?? term.frequency}
                  onChange={event => {
                    const nextFrequency = Number(event.target.value);
                    updateWordOverride(term.text, { frequency: Number.isFinite(nextFrequency) ? Math.max(0, Math.round(nextFrequency)) : term.frequency });
                  }}
                />
                {settings.weightByEngagement && <span className="word-engagement-count">{term.engagement.toLocaleString()}</span>}
                <input
                  type="number"
                  min={8}
                  max={120}
                  value={settings.wordOverrides[term.text]?.size ?? term.weight}
                  onChange={event => {
                    const nextSize = Number(event.target.value);
                    updateWordOverride(term.text, { size: Number.isFinite(nextSize) ? Math.max(8, Math.min(120, nextSize)) : term.weight });
                  }}
                />
                <input
                  type="color"
                  value={settings.wordOverrides[term.text]?.color ?? term.color}
                  onChange={event => updateWordOverride(term.text, { color: event.target.value })}
                />
              </div>
            ))}
          </div>
          <div className="wordcloud-stats">
            <StatBlock title="分析文本" value={sourceCount.toLocaleString()} detail="当前来源文本数" />
            <StatBlock title="词语数量" value={terms.length.toLocaleString()} detail="进入词云预览" />
          </div>
          <label className="editor-field">
            <span>
              停用词
              <button type="button" className="inline-text-action" onClick={appendCommonStopWords}>追加常见停用词</button>
            </span>
            <textarea value={settings.stopWords} onChange={event => updateSettings('stopWords', event.target.value)} />
          </label>
          <label className="editor-field">
            <span>强制加入词</span>
            <textarea placeholder="例如：a2、奶源、配方" value={settings.customWords} onChange={event => updateSettings('customWords', event.target.value)} />
          </label>
        </aside>

        <div className="wordcloud-preview-card" onFocusCapture={collapseEditor} onClick={() => { collapseEditor(); setTermEditor(null); }}>
          <div className="wordcloud-toolbar">
            <div>
              <span className="status-pill">{dashboard.active_project.name}</span>
              <h2>{settings.templateName}</h2>
            </div>
            <div className="report-export-actions">
              <button type="button" className="confirm-action" onClick={reshuffleWordCloud}><RefreshCw size={14} /> 重排词云</button>
              <button type="button" onClick={downloadPng}><Download size={14} /> 高清 PNG</button>
            </div>
          </div>
          {renderCanvas(terms, settings)}
          {termEditor && (
            <div
              className="word-term-popover"
              style={{ left: termEditor.left, top: termEditor.top }}
              onClick={event => event.stopPropagation()}
            >
              <input
                value={termEditor.text}
                onChange={event => setTermEditor(current => current ? { ...current, text: event.target.value } : current)}
                onKeyDown={event => {
                  if (event.key === 'Enter') applyTermEditor();
                  if (event.key === 'Escape') setTermEditor(null);
                }}
                autoFocus
              />
              <div>
                <label className="popover-check">选<input type="checkbox" checked={termEditor.repeat} onChange={event => setTermEditor(current => current ? { ...current, repeat: event.target.checked } : current)} /></label>
                <label>词频<input type="number" min={0} value={termEditor.frequency} onChange={event => setTermEditor(current => current ? { ...current, frequency: Number(event.target.value) || 0 } : current)} /></label>
                <label>字号<input type="number" min={8} max={128} value={termEditor.size} onChange={event => setTermEditor(current => current ? { ...current, size: Number(event.target.value) || 8 } : current)} /></label>
                <input type="color" value={termEditor.color} onChange={event => setTermEditor(current => current ? { ...current, color: event.target.value } : current)} aria-label="词语颜色" />
                <button type="button" onClick={applyTermEditor}>确认</button>
              </div>
            </div>
          )}
          <div className="wordcloud-word-list">
            {visibleSummaryTerms.map(term => (
              <button key={term.text} type="button" onClick={() => focusWordRow(term.text)}>
                {term.text}<b>{term.frequency}</b>
              </button>
            ))}
          </div>
        </div>

        <aside className={`wordcloud-panel wordcloud-settings-panel ${editorCollapsed ? 'is-collapsed' : ''}`}>
          {editorCollapsed ? (
            <>
              <button
                type="button"
                className="settings-collapse-button collapsed-toggle"
                onClick={() => setEditorCollapsed(false)}
                aria-label="展开设置"
              >
                <SlidersHorizontal size={20} />
              </button>
              <button type="button" className="collapsed-settings-summary" onClick={() => setEditorCollapsed(false)}>
                <strong>{wordCloudSourceOptions.find(option => option.value === settings.source)?.label ?? '数据来源'}</strong>
                <span>{wordCloudShapeOptions.find(option => option.value === settings.shape)?.label ?? '词云形状'}</span>
                <span>{selectedPalette.label}</span>
                <span>{wordCloudFontOptions.find(option => option.value === settings.fontFamily)?.label ?? '字体'}</span>
                <small>{Math.min(settings.minFontSize, settings.maxFontSize)} - {Math.max(settings.minFontSize, settings.maxFontSize)}px</small>
                <small>宽松度 {settings.spacing}%</small>
              </button>
            </>
          ) : (
            <>
          <div className="panel-title-row">
            <div>
              <span>编辑器</span>
              <h3>样式与规则</h3>
            </div>
            <button
              type="button"
              className="settings-collapse-button"
              onClick={() => setEditorCollapsed(true)}
              aria-label="收起设置"
            >
              <SlidersHorizontal size={20} />
            </button>
          </div>
          <label className="editor-field">
            <span><Cloud size={14} /> 数据来源</span>
            <select value={settings.source} onChange={event => updateSettings('source', event.target.value as WordCloudSource)}>
              {wordCloudSourceOptions.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
          <label className="editor-field">
            <span><Cloud size={14} /> 词云形状</span>
            <div className="shape-picker">
              {wordCloudShapeOptions.map(option => (
                <button
                  key={option.value}
                  type="button"
                  className={settings.shape === option.value ? 'active' : ''}
                  onClick={() => updateSettings('shape', option.value)}
                >
                  <i className={`shape-preview shape-${option.value}`} />
                  <b>{option.label}</b>
                </button>
              ))}
            </div>
          </label>
          <label className="editor-field">
            <span><Palette size={14} /> 配色方案</span>
            <details className="palette-dropdown">
              <summary>
                <b>{selectedPalette.label}</b>
                <em>
                  {selectedPalette.colors.map(color => <i key={color} style={{ background: color }} />)}
                </em>
              </summary>
              <div className="palette-option-list">
                {wordCloudPaletteOptions.map(option => (
                  <button
                    key={option.value}
                    type="button"
                    className={settings.palette === option.value ? 'active' : ''}
                    onClick={() => updateSettings('palette', option.value)}
                  >
                    <span>{option.label}</span>
                    <em>{option.colors.map(color => <i key={color} style={{ background: color }} />)}</em>
                  </button>
                ))}
              </div>
            </details>
          </label>
          <label className="editor-field">
            <span><Type size={14} /> 字体</span>
            <div className="font-picker">
              {wordCloudFontOptions.map(option => (
                <button
                  key={option.value}
                  type="button"
                  className={settings.fontFamily === option.value ? 'active' : ''}
                  style={{ fontFamily: option.family }}
                  onClick={() => updateSettings('fontFamily', option.value)}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </label>
          <label className="editor-field">
            <span>布局密度</span>
            <select value={settings.layout} onChange={event => updateSettings('layout', event.target.value as WordCloudLayoutMode)}>
              <option value="balanced">平衡</option>
              <option value="dense">紧凑</option>
              <option value="airy">留白</option>
            </select>
          </label>
          <div className="range-grid">
            <label>
              <span>字号范围 {Math.min(settings.minFontSize, settings.maxFontSize)} - {Math.max(settings.minFontSize, settings.maxFontSize)}px</span>
              <div className="font-size-range">
                <input type="range" min={8} max={80} value={settings.minFontSize} onChange={event => updateSettings('minFontSize', Number(event.target.value))} />
                <input type="range" min={24} max={128} value={settings.maxFontSize} onChange={event => updateSettings('maxFontSize', Number(event.target.value))} />
              </div>
            </label>
            <label>
              <span>宽松密度 {settings.spacing}%</span>
              <input type="range" min={0} max={200} value={settings.spacing} onChange={event => updateSettings('spacing', Number(event.target.value))} />
            </label>
            <label>
              <span>最大词数 {settings.maxWords} / {maxWordsLimit}</span>
              <input type="range" min={1} max={maxWordsLimit} value={Math.min(settings.maxWords, maxWordsLimit)} onChange={event => updateSettings('maxWords', Number(event.target.value))} />
            </label>
            <label>
              <span>最小词频 {settings.minFrequency}</span>
              <input type="range" min={1} max={10} value={settings.minFrequency} onChange={event => updateSettings('minFrequency', Number(event.target.value))} />
            </label>
          </div>
          <label className="switch-row">
            <span>根据互动数加权</span>
            <input type="checkbox" checked={settings.weightByEngagement} onChange={event => updateSettings('weightByEngagement', event.target.checked)} />
          </label>
          <button type="button" className="confirm-action full-width" onClick={() => saveTemplate()}><Save size={15} /> 保存到客户模板</button>
            </>
          )}
        </aside>
      </div>
      {bulkImportOpen && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="word-import-modal">
            <div className="word-import-head">
              <h3>Import words from</h3>
              <div>
                <button type="button" className="active">Text</button>
                <button type="button" disabled>Web</button>
              </div>
            </div>
            <div className="word-import-tip">
              可以直接粘贴文本、Excel 列或 CSV。系统会自动去除 @某人、链接、纯数字、纯表情和空内容。
            </div>
            <textarea
              value={bulkText}
              onChange={event => setBulkText(event.target.value)}
              placeholder="Input your text here"
            />
            <div className="word-import-options">
              <label><input type="checkbox" checked={removeCommonOnImport} onChange={event => setRemoveCommonOnImport(event.target.checked)} /> Remove common words</label>
              <label><input type="checkbox" checked={removeNumbersOnImport} onChange={event => setRemoveNumbersOnImport(event.target.checked)} /> Remove numbers</label>
              <label><input type="checkbox" checked readOnly /> Remove @ mentions / emoji</label>
              <label><input type="checkbox" checked={csvImportMode} onChange={event => setCsvImportMode(event.target.checked)} /> CSV format</label>
            </div>
            <div className="word-import-actions">
              <button type="button" className="confirm-action" onClick={importBulkWords}>Import words</button>
              <button type="button" onClick={() => setBulkImportOpen(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

function ReportView({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <section className="workbench-view">
      <ViewHeader
        title="在线报告"
        copy="报告由可编辑块组成，分析师在线确认内容、图表、重点样本和结论后，再导出 Word、PDF 或 PPT。"
        action="复制模板"
      />
      <div className="report-layout">
        <div className="report-canvas">
          <div className="report-title-row">
            <div>
              <span className="status-pill">{dashboard.report.version}</span>
              <h2>{dashboard.report.title}</h2>
            </div>
            <div className="report-export-actions">
              <button type="button">导出 Word</button>
              <button type="button">导出 PDF</button>
              <button type="button">导出 PPT</button>
            </div>
          </div>
          {dashboard.report.blocks.map(block => (
            <article key={block.id} className="report-block">
              <span>{block.block_type}</span>
              <strong>{block.title}</strong>
              <p>{block.content}</p>
              <textarea defaultValue={block.content} />
            </article>
          ))}
          <button type="button" className="add-report-block">添加报告块</button>
        </div>
        <aside className="report-side">
          <h3>模板与导出</h3>
          {dashboard.report_templates.map(template => (
            <button key={template.id} type="button">
              <strong>{template.name}</strong>
              <p>{template.version} / {template.sections.length} 个章节</p>
            </button>
          ))}
          {dashboard.export_presets.map(preset => (
            <button key={preset.id} type="button">
              <strong>{preset.name}</strong>
              <code>{preset.pattern}</code>
            </button>
          ))}
        </aside>
      </div>
      <ReportOpsPanel dashboard={dashboard} />
    </section>
  );
}

function UsersView({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <section className="workbench-view">
      <ViewHeader
        title="用户权限"
        copy="用户、角色和权限需要支持增删改查。人工确认记录会保留确认人和确认时间，后续规则重跑不覆盖。"
        action="邀请用户"
      />
      <div className="permission-layout">
        <div className="role-panel">
          {['项目管理员', '分析师', '标注员', '客户查看'].map((role, index) => (
            <button key={role} type="button" className={index === 0 ? 'active' : ''}>
              <strong>{role}</strong>
              <span>{index === 0 ? '全量权限' : index === 1 ? '规则与报告' : index === 2 ? '人工标注' : '只读报告'}</span>
            </button>
          ))}
        </div>
        <div className="permission-matrix">
          <h3>权限矩阵</h3>
          {['项目配置', '数据导入', '规则学习', '自动打标', '人工确认', '报告导出', '用户管理'].map((permission, index) => (
            <label key={permission}>
              <span>{permission}</span>
              <input type="checkbox" defaultChecked={index < 6} />
            </label>
          ))}
        </div>
      </div>
      <div className="entity-grid user-grid">
        {dashboard.users.map(user => (
          <button key={user.id} type="button" className="entity-card">
            <div className="large-avatar">{user.avatar}</div>
            <strong>{user.name}</strong>
            <p>{user.role}</p>
            <span className="status-pill">{user.status}</span>
          </button>
        ))}
      </div>
      <AuditTrail dashboard={dashboard} />
    </section>
  );
}

function ImportUploadDetails({
  selectedFileName,
  onNext
}: {
  selectedFileName: string;
  onNext: () => void;
}) {
  return (
    <div className="import-detail-grid">
      <div className="import-card">
        <h3>上传设置</h3>
        <label><span>目标项目</span><select defaultValue="A2 舆情分析项目"><option>A2 舆情分析项目</option><option>母婴品牌风险监测</option></select></label>
        <label><span>数据来源</span><select defaultValue="混合平台"><option>混合平台</option><option>小红书</option><option>抖音</option><option>微博</option></select></label>
        <label><span>导入模式</span><select defaultValue="replace"><option value="append">追加到当前项目</option><option value="replace">替换未确认数据</option><option value="snapshot">创建新数据版本</option></select></label>
      </div>
      <div className="import-card">
        <h3>文件校验</h3>
        <div className="file-check-list">
          {[
            ['文件类型', selectedFileName ? '已选择' : '等待选择'],
            ['行数上限', '100,000 行以内'],
            ['表头识别', '自动匹配常见字段'],
            ['历史版本', '保留导入记录和导出记录']
          ].map(([label, value]) => (
            <div key={label}><span>{label}</span><strong>{value}</strong></div>
          ))}
        </div>
        <button type="button" className="primary-action" onClick={onNext}>确认并进入字段映射</button>
      </div>
    </div>
  );
}

function ImportMappingPanel({ preview }: { preview: ImportPreviewResponse | null }) {
  const mappings = preview?.mappings ?? importFieldMappings();
  return (
    <div className="data-table-card">
      <div className="table-card-head">
        <h3>字段映射工作台</h3>
        <span>{preview ? `${preview.filename} / ${preview.sheet_name}` : '必填字段需要确认，非必填字段会保留为空值继续导入'}</span>
      </div>
      <table className="simple-table mapping-table">
        <thead>
          <tr><th>Excel 字段</th><th>系统字段</th><th>是否必填</th><th>识别置信度</th><th>样例</th><th>操作</th></tr>
        </thead>
        <tbody>
          {mappings.map(mapping => (
            <tr key={mapping.source}>
              <td>{mapping.source}</td>
              <td><select defaultValue={mapping.target}><option>{mapping.target}</option><option>忽略该字段</option></select></td>
              <td>{mapping.required ? <span className="status-pill">必填</span> : '可为空'}</td>
              <td><div className="confidence-bar"><span style={{ width: `${mapping.confidence}%` }} /></div><small>{mapping.confidence}%</small></td>
              <td>{mapping.sample}</td>
              <td><button type="button" className="tiny-action">确认</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ImportCleaningPanel({
  activeImport,
  preview
}: {
  activeImport?: Pick<DashboardResponse['imports'][number], 'total_rows' | 'valid_rows' | 'invalid_rows'>;
  preview: ImportPreviewResponse | null;
}) {
  const issueRows = preview?.quality_issues ?? [
    { rule: '空内容', count: 428, description: '正文为空或只包含空格', action: '排除', enabled: true },
    { rule: '纯符号表情', count: 312, description: '仅包含标点、emoji 或无语义符号', action: '排除', enabled: true },
    { rule: '纯@他人', count: 184, description: '评论只是在 @ 账号，无实际观点', action: '排除', enabled: true },
    { rule: '乱码内容', count: 96, description: '异常编码、重复不可读字符', action: '排除', enabled: true },
    { rule: '重复评论', count: 1880, description: '评论ID或内容组合重复', action: '合并', enabled: true },
    { rule: '缺失平台', count: 23, description: '平台为空但内容有效', action: '保留并待补', enabled: false }
  ];
  return (
    <div className="cleaning-workbench">
      <div className="ops-grid">
        <StatBlock title="总行数" value={activeImport ? activeImport.total_rows.toLocaleString() : '0'} detail="Excel 原始行数" />
        <StatBlock title="有效行" value={activeImport ? activeImport.valid_rows.toLocaleString() : '0'} detail="将进入规则学习与自动打标" />
        <StatBlock title="无效行" value={activeImport ? activeImport.invalid_rows.toLocaleString() : '0'} detail="可导出问题清单" />
        <StatBlock title="处理策略" value="规则可编辑" detail="保留非必填字段空值" />
      </div>
      <div className="data-table-card">
        <div className="table-card-head">
          <h3>无效数据原因</h3>
          <span>这里会决定哪些数据被排除、合并或保留待补</span>
        </div>
        <table className="simple-table">
          <thead>
            <tr><th>规则</th><th>命中数量</th><th>说明</th><th>处理方式</th><th>启用</th></tr>
          </thead>
          <tbody>
            {issueRows.map(issue => (
              <tr key={issue.rule}>
                <td>{issue.rule}</td>
                <td>{issue.count.toLocaleString()}</td>
                <td>{issue.description}</td>
                <td>
                  <select defaultValue={issue.action}>
                    <option>排除</option>
                    <option>提示</option>
                    <option>待确认</option>
                    <option>合并</option>
                    <option>保留并待补</option>
                    <option>自动补平台</option>
                  </select>
                </td>
                <td><input type="checkbox" defaultChecked={issue.enabled} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ImportDataReadinessReport({
  preview,
  uploadedFileName,
  effectiveRows,
  invalidRows,
  onAutoLabel
}: {
  preview: ImportPreviewResponse;
  uploadedFileName: string;
  effectiveRows: number;
  invalidRows: number;
  onAutoLabel: () => void;
}) {
  const duplicateIssue = preview.quality_issues.find(issue => issue.rule.includes('重复'));
  const missingPlatformIssue = preview.quality_issues.find(issue => issue.rule.includes('缺失平台'));
  const missingSourceIssue = preview.quality_issues.find(issue => issue.rule.includes('缺失内容ID'));
  const issueRows = preview.quality_issues.filter(issue => issue.count > 0);

  return (
    <div className="import-readiness-report">
      <div className="readiness-head">
        <div>
          <span>导入数据报告</span>
          <h3>{uploadedFileName || preview.filename}</h3>
          <p>报告只展示数据整理结果，不做主观评分。有效数据会进入下一步自动打标签，问题数据按下方策略处理。</p>
        </div>
        <button type="button" className="confirm-action" disabled={effectiveRows === 0} onClick={onAutoLabel}>
          确认 {effectiveRows.toLocaleString()} 条有效数据，进入自动打标签
        </button>
      </div>
      <div className="readiness-stats">
        <StatBlock title="上传总数据" value={preview.total_rows.toLocaleString()} detail={`${(preview.sheet_count ?? 1).toLocaleString()} 个 sheet / ${preview.inferred_platform}`} />
        <StatBlock title="参与分析有效数据" value={effectiveRows.toLocaleString()} detail="内容列非空、非空格、非乱码" />
        <StatBlock title="不进入分析数据" value={invalidRows.toLocaleString()} detail="空内容或乱码内容" />
        <StatBlock title="重复提示" value={(duplicateIssue?.count ?? 0).toLocaleString()} detail="提示用户，不扣有效数据" />
      </div>
      <div className="readiness-body">
        <div className="readiness-section">
          <h4>数据整理与清洗策略</h4>
          <div className="cleanup-policy-list">
            <div><strong>空内容 / 乱码</strong><span>默认排除，不进入标签分析。</span></div>
            <div><strong>重复评论 ID</strong><span>作为风险提示保留，暂不扣减预计有效数据。</span></div>
            <div><strong>缺失平台</strong><span>{(missingPlatformIssue?.count ?? 0) > 0 ? '按当前项目默认平台补全。' : '平台字段可识别，无需补全。'}</span></div>
            <div><strong>缺失内容 ID</strong><span>{(missingSourceIssue?.count ?? 0) > 0 ? '保留数据，但标记为不可完整回溯内容链接。' : '内容 ID 字段完整度正常。'}</span></div>
          </div>
        </div>
        <div className="readiness-section">
          <h4>需要关注的情况</h4>
          {issueRows.length > 0 ? (
            <div className="issue-chip-list">
              {issueRows.map(issue => (
                <span key={issue.rule}>{issue.rule} {issue.count.toLocaleString()} · {issue.action}</span>
              ))}
            </div>
          ) : (
            <p>当前没有明显的数据问题，可以直接进入自动打标签。</p>
          )}
        </div>
      </div>
    </div>
  );
}

function ImportUploadWorkspace({
  jobs,
  uploadedFileCount,
  batchLimit,
  previewUsableRows,
  previewInvalidRows,
  importing,
  selectedFileName,
  onPickFile,
  onFile,
  onToggle,
  onDelete,
  onRevalidate,
  busyImportId
}: {
  jobs: ImportedDataJob[];
  uploadedFileCount: number;
  batchLimit: string;
  previewUsableRows: number;
  previewInvalidRows: number;
  importing: boolean;
  selectedFileName: string;
  onPickFile: () => void;
  onFile: (file: File | undefined) => void;
  onToggle: (jobId: string) => void;
  onDelete: (jobId: string) => void;
  onRevalidate: (jobId: string) => void;
  busyImportId: string | null;
}) {
  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    onFile(event.dataTransfer.files?.[0]);
  };

  return (
    <div
      className="upload-list-card"
      onDragOver={event => event.preventDefault()}
      onDrop={handleDrop}
    >
      <div className="import-status-strip upload-stats-strip">
        <StatBlock title="已上传文件数" value={uploadedFileCount.toLocaleString()} detail="当前项目数据文件" />
        <StatBlock title="批量上限" value={batchLimit} detail="单次导入建议上限" />
        <StatBlock title="预计有效数据" value={previewUsableRows.toLocaleString()} detail="内容列非空、非空格、非乱码" />
        <StatBlock title="预计不进入分析数据" value={previewInvalidRows.toLocaleString()} detail="仅统计空内容和乱码内容" />
      </div>
      <button type="button" className="upload-drop-surface" onClick={onPickFile}>
        <UploadCloud size={30} />
        <strong>拖拽或选择 Excel / CSV 数据文件</strong>
        <span>整个区域都可以拖拽上传，也可以点击选择文件。上传后会在下方列表显示统计和下载入口。</span>
        <em>{importing ? '正在解析文件...' : selectedFileName || '支持 .xlsx / .csv，最多预览 100,000 行'}</em>
      </button>
      <ImportedDataList
        jobs={jobs}
        onToggle={onToggle}
        onDelete={onDelete}
        onRevalidate={onRevalidate}
        busyImportId={busyImportId}
        compact
      />
    </div>
  );
}

function ImportedDataList({
  jobs,
  onToggle,
  onDelete,
  onRevalidate,
  busyImportId,
  compact = false
}: {
  jobs: ImportedDataJob[];
  onToggle: (jobId: string) => void;
  onDelete: (jobId: string) => void;
  onRevalidate: (jobId: string) => void;
  busyImportId: string | null;
  compact?: boolean;
}) {
  return (
    <div className={`data-table-card imported-data-list ${compact ? 'compact-upload-list' : ''}`}>
      <div className="table-card-head">
        <h3>已上传数据文件</h3>
        <span>可选择哪些数据版本纳入当前项目分析，旧版本可以保留但不参与统计。</span>
      </div>
      <table className="simple-table">
        <thead>
          <tr><th>纳入分析</th><th>文件名</th><th>有效数据</th><th>问题数据</th><th>上传人</th><th>上传时间</th><th>文件大小</th><th>操作</th></tr>
        </thead>
        <tbody>
          {jobs.length > 0 ? jobs.map(job => (
            <tr key={job.id}>
              <td>
                <label className="report-check">
                  <input type="checkbox" checked={job.included} onChange={() => onToggle(job.id)} />
                  <span>{job.included ? '纳入' : '剔除'}</span>
                </label>
              </td>
              <td><strong>{job.filename}</strong><small>总数据 {job.total_rows.toLocaleString()} / {job.status}</small></td>
              <td>{job.imported_rows.toLocaleString()}</td>
              <td>{job.invalid_rows.toLocaleString()} 内容问题 <small>{job.duplicate_rows.toLocaleString()} 重复提示</small></td>
              <td>{job.owner.name}</td>
              <td>{job.created_at}</td>
              <td>{job.file_size_label}</td>
              <td>
                <div className="project-row-actions import-row-actions">
                  {job.download_url ? (
                    <a className="tiny-action download-link" href={job.download_url} download={job.filename}>下载</a>
                  ) : (
                    <button type="button" className="tiny-action" disabled>下载</button>
                  )}
                  <button type="button" className="tiny-action" disabled={busyImportId === job.id} onClick={() => onRevalidate(job.id)}>
                    {busyImportId === job.id ? '处理中' : '重新校验'}
                  </button>
                  <button type="button" className="tiny-action danger-action" disabled={busyImportId === job.id} onClick={() => onDelete(job.id)}>删除</button>
                </div>
              </td>
            </tr>
          )) : (
            <tr>
              <td colSpan={8}>
                <div className="project-empty-state">
                  <strong>还没有上传数据</strong>
                  <span>请先选择 Excel 或 CSV 文件，系统会在这里保留每一次上传结果。</span>
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function ImportHistoryPanel({
  jobs,
  onNavigate
}: {
  jobs: ImportedDataJob[];
  onNavigate: (view: string) => void;
}) {
  return (
    <div className="data-table-card">
      <div className="table-card-head">
        <h3>导入历史</h3>
        <span>每次导入都保留文件、去重结果、负责人、状态和版本入口</span>
      </div>
      <table className="simple-table">
        <thead>
          <tr><th>文件名</th><th>状态</th><th>总行数</th><th>有效导入</th><th>重复</th><th>无效</th><th>负责人</th><th>时间</th><th>下一步</th></tr>
        </thead>
        <tbody>
          {jobs.map(job => (
            <tr key={job.id}>
              <td>{job.filename}</td>
              <td><span className="status-pill">{job.status}</span></td>
              <td>{job.total_rows.toLocaleString()}</td>
              <td>{job.imported_rows.toLocaleString()}</td>
              <td>{job.duplicate_rows.toLocaleString()}</td>
              <td>{job.invalid_rows.toLocaleString()}</td>
              <td>{job.owner.name}</td>
              <td>{job.created_at}</td>
              <td><button type="button" className="tiny-action" onClick={() => onNavigate('auto')}>自动打标</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DataPreviewPanel({
  dashboard,
  preview
}: {
  dashboard: DashboardResponse;
  preview?: ImportPreviewResponse | null;
}) {
  const previewRows = preview?.samples ?? [];
  return (
    <div className="preview-layout">
      <div className="data-table-card">
        <div className="table-card-head">
          <h3>导入数据预览</h3>
          <span>按当前字段映射抽取前 3 条样本</span>
        </div>
        <table className="simple-table">
          <thead>
            <tr><th>评论ID</th><th>平台</th><th>评论内容</th><th>内容链接</th><th>品牌</th><th>报告统计</th></tr>
          </thead>
          <tbody>
            {previewRows.length > 0 ? previewRows.map((row, index) => (
              <tr key={`${row.comment_id}-${index}`}>
                <td>{tailId(row.comment_id ?? '', 6)}</td>
                <td>{row.platform || preview?.inferred_platform || '-'}</td>
                <td>{row.content}</td>
                <td>{row['source_content.url'] ? '已生成' : '-'}</td>
                <td>{detectBrands(row.content ?? '').join('、') || '-'}</td>
                <td>待确认</td>
              </tr>
            )) : dashboard.records.map(record => (
              <tr key={record.id}>
                <td>{tailId(record.id, 6)}</td>
                <td>{record.platform}</td>
                <td>{record.content}</td>
                <td>{record.source_content.url ? '已识别' : '-'}</td>
                <td>{record.brands.join('、') || '-'}</td>
                <td>{record.report_candidate ? '纳入' : '排除'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="cleaning-panel">
        <h3>清洗规则配置</h3>
        {(preview?.quality_issues.map(issue => issue.rule) ?? ['空内容', '纯符号表情', '纯@他人', '乱码内容', '重复评论', '缺失平台']).map((rule, index) => (
          <label key={rule}>
            <span>{rule}</span>
            <input type="checkbox" defaultChecked={preview?.quality_issues[index]?.enabled ?? index < 5} />
          </label>
        ))}
      </div>
    </div>
  );
}

function RuleRunChecklist({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <div className="ops-grid">
      {[
        ['品牌识别', `${dashboard.brand_rules.length} 个品牌规则`, '识别本品、竞品、别名和错字输入'],
        ['标签保护', '人工确认优先', '规则重跑不会覆盖人工黄点'],
        ['冲突复核', '自动生成队列', '自动标签和人工标签不一致时进入复核'],
        ['报告候选', '复选框控制', '只有纳入样本进入报告统计']
      ].map(([title, value, detail]) => (
        <StatBlock key={title} title={title} value={value} detail={detail} />
      ))}
    </div>
  );
}

function RuleEvidenceTable({
  samples,
  onUpdate,
  onDelete
}: {
  samples: EvidenceSample[];
  onUpdate: (sampleId: string, patch: Partial<EvidenceSample>) => void;
  onDelete: (sampleId: string) => void;
}) {
  const [query, setQuery] = React.useState('');
  const [sortBy, setSortBy] = React.useState<'created' | 'keyword'>('created');
  const visibleSamples = samples
    .filter(sample => {
      const term = query.trim();
      if (!term) return true;
      return [sample.content, sample.source_rule_name, sample.label_before, sample.label_after].join(' ').includes(term);
    })
    .sort((left, right) => sortBy === 'keyword'
      ? right.keyword_count - left.keyword_count
      : right.created_at.localeCompare(left.created_at)
    );
  return (
    <div className="data-table-card">
      <div className="table-card-head">
        <h3>规则学习证据样本</h3>
        <span>共 {samples.length} 条，当前显示 {visibleSamples.length} 条，可筛选、排序、编辑和删除。</span>
        <div className="evidence-controls">
          <input value={query} onChange={event => setQuery(event.target.value)} placeholder="搜索内容、规则或标签" />
          <select value={sortBy} onChange={event => setSortBy(event.target.value as 'created' | 'keyword')}>
            <option value="created">按加入时间</option>
            <option value="keyword">按关键词数量</option>
          </select>
        </div>
      </div>
      <table className="simple-table">
        <thead>
          <tr><th>评论ID</th><th>样本内容</th><th>归属规则</th><th>应用前</th><th>应用后</th><th>关键词数</th><th>加入时间</th><th>操作</th></tr>
        </thead>
        <tbody>
          {visibleSamples.map(sample => (
            <tr key={sample.id}>
              <td>{tailId(sample.record_id, 6)}</td>
              <td><textarea className="table-textarea evidence-text" value={sample.content} onChange={event => onUpdate(sample.id, { content: event.target.value })} /></td>
              <td>{sample.source_rule_name}</td>
              <td><input className="table-input" value={sample.label_before} onChange={event => onUpdate(sample.id, { label_before: event.target.value })} /></td>
              <td><input className="table-input" value={sample.label_after} onChange={event => onUpdate(sample.id, { label_after: event.target.value })} /></td>
              <td><input className="table-input narrow" inputMode="numeric" value={sample.keyword_count} onChange={event => onUpdate(sample.id, { keyword_count: Number(event.target.value) || 0 })} /></td>
              <td>{sample.created_at}</td>
              <td><button type="button" className="tiny-action danger-action" onClick={() => onDelete(sample.id)}>删除</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ReportOpsPanel({ dashboard }: { dashboard: DashboardResponse }) {
  return (
    <div className="report-ops-grid">
      <div className="data-table-card">
        <div className="table-card-head">
          <h3>导出记录</h3>
          <span>同一项目可保留多版本文件</span>
        </div>
        <table className="simple-table">
          <thead>
            <tr><th>文件名</th><th>格式</th><th>版本</th><th>状态</th><th>大小</th><th>负责人</th><th>时间</th></tr>
          </thead>
          <tbody>
            {dashboard.export_records.map(record => (
              <tr key={record.id}>
                <td>{record.filename}</td>
                <td>{record.format}</td>
                <td>{record.report_version}</td>
                <td><span className="status-pill">{record.status}</span></td>
                <td>{record.size}</td>
                <td>{record.owner.name}</td>
                <td>{record.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="report-checklist">
        <h3>发布前检查</h3>
        {['报告文字已确认', '图表口径已确认', '重点样本已纳入', '导出命名已选择', 'Word / PDF / PPT 均可生成'].map((item, index) => (
          <label key={item}>
            <span>{item}</span>
            <input type="checkbox" defaultChecked={index < 3} />
          </label>
        ))}
      </div>
    </div>
  );
}

function AuditTrail({ dashboard }: { dashboard: DashboardResponse }) {
  const rows = dashboard.records
    .flatMap(record => Object.values(record.labels).filter(label => label.confirmed && label.confirmed_by).map(label => ({
      record,
      label
    })))
    .slice(0, 6);
  return (
    <div className="data-table-card">
      <div className="table-card-head">
        <h3>最近人工确认记录</h3>
        <span>用于追踪是谁在什么时候修改了标签</span>
      </div>
      <table className="simple-table">
        <thead>
          <tr><th>评论ID</th><th>用户</th><th>角色</th><th>时间</th><th>修改</th></tr>
        </thead>
        <tbody>
          {rows.map(({ record, label }, index) => (
            <tr key={`${record.id}-${index}`}>
              <td>{tailId(record.id, 6)}</td>
              <td>{label.confirmed_by?.name}</td>
              <td>{label.confirmed_by?.role}</td>
              <td>{label.confirmed_at}</td>
              <td>{label.previous_value ?? '自动'} → {label.final ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BrandRuleList({ dashboard }: { dashboard: DashboardResponse }) {
  const [rules, setRules] = React.useState<BrandRule[]>(dashboard.brand_rules);
  React.useEffect(() => {
    setRules(dashboard.brand_rules);
  }, [dashboard.brand_rules]);
  const addRule = () => {
    setRules(current => [{
      id: `brand-custom-${Date.now()}`,
      brand: '新品牌',
      category: '母婴奶粉',
      aliases: ['新品牌'],
      products: ['新品牌奶粉'],
      typo_variants: [],
      competitor: true,
      enabled: true
    }, ...current]);
  };
  const updateRule = (ruleId: string, patch: Partial<BrandRule>) => {
    setRules(current => current.map(rule => rule.id === ruleId ? { ...rule, ...patch } : rule));
  };
  const deleteRule = (ruleId: string) => {
    setRules(current => current.filter(rule => rule.id !== ruleId));
  };
  const copyRule = (rule: BrandRule) => {
    setRules(current => [{ ...rule, id: `brand-copy-${Date.now()}`, brand: `${rule.brand} 副本` }, ...current]);
  };
  return (
    <div className="brand-rule-list">
      <div className="brand-rule-head">
        <h3>品牌与竞品识别规则</h3>
        <button type="button" className="primary-action" onClick={addRule}><Plus size={14} /> 新增品牌规则</button>
      </div>
      <div className="data-table-card">
        <table className="simple-table">
          <thead>
            <tr><th>品牌</th><th>类别</th><th>类型</th><th>别名</th><th>主力产品</th><th>口语/错字</th><th>启用</th><th>操作</th></tr>
          </thead>
          <tbody>
            {rules.map(rule => (
              <tr key={rule.id}>
                <td><input className="table-input" value={rule.brand} onChange={event => updateRule(rule.id, { brand: event.target.value })} /></td>
                <td><input className="table-input" value={rule.category} onChange={event => updateRule(rule.id, { category: event.target.value })} /></td>
                <td>
                  <select value={rule.competitor ? 'competitor' : 'self'} onChange={event => updateRule(rule.id, { competitor: event.target.value === 'competitor' })}>
                    <option value="self">本品</option>
                    <option value="competitor">竞品</option>
                  </select>
                </td>
                <td><textarea className="table-textarea" value={rule.aliases.join('、')} onChange={event => updateRule(rule.id, { aliases: splitTokenList(event.target.value) })} /></td>
                <td><textarea className="table-textarea" value={rule.products.join('、')} onChange={event => updateRule(rule.id, { products: splitTokenList(event.target.value) })} /></td>
                <td><textarea className="table-textarea" value={rule.typo_variants.join('、')} onChange={event => updateRule(rule.id, { typo_variants: splitTokenList(event.target.value) })} /></td>
                <td><input type="checkbox" checked={rule.enabled} onChange={event => updateRule(rule.id, { enabled: event.target.checked })} /></td>
                <td>
                  <div className="row-icon-actions">
                    <button type="button" title="复制" onClick={() => copyRule(rule)}><Copy size={14} /></button>
                    <button type="button" title="删除" onClick={() => deleteRule(rule.id)}><Trash2 size={14} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ViewHeader({
  title,
  copy,
  action,
  onAction
}: {
  title: string;
  copy: string;
  action: string;
  onAction?: () => void;
}) {
  return (
    <div className="view-header">
      <div>
        <h2>{title}</h2>
        <p>{copy}</p>
      </div>
      {action && onAction && <button type="button" onClick={onAction}>{action}</button>}
    </div>
  );
}

function applyAdvancedFilters(records: DataRecord[], filters: AdvancedFilters): DataRecord[] {
  const minLikes = parseNumberFilter(filters.minLikes);
  const minReplies = parseNumberFilter(filters.minReplies);
  return records.filter(record => {
    if (filters.platform && record.platform !== filters.platform) return false;
    if (filters.commentType && !commentTypeTags(record).includes(filters.commentType)) return false;
    if (minLikes !== null && record.engagement.likes < minLikes) return false;
    if (minReplies !== null && record.engagement.replies < minReplies) return false;
    if (filters.sentimentPolarity && record.labels.sentiment_polarity?.final !== filters.sentimentPolarity) return false;
    if (filters.cognition && record.labels.cognition?.final !== filters.cognition) return false;
    if (filters.sentimentType && record.labels.sentiment_type?.final !== filters.sentimentType) return false;
    if (filters.action && record.labels.action?.final !== filters.action) return false;
    if (filters.brand && !record.brands.includes(filters.brand)) return false;
    if (filters.reportStatus === 'included' && !record.report_candidate) return false;
    if (filters.reportStatus === 'excluded' && record.report_candidate) return false;
    return true;
  });
}

function sortRecords(records: DataRecord[], sortKey: SortKey, direction: SortDirection): DataRecord[] {
  if (sortKey === 'none') return records;
  const factor = direction === 'desc' ? -1 : 1;
  return [...records].sort((a, b) => {
    const left = sortValue(a, sortKey);
    const right = sortValue(b, sortKey);
    if (left === right) return a.id.localeCompare(b.id);
    return left > right ? factor : -factor;
  });
}

function sortValue(record: DataRecord, sortKey: SortKey): number {
  if (sortKey === 'comment_likes') return record.engagement.likes;
  if (sortKey === 'comment_replies') return record.engagement.replies;
  if (sortKey === 'comment_total') return record.engagement.likes + record.engagement.replies;
  if (sortKey === 'comment_publish_time') return parseDateValue(record.publish_time);
  if (sortKey === 'source_publish_time') return parseDateValue(record.source_content.publish_time);
  if (sortKey === 'source_comments') return record.source_content.comments;
  if (sortKey === 'source_likes') return record.source_content.likes;
  if (sortKey === 'source_favorites') return record.source_content.favorites;
  if (sortKey === 'source_shares') return record.source_content.shares;
  return 0;
}

function buildTableStats(records: DataRecord[], schema: LabelSchema) {
  const sentiment = countLabels(records, schema, 'sentiment_polarity');
  const cognition = countLabels(records, schema, 'cognition');
  const emotion = countLabels(records, schema, 'sentiment_type');
  const action = countLabels(records, schema, 'action');
  const reportIncluded = records.filter(record => record.report_candidate).length;
  return {
    total: records.length,
    reportIncluded,
    reportExcluded: records.length - reportIncluded,
    topSentiment: topCount(sentiment),
    topCognition: topCount(cognition),
    topEmotion: topCount(emotion),
    topAction: topCount(action),
    sentimentSummary: summarizeCounts(sentiment),
    cognitionSummary: summarizeCounts(cognition),
    emotionSummary: summarizeCounts(emotion),
    actionSummary: summarizeCounts(action)
  };
}

function countLabels(records: DataRecord[], schema: LabelSchema, fieldKey: string): Record<string, number> {
  return records.reduce<Record<string, number>>((counts, record) => {
    const label = optionLabel(schema, fieldKey, record.labels[fieldKey]?.final);
    counts[label] = (counts[label] ?? 0) + 1;
    return counts;
  }, {});
}

function topCount(counts: Record<string, number>): string {
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  return top ? `${top[0]} ${top[1]}` : '无数据';
}

function summarizeCounts(counts: Record<string, number>): string {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return entries.length ? entries.map(([label, count]) => `${label} ${count}`).join(' / ') : '无数据';
}

function formatRuleCounts(counts: Record<string, number>): string {
  const labelMap: Record<string, string> = {
    positive: '正面',
    neutral: '中性',
    negative: '负面'
  };
  return Object.entries(counts)
    .map(([key, value]) => `${labelMap[key] ?? key} ${value}`)
    .join(' / ');
}

function parseNumberFilter(value: string): number | null {
  const normalized = Number(value);
  return Number.isFinite(normalized) && normalized >= 0 ? normalized : null;
}

function parseDateValue(value?: string | null): number {
  if (!value) return 0;
  const parsed = Date.parse(value.replace(/-/g, '/'));
  return Number.isFinite(parsed) ? parsed : 0;
}

function uniqueOptions(values: string[]): string[] {
  return Array.from(new Set(values.map(value => value.trim()).filter(Boolean)));
}

function toggleListValue(values: string[], value: string): string[] {
  return values.includes(value) ? values.filter(item => item !== value) : [...values, value];
}

function splitSchemaNames(value: string): string[] {
  return value.split('+').map(item => item.trim()).filter(Boolean);
}

function splitTokenList(value: string): string[] {
  return value.split(/[、,，\n]/).map(item => item.trim()).filter(Boolean);
}

function buildInitialEvidenceSamples(dashboard: DashboardResponse): EvidenceSample[] {
  const latestRule = dashboard.rule_sets.find(rule => dashboard.active_project.selected_rule_set_ids.includes(rule.id))
    ?? dashboard.rule_sets[0];
  return dashboard.records
    .filter(record => Object.values(record.labels).some(label => label.previous_value))
    .map((record, index) => ({
      id: `ev-seed-${record.id}-${index}`,
      record_id: record.id,
      content: record.content,
      source_rule_set_id: latestRule?.id ?? 'rules-seed',
      source_rule_name: latestRule ? `${latestRule.name} ${latestRule.version}` : '历史规则证据',
      label_before: optionLabel(dashboard.label_schema, 'sentiment_type', record.labels.sentiment_type?.previous_value),
      label_after: optionLabel(dashboard.label_schema, 'sentiment_type', record.labels.sentiment_type?.final),
      keyword_count: record.matched_keywords.length,
      created_at: '2026-06-05 14:22'
    }));
}

function tailId(value: string, length: number): string {
  const compact = value.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '');
  return compact.length <= length ? compact : compact.slice(-length);
}

function formatTopics(topics: string[]): string[] {
  return topics.slice(0, 3).map(topic => {
    const normalized = topic.trim();
    return normalized.startsWith('#') ? normalized : `#${normalized}`;
  });
}

function detectBrands(content: string): string[] {
  const terms = ['a2', '爱他美', '飞鹤', '金领冠', '合生元', '美素佳儿', '完达山', '君乐宝', '贝因美', '伊利', '圣元', '蒙牛', '澳优', '雅士利'];
  const lower = content.toLowerCase();
  return terms.filter(term => lower.includes(term.toLowerCase())).slice(0, 5);
}

function importFieldMappings() {
  return [
    { source: '评论ID', target: 'id', required: true, confidence: 98, sample: 'r-001' },
    { source: '平台', target: 'platform', required: true, confidence: 96, sample: '小红书' },
    { source: '评论内容', target: 'content', required: true, confidence: 99, sample: '不敢喝了，有没有事啊？' },
    { source: '评论发布时间', target: 'publish_time', required: false, confidence: 92, sample: '2026-05-22' },
    { source: '评论作者', target: 'author', required: false, confidence: 88, sample: '小小妈妈' },
    { source: '评论点赞数', target: 'engagement.likes', required: false, confidence: 91, sample: '128' },
    { source: '评论回复数', target: 'engagement.replies', required: false, confidence: 86, sample: '18' },
    { source: '内容ID', target: 'source_content.id', required: false, confidence: 90, sample: 'note-001' },
    { source: '内容链接', target: 'source_content.url', required: false, confidence: 94, sample: 'https://...' },
    { source: '内容话题标签', target: 'source_content.topics', required: false, confidence: 83, sample: '#奶粉 #母婴' },
    { source: '内容发布者', target: 'source_content.author', required: false, confidence: 87, sample: '母婴观察号' },
    { source: '内容发布时间', target: 'source_content.publish_time', required: false, confidence: 89, sample: '2026-05-22 09:18' },
    { source: '内容评论数', target: 'source_content.comments', required: false, confidence: 84, sample: '240' },
    { source: '内容点赞数', target: 'source_content.likes', required: false, confidence: 84, sample: '1840' },
    { source: '内容收藏数', target: 'source_content.favorites', required: false, confidence: 79, sample: '316' },
    { source: '内容分享数', target: 'source_content.shares', required: false, confidence: 79, sample: '72' }
  ];
}

createRoot(document.getElementById('root')!).render(<App />);
