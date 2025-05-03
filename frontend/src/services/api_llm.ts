import { } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LLMModel {
  name: string;
  description: string;
}

export interface LLMModelsResponse {
  models: LLMModel[];
  default: string;
  note?: string;
  error?: string;
}

export const getAvailableModels = async (): Promise<LLMModelsResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/llm/models`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get available models');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting available models:', error);
    return {
      models: [
        { name: "mistral:latest", description: "バランスの取れた性能と速度（デフォルト）" },
        { name: "llama3:70b", description: "最高の精度（M4 Max 128GBで実行可能）" },
        { name: "tinyllama:latest", description: "軽量で高速（精度は低下）" }
      ],
      default: "mistral:latest",
      error: error instanceof Error ? error.message : String(error)
    };
  }
};

export const runLLMSearchForDisease = async (diseaseId: string, model: string = 'mistral:latest'): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_URL}/api/llm/search/run/${diseaseId}?ollama_model=${model}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to run LLM search');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error running LLM search for disease:', error);
    throw error;
  }
};

export const runLLMSearchForAllDiseases = async (model: string = 'mistral:latest', maxDiseases: number = 0): Promise<{ message: string }> => {
  try {
    const url = new URL(`${API_URL}/api/llm/search/run-all`);
    url.searchParams.append('ollama_model', model);
    if (maxDiseases > 0) {
      url.searchParams.append('max_diseases', maxDiseases.toString());
    }
    
    const response = await fetch(url.toString(), {
      method: 'POST',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to run LLM search for all diseases');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error running LLM search for all diseases:', error);
    throw error;
  }
};

export const getLLMSearchStatus = async (): Promise<{ daily_search_running: boolean; stats_count: number; collections_count: number }> => {
  try {
    const response = await fetch(`${API_URL}/api/llm/search/status`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get LLM search status');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting LLM search status:', error);
    throw error;
  }
};

export const getLLMSearchProgress = async (): Promise<{
  total_diseases: number;
  searched_diseases: number;
  progress_percentage: number;
  remaining_diseases: number;
  estimated_remaining_time: {
    hours: number;
    minutes: number;
    seconds: number;
  };
}> => {
  try {
    const response = await fetch(`${API_URL}/api/llm/search/progress`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get LLM search progress');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting LLM search progress:', error);
    throw error;
  }
};
