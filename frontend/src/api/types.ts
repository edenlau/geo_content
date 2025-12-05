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
