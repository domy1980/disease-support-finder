import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SearchTerm {
  id: string;
  term: string;
  language: string;
  type: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface SearchConfig {
  disease_id: string;
  search_terms: SearchTerm[];
  max_token_limit: number;
  use_approximate_matching: boolean;
  two_step_validation: boolean;
  require_human_verification: boolean;
  last_updated: string;
}

export interface SearchTermRequest {
  term: string;
  language: string;
  type: string;
}

export const fetchSearchConfig = async (diseaseId: string): Promise<SearchConfig> => {
  const response = await axios.get(`${API_URL}/api/search-terms/config/${diseaseId}`);
  return response.data;
};

export const updateSearchConfig = async (diseaseId: string, configUpdate: Partial<SearchConfig>): Promise<SearchConfig> => {
  const response = await axios.post(`${API_URL}/api/search-terms/config/${diseaseId}`, configUpdate);
  return response.data;
};

export const addSearchTerm = async (diseaseId: string, termRequest: SearchTermRequest): Promise<SearchTerm> => {
  const response = await axios.post(`${API_URL}/api/search-terms/terms/${diseaseId}`, termRequest);
  return response.data;
};

export const updateSearchTerm = async (diseaseId: string, termId: string, termUpdate: Partial<SearchTerm>): Promise<SearchTerm> => {
  const response = await axios.put(`${API_URL}/api/search-terms/terms/${diseaseId}/${termId}`, termUpdate);
  return response.data;
};

export const deleteSearchTerm = async (diseaseId: string, termId: string): Promise<{ message: string }> => {
  const response = await axios.delete(`${API_URL}/api/search-terms/terms/${diseaseId}/${termId}`);
  return response.data;
};
