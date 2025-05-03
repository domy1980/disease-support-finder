export interface DiseaseInfo {
  disease_id: string;
  name_ja: string;
  name_en?: string;
  synonyms_ja?: string[];
  synonyms_en?: string[];
  is_intractable: boolean;
  is_childhood_chronic: boolean;
}

export interface SupportOrganization {
  name: string;
  url: string;
  type: "patient" | "family" | "support";
  description?: string;
}

export interface WebsiteAvailabilityRecord {
  url: string;
  check_date: string;
  is_available: boolean;
  status_code?: number;
  response_time_ms?: number;
  error_message?: string;
}

export interface EnhancedSupportOrganization extends SupportOrganization {
  source: "auto" | "manual";
  added_date: string;
  last_checked?: string;
  is_available: boolean;
  notes?: string;
  availability_history: WebsiteAvailabilityRecord[];
}

export interface ManualEntry {
  id: string;
  disease_id: string;
  title: string;
  content: string;
  url?: string;
  entry_type: string;
  created_at: string;
  updated_at: string;
}

export interface DiseaseWithOrganizations {
  disease: DiseaseInfo;
  organizations: SupportOrganization[];
}

export interface EnhancedDiseaseWithOrganizations {
  disease: DiseaseInfo;
  organizations: EnhancedSupportOrganization[];
  manual_entries: ManualEntry[];
}

export interface OrganizationStats {
  total_count: number;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
  available_count: number;
  unavailable_count: number;
  last_updated: string;
}

export interface DiseaseSearchStats {
  disease_id: string;
  disease_name: string;
  search_count: number;
  last_searched?: string;
  organization_stats: OrganizationStats;
}

export interface SearchRequest {
  query: string;
  include_synonyms: boolean;
}

export interface SearchResponse {
  results: DiseaseWithOrganizations[];
  total: number;
}

export interface DiseaseListResponse {
  results: DiseaseInfo[];
  total: number;
  intractable_count: number;
  childhood_chronic_count: number;
}

export interface SearchStatsResponse {
  results: DiseaseSearchStats[];
  total: number;
}

export interface OrganizationCollection {
  disease_id: string;
  disease_name: string;
  organizations: EnhancedSupportOrganization[];
  manual_entries: ManualEntry[];
  last_updated: string;
}

export interface OrganizationCollectionResponse {
  results: OrganizationCollection[];
  total: number;
}

export interface ManualEntryRequest {
  disease_id: string;
  title: string;
  content: string;
  url?: string;
  entry_type: string;
}

export interface ManualOrganizationRequest {
  disease_id: string;
  name: string;
  url: string;
  type: "patient" | "family" | "support";
  description?: string;
  notes?: string;
}

export interface WebsiteStatusResponse {
  disease_id: string;
  disease_name: string;
  total_organizations: number;
  available_count: number;
  unavailable_count: number;
  organizations: {
    name: string;
    url: string;
    is_available: boolean;
    last_checked: string | null;
    history: WebsiteAvailabilityRecord[];
  }[];
}

export interface AllWebsiteStatusResponse {
  total_diseases: number;
  total_organizations: number;
  available_count: number;
  unavailable_count: number;
  availability_rate: number;
  disease_summary: {
    disease_id: string;
    disease_name: string;
    total_organizations: number;
    available_count: number;
    unavailable_count: number;
  }[];
}
