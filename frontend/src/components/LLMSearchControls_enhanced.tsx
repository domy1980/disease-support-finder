import React, { useState, useEffect } from 'react';
import { 
  runLLMSearchForAllDiseases, 
  getLLMSearchStatus, 
  getLLMSearchProgress,
} from '../services/api_llm_enhanced';
import LLMProviderSelector from './LLMProviderSelector';

export const EnhancedLLMSearchControls = () => {
  const [isRunningSearch, setIsRunningSearch] = useState(false);
  const [searchStatus, setSearchStatus] = useState<{
    daily_search_running: boolean;
    stats_count: number;
    collections_count: number;
  } | null>(null);
  const [searchProgress, setSearchProgress] = useState<{
    total_diseases: number;
    searched_diseases: number;
    progress_percentage: number;
    remaining_diseases: number;
    estimated_remaining_time: {
      hours: number;
      minutes: number;
      seconds: number;
    };
  } | null>(null);
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [selectedModel, setSelectedModel] = useState('mistral:latest');
  const [baseUrl, setBaseUrl] = useState('http://localhost:11434');
  const [maxDiseases, setMaxDiseases] = useState(10);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadSearchStatus();
    loadSearchProgress();
    const interval = setInterval(() => {
      loadSearchStatus();
      loadSearchProgress();
    }, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);
  
  const handleProviderChange = (provider: string, model: string, url: string) => {
    setSelectedProvider(provider);
    setSelectedModel(model);
    setBaseUrl(url);
  };

  const loadSearchStatus = async () => {
    try {
      const status = await getLLMSearchStatus();
      setSearchStatus(status);
    } catch (err) {
      console.error('Error loading LLM search status:', err);
    }
  };

  const loadSearchProgress = async () => {
    try {
      const progress = await getLLMSearchProgress();
      setSearchProgress(progress);
    } catch (err) {
      console.error('Error loading LLM search progress:', err);
    }
  };

  const handleRunSearch = async () => {
    try {
      setIsRunningSearch(true);
      setError(null);
      setSuccess(null);
      
      const result = await runLLMSearchForAllDiseases(
        selectedProvider,
        selectedModel,
        baseUrl,
        maxDiseases
      );
      
      setSuccess(result.message);
      await loadSearchStatus();
      await loadSearchProgress();
    } catch (err) {
      setError('LLM検索の開始中にエラーが発生しました。');
      console.error('Error starting LLM search:', err);
    } finally {
      setIsRunningSearch(false);
    }
  };

  return (
    <div className="w-full space-y-6 border rounded-lg p-6 bg-white shadow-sm">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold">LLM拡張検索（マルチプロバイダー対応）</h2>
          <p className="text-muted-foreground">
            Ollama または LM Studio を使用して患者会データ収集の精度を向上させます
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 border border-red-200 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {success && (
        <div className="p-4 border border-green-200 bg-green-50 text-green-700 rounded-md">
          {success}
        </div>
      )}

      <LLMProviderSelector onProviderChange={handleProviderChange} />

      {searchStatus && (
        <div className="p-4 border rounded-md bg-blue-50">
          <h3 className="font-semibold mb-2">LLM検索ステータス</h3>
          <p>
            検索実行中: {searchStatus.daily_search_running ? 'はい' : 'いいえ'}
          </p>
          <p>
            統計データ数: {searchStatus.stats_count} 件
          </p>
          <p>
            収集データ数: {searchStatus.collections_count} 件
          </p>
        </div>
      )}

      {searchProgress && (
        <div className="p-4 border rounded-md bg-blue-50 mt-4">
          <h3 className="font-semibold mb-2">検索進捗状況</h3>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              className="bg-blue-600 h-2.5 rounded-full" 
              style={{ width: `${searchProgress.progress_percentage}%` }}
            ></div>
          </div>
          <p>
            進捗: {searchProgress.searched_diseases}/{searchProgress.total_diseases} 
            ({searchProgress.progress_percentage.toFixed(1)}%)
          </p>
          <p>
            残り: {searchProgress.remaining_diseases} 件
          </p>
          <p>
            推定残り時間: {searchProgress.estimated_remaining_time.hours}時間
            {searchProgress.estimated_remaining_time.minutes}分
            {searchProgress.estimated_remaining_time.seconds}秒
          </p>
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            最大疾患数 (0 = 無制限)
          </label>
          <input
            type="number"
            className="w-full px-3 py-2 border rounded-md"
            value={maxDiseases}
            onChange={(e) => setMaxDiseases(parseInt(e.target.value) || 0)}
            min="0"
            max="2871"
          />
          <p className="text-sm text-gray-500 mt-1">
            テスト用に少数の疾患で実行する場合は、10〜20程度の値を設定してください。
          </p>
        </div>

        <div className="flex gap-3">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            onClick={handleRunSearch}
            disabled={isRunningSearch || (searchStatus?.daily_search_running || false)}
          >
            {isRunningSearch ? 'LLM検索実行中...' : 'LLM拡張検索を実行'}
          </button>
          
          <button
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
            onClick={() => {
              loadSearchStatus();
              loadSearchProgress();
            }}
          >
            ステータス更新
          </button>
        </div>
      </div>
    </div>
  );
};
