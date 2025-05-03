import { useEffect, useState } from 'react';
import { WebsiteStatusResponse, AllWebsiteStatusResponse, OrganizationCollection } from '../types';
import { 
  getWebsiteStatusForDisease, 
  getAllWebsiteStatus, 
  checkWebsitesForDisease,
  checkAllWebsites,
  getWebsiteHistory
} from '../services/api';

interface WebsiteStatusTrackerProps {
  diseaseId?: string;
  diseaseName?: string;
  organizationData?: OrganizationCollection | null;
}

export const WebsiteStatusTracker = ({ diseaseId, diseaseName, organizationData }: WebsiteStatusTrackerProps) => {
  const [diseaseStatus, setDiseaseStatus] = useState<WebsiteStatusResponse | null>(null);
  const [allStatus, setAllStatus] = useState<AllWebsiteStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [selectedUrl, setSelectedUrl] = useState<string | null>(null);
  const [urlHistory, setUrlHistory] = useState<any | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  
  useEffect(() => {
    if (organizationData) {
      console.log('Organization data available:', organizationData);
    }
  }, [organizationData]);

  useEffect(() => {
    loadData();
  }, [diseaseId]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      if (diseaseId) {
        const status = await getWebsiteStatusForDisease(diseaseId);
        setDiseaseStatus(status);
        setAllStatus(null);
      } else {
        const status = await getAllWebsiteStatus();
        setAllStatus(status);
        setDiseaseStatus(null);
      }
    } catch (err) {
      setError('ウェブサイト状態の取得中にエラーが発生しました。');
      console.error('Error loading website status:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckWebsites = async () => {
    try {
      setIsChecking(true);
      setError(null);
      
      if (diseaseId) {
        await checkWebsitesForDisease(diseaseId);
        alert(`${diseaseName || '選択された疾患'}のウェブサイト状態チェックが開始されました。`);
      } else {
        await checkAllWebsites();
        alert('全てのウェブサイト状態チェックが開始されました。このプロセスはバックグラウンドで実行され、完了までに時間がかかる場合があります。');
      }
      
      setTimeout(() => {
        loadData();
      }, 2000);
    } catch (err) {
      setError('ウェブサイトチェックの開始中にエラーが発生しました。');
      console.error('Error checking websites:', err);
    } finally {
      setIsChecking(false);
    }
  };

  const handleViewHistory = async (url: string) => {
    try {
      setSelectedUrl(url);
      setShowHistory(true);
      
      const history = await getWebsiteHistory(url);
      setUrlHistory(history);
    } catch (err) {
      console.error('Error getting website history:', err);
      alert('履歴の取得中にエラーが発生しました。');
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
    <div className="w-full space-y-6" data-selected-url={selectedUrl || ''}>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">
            {diseaseId 
              ? `${diseaseName || '疾患'} のウェブサイト状態`
              : 'すべての疾患のウェブサイト状態'}
          </h2>
          {diseaseStatus && (
            <p className="text-muted-foreground">
              団体数: {diseaseStatus.total_organizations} 件（利用可能: {diseaseStatus.available_count} 件、利用不可: {diseaseStatus.unavailable_count} 件）
            </p>
          )}
          {allStatus && (
            <p className="text-muted-foreground">
              疾患数: {allStatus.total_diseases} 件、団体数: {allStatus.total_organizations} 件
              （利用可能: {allStatus.available_count} 件、利用不可: {allStatus.unavailable_count} 件、
              可用率: {(allStatus.availability_rate * 100).toFixed(1)}%）
            </p>
          )}
        </div>
        
        <div className="flex gap-3">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            onClick={handleCheckWebsites}
            disabled={isChecking}
          >
            {isChecking ? 'チェック中...' : 'ウェブサイトをチェック'}
          </button>
          
          <button
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
            onClick={loadData}
          >
            更新
          </button>
        </div>
      </div>

      {showHistory && urlHistory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">ウェブサイト履歴</h3>
              <button
                className="text-gray-500 hover:text-gray-700"
                onClick={() => {
                  setShowHistory(false);
                  setUrlHistory(null);
                  setSelectedUrl(null);
                }}
              >
                ✕
              </button>
            </div>
            
            <div className="mb-4">
              <p><strong>URL:</strong> <a href={urlHistory.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{urlHistory.url}</a></p>
              <p><strong>名前:</strong> {urlHistory.name}</p>
              <p><strong>疾患:</strong> {urlHistory.disease_name}</p>
              <p><strong>現在の状態:</strong> {urlHistory.is_available ? '利用可能' : '利用不可'}</p>
              <p><strong>最終チェック:</strong> {urlHistory.last_checked ? new Date(urlHistory.last_checked).toLocaleString('ja-JP') : '未チェック'}</p>
            </div>
            
            <h4 className="font-semibold mb-2">履歴</h4>
            {urlHistory.history.length === 0 ? (
              <p>履歴データがありません。</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border p-2">日時</th>
                      <th className="border p-2">状態</th>
                      <th className="border p-2">ステータスコード</th>
                      <th className="border p-2">応答時間</th>
                      <th className="border p-2">エラー</th>
                    </tr>
                  </thead>
                  <tbody>
                    {urlHistory.history.map((record: any, index: number) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="border p-2">{new Date(record.check_date).toLocaleString('ja-JP')}</td>
                        <td className="border p-2">
                          <span className={record.is_available ? 'text-green-600' : 'text-red-600'}>
                            {record.is_available ? '利用可能' : '利用不可'}
                          </span>
                        </td>
                        <td className="border p-2">{record.status_code || '-'}</td>
                        <td className="border p-2">{record.response_time_ms ? `${record.response_time_ms}ms` : '-'}</td>
                        <td className="border p-2">{record.error_message || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {diseaseStatus && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2 text-left">団体名</th>
                <th className="border p-2 text-left">URL</th>
                <th className="border p-2 text-center">状態</th>
                <th className="border p-2 text-center">最終チェック</th>
                <th className="border p-2 text-center">アクション</th>
              </tr>
            </thead>
            <tbody>
              {diseaseStatus.organizations.map((org) => (
                <tr key={org.url} className="hover:bg-gray-50">
                  <td className="border p-2">{org.name}</td>
                  <td className="border p-2">
                    <a 
                      href={org.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {org.url.length > 50 ? org.url.substring(0, 50) + '...' : org.url}
                    </a>
                  </td>
                  <td className="border p-2 text-center">
                    <span className={org.is_available ? 'text-green-600' : 'text-red-600'}>
                      {org.is_available ? '利用可能' : '利用不可'}
                    </span>
                  </td>
                  <td className="border p-2 text-center">
                    {org.last_checked ? new Date(org.last_checked).toLocaleString('ja-JP') : '未チェック'}
                  </td>
                  <td className="border p-2 text-center">
                    <button
                      className="text-blue-600 hover:underline"
                      onClick={() => handleViewHistory(org.url)}
                    >
                      履歴を表示
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {allStatus && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2 text-left">疾患名</th>
                <th className="border p-2 text-center">団体数</th>
                <th className="border p-2 text-center">利用可能</th>
                <th className="border p-2 text-center">利用不可</th>
                <th className="border p-2 text-center">可用率</th>
              </tr>
            </thead>
            <tbody>
              {allStatus.disease_summary.map((summary) => (
                <tr key={summary.disease_id} className="hover:bg-gray-50">
                  <td className="border p-2">{summary.disease_name}</td>
                  <td className="border p-2 text-center">{summary.total_organizations}</td>
                  <td className="border p-2 text-center">{summary.available_count}</td>
                  <td className="border p-2 text-center">{summary.unavailable_count}</td>
                  <td className="border p-2 text-center">
                    {summary.total_organizations > 0
                      ? `${((summary.available_count / summary.total_organizations) * 100).toFixed(1)}%`
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
