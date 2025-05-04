import { DiseaseInfo, SupportOrganization, OrganizationStats } from './index';

export enum LLMValidationStatus {
  PENDING = "pending",
  EXTRACTED = "extracted",
  VERIFIED = "verified",
  HUMAN_APPROVED = "human_approved",
  REJECTED = "rejected"
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  model: string;
  timestamp: string;
}

export interface SearchTerm {
  id: string;
  term: string;
  language: string;
  type: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface LLMSearchConfig {
  disease_id: string;
  search_terms: SearchTerm[];
  max_token_limit: number;
  use_approximate_matching: boolean;
  two_step_validation: boolean;
  require_human_verification: boolean;
  last_updated: string;
}

export interface LLMValidatedOrganization extends SupportOrganization {
  validation_status: LLMValidationStatus;
  validation_score: number;
  validation_notes?: string;
  token_usage: TokenUsage[];
  human_verified: boolean;
  human_verification_date?: string;
  human_verification_notes?: string;
}

export interface LLMSearchStats {
  disease_id: string;
  disease_name: string;
  search_count: number;
  last_searched?: string;
  organization_stats: OrganizationStats;
  token_usage: TokenUsage[];
  search_terms_used: string[];
  approximate_matches_found: number;
  verified_organizations: number;
  human_approved_organizations: number;
  rejected_organizations: number;
}

export interface LLMOrganizationCollection {
  disease_id: string;
  disease_name: string;
  organizations: LLMValidatedOrganization[];
  last_updated: string;
  search_config?: LLMSearchConfig;
  token_usage: TokenUsage[];
}

export interface LLMValidationRequest {
  validation_notes?: string;
  approve: boolean;
}
