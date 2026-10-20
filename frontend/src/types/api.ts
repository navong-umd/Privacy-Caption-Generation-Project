// Mirrors webapi/models.py. Keep in sync with the FastAPI response models.

export interface Banner {
  kind: "bootstrap" | "weak" | "llm" | "judge" | "none";
  text: string;
}

export interface PipelineStage {
  key: string;
  title: string;
  tool: string;
  description: string;
  inputs: string;
  outputs: string;
}

export interface Overview {
  title: string;
  summary: string;
  data_root: string;
  n_apps: number;
  n_prcs: number;
  n_captions_llm: number;
  n_captions_mock: number;
  splits: Record<string, number>;
  practice_macro_f1: number | null;
  purpose_macro_f1: number | null;
  n_test: number | null;
  caption_judge: Record<string, number> | null;
  banners: Banner[];
  pipeline: PipelineStage[];
}

export interface AppSummary {
  package: string;
  display_name: string;
  n_prcs: number;
  collected: string[];
  purposes: string[];
  shared_with: string[];
  gdpr_reqs: number;
  ccpa_reqs: number;
  completeness: number | null;
}

export interface NameCount {
  name: string;
  count: number;
}

export interface CaptionRow {
  prcs_id: string;
  app_package: string;
  caption: string;
  provider: string;
  label_source: string;
  baseline_caption: string | null;
}

export interface AppDetail extends AppSummary {
  top_pi_categories: NameCount[];
  top_sink_types: NameCount[];
  gdpr: string[];
  ccpa: string[];
  sample_captions: CaptionRow[];
}

export interface PrcsListItem {
  prcs_id: string;
  app_package: string;
  class_name: string;
  method_name: string;
  source_api: string;
  sink_api: string;
  sink_type: string;
  pi_type: string;
  pi_category: string;
  permission: string;
  privacy_threat: string;
  hop_count: number;
  n_nodes: number;
  n_edges: number;
  label_source: string;
  practice: string[];
  purpose: string[];
  split: string;
}

export interface GraphNode {
  id: string;
  label?: string | null;
  type?: string | null;
  callee?: string | null;
  code?: string | null;
}

export interface GraphEdge {
  start: string;
  end: string;
  type: string;
  taint_rule?: string | null;
}

export interface Subgraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface PrcsDetail {
  prcs_id: string;
  app_package: string;
  apk_filename: string | null;
  class_name: string;
  method_name: string;
  method_signature: string | null;
  source_api: string;
  sink_api: string;
  sink_type: string;
  sink_label: string | null;
  pi_type: string;
  pi_category: string;
  permission: string;
  privacy_threat: string;
  hop_count: number;
  involved_methods: string[];
  code_snippet: string;
  subgraph: Subgraph;
  taint_path: string[] | null;
  taint_rules: string[] | null;
  label_source: string;
  practice: string[];
  purpose: string[];
  split: string;
  llm_caption: string | null;
  mock_caption: string | null;
  baseline_caption: string | null;
}

export interface LabelMetric {
  label: string;
  precision: number | null;
  recall: number | null;
  f1: number | null;
}

export interface ClassificationResults {
  banner: Banner;
  n_test: number | null;
  practice_macro_f1: number | null;
  practice_micro_f1: number | null;
  purpose_macro_f1: number | null;
  purpose_micro_f1: number | null;
  practice_labels: LabelMetric[];
  purpose_labels: LabelMetric[];
}

export interface CaptionResults {
  banner: Banner;
  judge: string | null;
  n_captions: number;
  llm_mean: Record<string, number> | null;
  baseline_mean: Record<string, number> | null;
  pairwise: Record<string, number> | null;
}

export interface ComplianceApp {
  package: string;
  display_name: string;
  facts: number;
  surfaced: number;
  completeness: number;
  gdpr_reqs: number;
  ccpa_reqs: number;
}

export interface ComplianceResults {
  overall_completeness: number | null;
  per_app: ComplianceApp[];
}

export interface ExperimentsStatus {
  available: boolean;
  logged_runs: number;
  note: string;
}

export interface DocMeta {
  slug: string;
  title: string;
  file: string;
}

export interface DocContent {
  slug: string;
  title: string;
  markdown: string;
}

export interface Page<T> {
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
  items: T[];
}

export type PrcsPage = Page<PrcsListItem>;
export type CaptionPage = Page<CaptionRow>;
