export type AccountType = 'standard' | 'professional' | 'institutional';

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed';

export type ConclusionLevel =
  | 'no_major_alert'
  | 'review_recommended'
  | 'important_attention';

export type ProvenanceStatus =
  | 'verified'
  | 'partial'
  | 'unknown'
  | 'inconsistent';

export type IntegrityStatus =
  | 'clear'
  | 'review'
  | 'major_anomaly';

export type AIStatus =
  | 'indeterminate'
  | 'low'
  | 'moderate'
  | 'high'
  | 'declared';

export type ContextStatus =
  | 'coherent'
  | 'review'
  | 'potential_decontextualization';

export type EvidenceType =
  | 'technical_proof'
  | 'declared_info'
  | 'external_match'
  | 'estimation';

export type EvidenceSeverity = 'info' | 'positive' | 'warning' | 'critical';

export interface EvidenceItem {
  id: string;
  evidence_type: EvidenceType;
  title_fr: string;
  description_fr: string;
  source_engine: string;
  severity: EvidenceSeverity;
  reference_id?: string;
}

export interface AnalysisCreateResponse {
  analysis_id: string;
  public_id: string;
  status: AnalysisStatus;
  original_filename: string;
  file_size: number;
  sha256: string;
  access_token?: string;
  progress_url: string;
  created_at: string;
}

export interface AnalysisProgressResponse {
  analysis_id: string;
  public_id: string;
  status: AnalysisStatus;
  progress_percent: number;
  current_step?: string;
  steps: {
    engine_code: string;
    status: string;
    duration_ms?: number;
  }[];
  error_code?: string;
  public_error_message?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface AnalysisResultResponse {
  analysis_id: string;
  public_id: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  sha256: string;
  phash?: string;
  claim?: string;
  status: AnalysisStatus;
  has_original_file: boolean;
  conclusion_level?: ConclusionLevel;
  provenance_status?: ProvenanceStatus;
  integrity_status?: IntegrityStatus;
  ai_status?: AIStatus;
  context_status?: ContextStatus;
  summary_fr?: string;
  evidences: EvidenceItem[];
  created_at: string;
  completed_at?: string;
}
