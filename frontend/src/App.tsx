import { useState, useEffect } from 'react';
import './App.css';
import { SearchBar } from './components/SearchBar';
import { DiseaseCard } from './components/DiseaseCard';
import { DiseaseDetail } from './components/DiseaseDetail';
import { DiseaseList } from './components/DiseaseList';
import { StatsDisplay } from './components/StatsDisplay';
import { WebsiteStatusTracker } from './components/WebsiteStatusTracker';
import { ManualEntryForm } from './components/ManualEntryForm';
import { LLMSearchControls } from './components/LLMSearchControls';
import { LLMInfoPanel } from './components/LLMInfoPanel';
import { EnhancedLLMSearchControls } from './components/LLMSearchControls_enhanced';
import { DiseaseWithOrganizations, SearchResponse, OrganizationCollection } from './types';
import { searchDiseases, fetchDiseaseWithOrganizations, fetchOrganizationCollection } from './services/api';

type View = 'search' | 'list' | 'stats' | 'websites' | 'llm' | 'detail';

function App() {
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedDisease, setSelectedDisease] = useState<DiseaseWithOrganizations | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<View>('search');
  const [orgCollection, setOrgCollection] = useState<OrganizationCollection | null>(null);
  const [showManualEntry, setShowManualEntry] = useState(false);

  useEffect(() => {
    setError(null);
  }, [currentView]);

  const handleSearch = async (query: string, includeSynonyms: boolean) => {
    try {
      setIsSearching(true);
      setError(null);
      setSelectedDisease(null);
      
      const results = await searchDiseases({
        query,
        include_synonyms: includeSynonyms
      });
      
      setSearchResults(results);
      setCurrentView('search');
    } catch (err) {
      setError('検索中にエラーが発生しました。もう一度お試しください。');
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleDiseaseSelect = async (diseaseId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const diseaseWithOrgs = await fetchDiseaseWithOrganizations(diseaseId);
      setSelectedDisease(diseaseWithOrgs);
      
      try {
        const collection = await fetchOrganizationCollection(diseaseId);
        setOrgCollection(collection);
      } catch (err) {
        console.error('Error fetching organization collection:', err);
      }
      
      setCurrentView('detail');
    } catch (err) {
      setError('疾患情報の取得中にエラーが発生しました。もう一度お試しください。');
      console.error('Disease detail error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToResults = () => {
    setSelectedDisease(null);
    setOrgCollection(null);
    setShowManualEntry(false);
    
    if (searchResults) {
      setCurrentView('search');
    } else {
      setCurrentView('list');
    }
  };

  const handleManualEntryAdded = async () => {
    if (selectedDisease) {
      try {
        const collection = await fetchOrganizationCollection(selectedDisease.disease.disease_id);
        setOrgCollection(collection);
      } catch (err) {
        console.error('Error refreshing organization collection:', err);
      }
    }
  };

  const renderContent = () => {
    if (currentView === 'detail' && selectedDisease) {
      return (
        <div className="w-full max-w-4xl mx-auto">
          <DiseaseDetail
            diseaseWithOrgs={selectedDisease}
            onBack={handleBackToResults}
            isLoading={isLoading}
          />
          
          {showManualEntry ? (
            <div className="mt-8">
              <ManualEntryForm
                diseaseId={selectedDisease.disease.disease_id}
                diseaseName={selectedDisease.disease.name_ja}
                onEntryAdded={handleManualEntryAdded}
              />
            </div>
          ) : (
            <div className="mt-4 text-center">
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                onClick={() => setShowManualEntry(true)}
              >
                情報を追加する
              </button>
            </div>
          )}
          
          {selectedDisease && (
            <div className="mt-8">
              <WebsiteStatusTracker
                diseaseId={selectedDisease.disease.disease_id}
                diseaseName={selectedDisease.disease.name_ja}
                organizationData={orgCollection}
              />
            </div>
          )}
        </div>
      );
    }
    
    if (currentView === 'search') {
      return (
        <div className="flex flex-col items-center space-y-8">
          <div className="space-y-2 text-center">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              難病・希少疾患の支援団体を検索
            </h1>
            <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
              指定難病や小児慢性特定疾病の患者会、家族会、支援団体を検索できます。
            </p>
          </div>
          
          <div className="w-full max-w-3xl">
            <SearchBar onSearch={handleSearch} isLoading={isSearching} />
          </div>
          
          {error && (
            <div className="w-full max-w-3xl p-4 border border-red-200 bg-red-50 text-red-700 rounded-md">
              {error}
            </div>
          )}
          
          {searchResults && (
            <div className="w-full max-w-4xl">
              <h2 className="text-xl font-semibold mb-4">
                検索結果: {searchResults.total}件
              </h2>
              
              {searchResults.total === 0 ? (
                <div className="text-center p-8 border rounded-lg bg-muted/50">
                  <p>該当する疾患が見つかりませんでした。</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    別の病名や表記で検索してみてください。
                  </p>
                </div>
              ) : (
                <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                  {searchResults.results.map((result) => (
                    <DiseaseCard
                      key={result.disease.disease_id}
                      disease={result.disease}
                      onClick={handleDiseaseSelect}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      );
    }
    
    if (currentView === 'list') {
      return <DiseaseList onSelectDisease={handleDiseaseSelect} />;
    }
    
    if (currentView === 'stats') {
      return <StatsDisplay />;
    }
    
    if (currentView === 'websites') {
      return <WebsiteStatusTracker />;
    }
    
    if (currentView === 'llm') {
      return (
        <div className="space-y-8">
          <EnhancedLLMSearchControls />
          <LLMInfoPanel />
        </div>
      );
    }
    
    return null;
  };

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          <div className="mr-4 flex">
            <a className="mr-6 flex items-center space-x-2" href="/">
              <span className="font-bold text-xl">
                難病・希少疾患支援団体検索
              </span>
            </a>
          </div>
          
          <nav className="flex items-center space-x-4 lg:space-x-6">
            <button
              onClick={() => setCurrentView('search')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                currentView === 'search' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              検索
            </button>
            <button
              onClick={() => setCurrentView('list')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                currentView === 'list' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              全疾患リスト
            </button>
            <button
              onClick={() => setCurrentView('stats')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                currentView === 'stats' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              統計情報
            </button>
            <button
              onClick={() => setCurrentView('websites')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                currentView === 'websites' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              ウェブサイト状態
            </button>
            <button
              onClick={() => setCurrentView('llm')}
              className={`text-sm font-medium transition-colors hover:text-primary ${
                currentView === 'llm' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              LLM検索
            </button>
          </nav>
        </div>
      </header>
      
      <main className="flex-1">
        <section className="w-full py-8 md:py-12">
          <div className="container px-4 md:px-6">
            {renderContent()}
          </div>
        </section>
      </main>
      
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} 難病・希少疾患支援団体検索
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
