'use client';

import { useRouter } from 'next/navigation';

import SearchComponent from '@/components/SearchComponent';
import ResultsComponent from '@/components/ResultsComponent';
import { useSearchData, DropData } from '@/hooks/useSearchData';
import ChatComponent from '@/components/ChatComponent';


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
        handleSearch={handleSearch}
        loading={loading}
        searchHistory={searchHistory}
        handleHistoryClick={handleHistoryClick}
        handleDeleteHistory={handleDeleteHistory}
        disabled={false} // Disable search if no token
      />
      <div className="flex justify-end my-4">
        <button
          onClick={() => router.push('/add_drop')}
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          disabled={false} // Disable add button if no token
        >
          Add New Item
        </button>
      </div>
      <ResultsComponent
        loading={loading}
        error={error}
        searchResults={searchResults}
        searchTerm={searchTerm}
        handleItemClick={handleItemClick}
      />
      <ChatComponent />
    </div>
  );
}