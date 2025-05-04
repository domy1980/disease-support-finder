import axios from 'axios';
import { LLMOrganizationCollection, LLMValidationRequest } from '../types/llm_enhanced';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const fetchOrganizationCollection = async (diseaseId: string): Promise<LLMOrganizationCollection> => {
  const response = await axios.get(`${API_URL}/api/validation/organizations/${diseaseId}`);
  return response.data;
};

export const validateOrganization = async (
  diseaseId: string, 
  organizationId: string, 
  validationRequest: LLMValidationRequest
): Promise<any> => {
  const response = await axios.post(
    `${API_URL}/api/validation/organizations/${diseaseId}/${organizationId}`, 
    validationRequest
  );
  return response.data;
};

export const getValidationStats = async (diseaseId: string): Promise<any> => {
  const response = await axios.get(`${API_URL}/api/validation/stats/${diseaseId}`);
  return response.data;
};

export const getAllValidationStats = async (): Promise<any> => {
  const response = await axios.get(`${API_URL}/api/validation/stats`);
  return response.data;
};
