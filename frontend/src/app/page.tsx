"use client";

import { useRouter } from 'next/navigation';
import SearchComponent from '@/components/SearchComponent';
import ResultsComponent from '@/components/ResultsComponent';
import { useSearchData, DropData } from '@/hooks/useSearchData';

export default function Home() {
  const {
    searchTerm,
    setSearchTerm,
    searchResults,
    loading,
    error,
    searchHistory,
    handleSearch,
    handleDeleteHistory,
  } = useSearchData();

  const router = useRouter();

  const handleHistoryClick = (term: string) => {
    setSearchTerm(term);
    handleSearch(term);
  };

  const handleItemClick = (item: DropData) => {
    router.push(`/edit_drop/${item.id}`);
  };

  return (
    <div className="p-4">
      <SearchComponent
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        handleSearch={() => handleSearch()}
        loading={loading}
        searchHistory={searchHistory}
        handleHistoryClick={handleHistoryClick}
        handleDeleteHistory={handleDeleteHistory}
      />
      <ResultsComponent
        loading={loading}
        error={error}
        searchResults={searchResults}
        searchTerm={searchTerm}
        handleItemClick={handleItemClick}
      />
    </div>
  );
}