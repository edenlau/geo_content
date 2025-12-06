// API Types - matching backend Pydantic models

// Request types
export interface ContentGenerationRequest {
  client_name: string;
  target_question: string;
  reference_urls?: string[];
  reference_documents?: string[];
  language_override?: string;
  target_word_count?: number;
}

// Async job response
export interface AsyncJobResponse {
  job_id: string;
  status: JobStatus;
  status_url: string;
  message: string;
}

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

// Job status response
export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  created_at: string;
  completed_at?: string;
  result?: ContentGenerationResponse;
  error?: string;
}

// GEO Strategy Analysis (matches backend strategies array items)
export interface GEOStrategyAnalysis {
  strategy_name: string;
  applied_count: number;
  expected_boost: string;
  effectiveness: 'High' | 'Medium' | 'Low';
  examples: string[];
}

// E-E-A-T Data (matches backend eeat object)
export interface EEATData {
  score: number;
  experience: string[];
  expertise: string[];
  authority: string[];
  trust: string[];
}

// Selection info (matches backend selection object)
export interface SelectionData {
  selected: 'A' | 'B';
  score: number;
  rationale: string;
  advantages: string[];
}

// GEO Performance Commentary (matches actual backend response)
export interface GEOPerformanceCommentary {
  summary: {
    overall_assessment: string;
    predicted_visibility_improvement: string;
    confidence_level: 'High' | 'Medium' | 'Low';
  };
  strategies: GEOStrategyAnalysis[];
  eeat: EEATData;
  key_strengths: string[];
  selection: SelectionData;
  suggestions: string[];
}

// Evaluation Score
export interface EvaluationScore {
  statistics_score: number;
  citations_score: number;
  quotations_score: number;
  fluency_score: number;
  experience_score: number;
  expertise_score: number;
  authority_score: number;
  trust_score: number;
  opening_effectiveness: number;
  structure_quality: number;
  entity_mention_quality: number;
  language_accuracy: number;
}

// GEO Analysis summary (matches backend geo_analysis object)
export interface GEOAnalysis {
  statistics_count: number;
  citations_count: number;
  quotations_count: number;
  fluency_score: number;
  eeat_score?: number;
}

// Models used
export interface ModelsUsed {
  writer_a: string;
  writer_b: string;
  evaluator: string;
  research: string;
}

// Full content generation response
export interface ContentGenerationResponse {
  // Request tracking
  job_id: string;
  trace_id: string;
  trace_url: string;

  // Language
  detected_language: string;
  language_code: string;
  dialect: string | null;
  writing_direction: 'ltr' | 'rtl';

  // Generated content
  content: string;
  word_count: number;

  // Evaluation
  selected_draft: 'A' | 'B';
  evaluation_score: number;
  evaluation_iterations: number;

  // GEO Commentary
  geo_commentary: GEOPerformanceCommentary;
  geo_insights?: any; // Enhanced GEO insights (optional for backward compatibility)
  schema_markup: Record<string, unknown>;
  geo_analysis: GEOAnalysis;

  // Metadata
  generation_time_ms: number;
  models_used: ModelsUsed;
  timestamp: string;
}

// Language info
export interface LanguageInfo {
  code: string;
  name: string;
  region?: string;
  variants?: string[];
}

export interface LanguagesResponse {
  languages: LanguageInfo[];
  auto_detection: boolean;
  rtl_languages: string[];
}

// Strategy info
export interface StrategyInfo {
  name: string;
  visibility_boost: string;
  description: string;
  research: string;
}

export interface StrategiesResponse {
  strategies: StrategyInfo[];
  quality_threshold: number;
  max_iterations: number;
}

// Health check
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}

// File upload response
export interface FileUploadResponse {
  uploaded_files: string[];
  upload_count: number;
  errors: string[] | null;
}

// Job history item
export interface JobHistoryItem {
  job_id: string;
  client_name: string;
  target_question: string;
  evaluation_score: number;
  word_count: number;
  completed_at: string;
  generation_time_ms: number;
}

// Job history response
export interface JobHistoryResponse {
  jobs: JobHistoryItem[];
  total_count: number;
}

// =============================================================================
// CONTENT REWRITE TYPES
// =============================================================================

// Rewrite style and tone types
export type RewriteStyle = 'professional' | 'casual' | 'academic' | 'journalistic' | 'marketing';
export type RewriteTone = 'neutral' | 'enthusiastic' | 'authoritative' | 'conversational';

// Rewrite request
export interface ContentRewriteRequest {
  source_url?: string;
  source_file_path?: string;
  source_text?: string;
  style?: RewriteStyle;
  tone?: RewriteTone;
  preserve_structure?: boolean;
  target_word_count?: number;
  reference_urls?: string[];
  reference_documents?: string[];
  client_name?: string;
  language_override?: string;
}

// Comparison between original and rewritten content
export interface RewriteComparison {
  original_content: string;
  original_word_count: number;
  original_language: string;
  rewritten_content: string;
  rewritten_word_count: number;
  changes_summary: string[];
}

// GEO optimizations that were applied
export interface GEOOptimizationsApplied {
  statistics_added: number;
  statistics_original: number;
  citations_added: number;
  citations_original: number;
  quotations_added: number;
  quotations_original: number;
  fluency_improvements: string[];
  structure_changes: string[];
  eeat_enhancements: string[];
}

// Full rewrite response
export interface ContentRewriteResponse {
  // Request tracking
  job_id: string;
  trace_id: string;
  trace_url: string;

  // Language
  detected_language: string;
  language_code: string;
  writing_direction: 'ltr' | 'rtl';

  // Comparison
  comparison: RewriteComparison;

  // Optimizations
  optimizations_applied: GEOOptimizationsApplied;

  // Style/tone used
  style_applied: RewriteStyle;
  tone_applied: RewriteTone;

  // Evaluation
  evaluation_score: number;
  evaluation_iterations: number;

  // GEO Commentary
  geo_commentary: GEOPerformanceCommentary;
  geo_insights?: any;

  // Metadata
  generation_time_ms: number;
  models_used: ModelsUsed;
  timestamp: string;
}

// Rewrite job status response (extends base job status)
export interface RewriteJobStatusResponse {
  job_id: string;
  status: JobStatus;
  created_at: string;
  completed_at?: string;
  result?: ContentRewriteResponse;
  error?: string;
}

// Style info for dropdown
export interface RewriteStyleInfo {
  id: RewriteStyle;
  name: string;
  description: string;
}

// Tone info for dropdown
export interface RewriteToneInfo {
  id: RewriteTone;
  name: string;
  description: string;
}

// Styles response
export interface RewriteStylesResponse {
  styles: RewriteStyleInfo[];
  tones: RewriteToneInfo[];
}

// URL content preview
export interface UrlContentPreview {
  url: string;
  title: string;
  content_preview: string;
  full_content: string;
  word_count: number;
  language: string;
  fetch_time_ms: number;
}
