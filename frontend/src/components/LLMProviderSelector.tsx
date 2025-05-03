import React, { useState, useEffect } from 'react';
import { getAvailableProviders, getAvailableModels, LLMProvider, LLMModel } from '../services/api_llm_enhanced';

interface LLMProviderSelectorProps {
  onProviderChange: (provider: string, model: string, baseUrl: string) => void;
}

const LLMProviderSelector: React.FC<LLMProviderSelectorProps> = ({ onProviderChange }) => {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('ollama');
  const [selectedModel, setSelectedModel] = useState<string>('mistral:latest');
  const [baseUrl, setBaseUrl] = useState<string>('http://localhost:11434');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProviders = async () => {
      try {
        setLoading(true);
        const response = await getAvailableProviders();
        setProviders(response.providers);
        
        const defaultProvider = response.default;
        setSelectedProvider(defaultProvider);
        
        const provider = response.providers.find(p => p.id === defaultProvider);
        if (provider) {
          setBaseUrl(provider.default_url);
        }
        
        setError(null);
      } catch (err) {
        setError('プロバイダーの読み込みに失敗しました');
        console.error('Error loading providers:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadProviders();
  }, []);
  
  useEffect(() => {
    const loadModels = async () => {
      try {
        setLoading(true);
        const response = await getAvailableModels(selectedProvider, baseUrl);
        setModels(response.models);
        
        setSelectedModel(response.default);
        
        setError(null);
      } catch (err) {
        setError('モデルの読み込みに失敗しました');
        console.error('Error loading models:', err);
      } finally {
        setLoading(false);
      }
    };
    
    if (selectedProvider && baseUrl) {
      loadModels();
    }
  }, [selectedProvider, baseUrl]);
  
  useEffect(() => {
    onProviderChange(selectedProvider, selectedModel, baseUrl);
  }, [selectedProvider, selectedModel, baseUrl, onProviderChange]);
  
  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProvider = e.target.value;
    setSelectedProvider(newProvider);
    
    const provider = providers.find(p => p.id === newProvider);
    if (provider) {
      setBaseUrl(provider.default_url);
    }
  };
  
  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedModel(e.target.value);
  };
  
  const handleBaseUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBaseUrl(e.target.value);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <h3 className="text-lg font-semibold mb-3">LLMプロバイダー設定</h3>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            プロバイダー
          </label>
          <select
            value={selectedProvider}
            onChange={handleProviderChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            disabled={loading}
          >
            {providers.map((provider) => (
              <option key={provider.id} value={provider.id}>
                {provider.name}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {providers.find(p => p.id === selectedProvider)?.description || ''}
          </p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            モデル
          </label>
          <select
            value={selectedModel}
            onChange={handleModelChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            disabled={loading}
          >
            {models.map((model) => (
              <option key={model.name} value={model.name}>
                {model.name}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {models.find(m => m.name === selectedModel)?.description || ''}
          </p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API URL
          </label>
          <input
            type="text"
            value={baseUrl}
            onChange={handleBaseUrlChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="http://localhost:11434"
            disabled={loading}
          />
          <p className="mt-1 text-xs text-gray-500">
            {selectedProvider === 'ollama' 
              ? 'Ollamaのデフォルト: http://localhost:11434' 
              : selectedProvider === 'mlx'
                ? 'MLXのデフォルト: http://localhost:8080'
                : 'LM Studioのデフォルト: http://localhost:1234/v1'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default LLMProviderSelector;
