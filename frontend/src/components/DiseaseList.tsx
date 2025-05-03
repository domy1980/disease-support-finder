import { useEffect, useState } from 'react';
import { DiseaseInfo, DiseaseListResponse } from '../types';
import { fetchAllDiseases } from '../services/api';
import { DiseaseCard } from './DiseaseCard';

interface DiseaseListProps {
  onSelectDisease: (diseaseId: string) => void;
}

export const DiseaseList = ({ onSelectDisease }: DiseaseListProps) => {
  const [diseaseList, setDiseaseList] = useState<DiseaseListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'intractable' | 'childhood'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const loadDiseases = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAllDiseases();
        setDiseaseList(data);
      } catch (err) {
        setError('疾患リストの取得中にエラーが発生しました。');
        console.error('Error loading diseases:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadDiseases();
  }, []);

  const filteredDiseases = (): DiseaseInfo[] => {
    if (!diseaseList) return [];

    let filtered = diseaseList.results;

    if (filter === 'intractable') {
      filtered = filtered.filter(disease => disease.is_intractable);
    } else if (filter === 'childhood') {
      filtered = filtered.filter(disease => disease.is_childhood_chronic);
    }

    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(disease => 
        disease.name_ja.toLowerCase().includes(term) || 
        disease.name_en?.toLowerCase().includes(term) ||
        disease.synonyms_ja?.some(syn => syn.toLowerCase().includes(term)) ||
        disease.synonyms_en?.some(syn => syn.toLowerCase().includes(term))
      );
    }

    return filtered;
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

  const diseases = filteredDiseases();

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">全疾患リスト</h2>
          {diseaseList && (
            <p className="text-muted-foreground">
              全 {diseaseList.total} 件（指定難病: {diseaseList.intractable_count} 件、小児慢性特定疾病: {diseaseList.childhood_chronic_count} 件）
            </p>
          )}
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <input
            type="text"
            placeholder="疾患名で絞り込み"
            className="px-3 py-2 border rounded-md"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          
          <select
            className="px-3 py-2 border rounded-md"
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'intractable' | 'childhood')}
          >
            <option value="all">すべての疾患</option>
            <option value="intractable">指定難病のみ</option>
            <option value="childhood">小児慢性特定疾病のみ</option>
          </select>
        </div>
      </div>

      {diseases.length === 0 ? (
        <div className="text-center p-8 border rounded-lg bg-muted/50">
          <p>条件に一致する疾患が見つかりませんでした。</p>
        </div>
      ) : (
        <div>
          <p className="mb-4">表示: {diseases.length} 件</p>
          <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {diseases.map((disease) => (
              <DiseaseCard
                key={disease.disease_id}
                disease={disease}
                onClick={onSelectDisease}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
