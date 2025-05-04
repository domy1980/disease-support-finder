import { useEffect, useState } from 'react';
import { SearchStatsResponse } from '../types';
import { fetchAllStats, runSearchForAllDiseases, getSearchStatus } from '../services/api';
import { 
  runLLMSearchForAllDiseases, 
  getLLMSearchStatus
} from '../services/api_llm_enhanced';
import LLMProviderSelector from './LLMProviderSelector';

export const StatsDisplay = () => {
  const [stats, setStats] = useState<SearchStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchStatus, setSearchStatus] = useState<{
    daily_search_running: boolean;
    stats_count: number;
    collections_count: number;
  } | null>(null);
  const [isRunningSearch, setIsRunningSearch] = useState(false);
  const [isRunningLLMSearch, setIsRunningLLMSearch] = useState(false);
  const [llmSearchStatus, setLLMSearchStatus] = useState<{
    daily_search_running: boolean;
    stats_count: number;
    collections_count: number;
  } | null>(null);
  const [selectedProvider, setSelectedProvider] = useState('lmstudio');
  const [selectedModel, setSelectedModel] = useState('Qwen30B-A3B');
  const [baseUrl, setBaseUrl] = useState('http://localhost:1234/v1');
  const [maxDiseases, setMaxDiseases] = useState(0);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
    loadSearchStatus();
    loadLLMSearchStatus();
    const interval = setInterval(() => {
      loadSearchStatus();
      loadLLMSearchStatus();
    }, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);
  
  const handleProviderChange = (provider: string, model: string, url: string) => {
    setSelectedProvider(provider);
    setSelectedModel(model);
    setBaseUrl(url);
  };

  const loadStats = async () => {
    try {
      setIsLoading(true);
      const data = await fetchAllStats();
      setStats(data);
    } catch (err) {
      setError('統計情報の取得中にエラーが発生しました。');
      console.error('Error loading stats:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSearchStatus = async () => {
    try {
      const status = await getSearchStatus();
      setSearchStatus(status);
    } catch (err) {
      console.error('Error loading search status:', err);
    }
  };
  
  const loadLLMSearchStatus = async () => {
    try {
      const status = await getLLMSearchStatus();
      setLLMSearchStatus(status);
    } catch (err) {
      console.error('Error loading LLM search status:', err);
    }
  };

  const handleRunSearch = async () => {
    try {
      setIsRunningSearch(true);
      setError(null);
      setSuccess(null);
      await runSearchForAllDiseases();
      await loadSearchStatus();
      setSuccess('全疾患の検索が開始されました。このプロセスはバックグラウンドで実行され、完了までに時間がかかる場合があります。');
    } catch (err) {
      setError('検索の開始中にエラーが発生しました。');
      console.error('Error starting search:', err);
    } finally {
      setIsRunningSearch(false);
    }
  };
  
  const handleRunLLMSearch = async () => {
    try {
      setIsRunningLLMSearch(true);
      setError(null);
      setSuccess(null);
      
      const result = await runLLMSearchForAllDiseases(
        selectedProvider,
        selectedModel,
        baseUrl,
        maxDiseases
      );
      
      setSuccess(`LLM拡張検索が開始されました: ${result.message}`);
      await loadLLMSearchStatus();
    } catch (err) {
      setError('LLM検索の開始中にエラーが発生しました。');
      console.error('Error starting LLM search:', err);
    } finally {
      setIsRunningLLMSearch(false);
    }
  };

  if (isLoading) {
    return (
      <div className="w-full flex justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full p-4 border border-red-200 bg-red-50 text-red-700 rounded-md">
        {error}
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
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
    
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">検索統計情報</h2>
          {stats && (
            <p className="text-muted-foreground">
              統計情報: {stats.total} 件の疾患
            </p>
          )}
        </div>
        
        <div className="flex gap-3">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            onClick={handleRunSearch}
            disabled={isRunningSearch || (searchStatus?.daily_search_running || false)}
          >
            {isRunningSearch ? '実行中...' : '全疾患の検索を実行'}
          </button>
          
          <button
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
            onClick={() => {
              loadStats();
              loadSearchStatus();
              loadLLMSearchStatus();
            }}
          >
            更新
          </button>
        </div>
      </div>

      {searchStatus && (
        <div className="p-4 border rounded-md bg-blue-50">
          <h3 className="font-semibold mb-2">検索ステータス</h3>
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
      
      <div className="border rounded-lg p-6 bg-white shadow-sm">
        <h3 className="text-xl font-bold mb-4">LLM拡張検索</h3>
        <p className="text-muted-foreground mb-4">
          ローカルLLMを使用して患者会データ収集の精度を向上させます
        </p>
        
        <LLMProviderSelector onProviderChange={handleProviderChange} />
        
        <div className="mt-4">
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
        
        <div className="flex gap-3 mt-4">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            onClick={handleRunLLMSearch}
            disabled={isRunningLLMSearch || (llmSearchStatus?.daily_search_running || false)}
          >
            {isRunningLLMSearch ? 'LLM検索実行中...' : 'LLM拡張検索を実行'}
          </button>
        </div>
        
        {llmSearchStatus && (
          <div className="p-4 border rounded-md bg-blue-50 mt-4">
            <h3 className="font-semibold mb-2">LLM検索ステータス</h3>
            <p>
              LLM検索実行中: {llmSearchStatus.daily_search_running ? 'はい' : 'いいえ'}
            </p>
            <p>
              LLM統計データ数: {llmSearchStatus.stats_count} 件
            </p>
            <p>
              LLM収集データ数: {llmSearchStatus.collections_count} 件
            </p>
          </div>
        )}
      </div>

      {stats && stats.results.length === 0 ? (
        <div className="text-center p-8 border rounded-lg bg-muted/50">
          <p>統計情報がありません。「全疾患の検索を実行」ボタンをクリックして検索を開始してください。</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2 text-left">疾患名</th>
                <th className="border p-2 text-center">検索回数</th>
                <th className="border p-2 text-center">最終検索日時</th>
                <th className="border p-2 text-center">団体数</th>
                <th className="border p-2 text-center">患者会</th>
                <th className="border p-2 text-center">家族会</th>
                <th className="border p-2 text-center">支援団体</th>
              </tr>
            </thead>
            <tbody>
              {stats?.results.map((stat) => (
                <tr key={stat.disease_id} className="hover:bg-gray-50">
                  <td className="border p-2">{stat.disease_name}</td>
                  <td className="border p-2 text-center">{stat.search_count}</td>
                  <td className="border p-2 text-center">
                    {stat.last_searched 
                      ? new Date(stat.last_searched).toLocaleString('ja-JP')
                      : '-'}
                  </td>
                  <td className="border p-2 text-center">{stat.organization_stats.total_count}</td>
                  <td className="border p-2 text-center">{stat.organization_stats.by_type.patient || 0}</td>
                  <td className="border p-2 text-center">{stat.organization_stats.by_type.family || 0}</td>
                  <td className="border p-2 text-center">{stat.organization_stats.by_type.support || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
