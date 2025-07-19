"use client";

import { useRouter } from 'next/navigation';
import SearchComponent from '@/components/SearchComponent';
import ResultsComponent from '@/components/ResultsComponent';
import { useSearchData, DropData } from '@/hooks/useSearchData';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const { token } = useAuth();
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

  const loginMessage = "Please log in to search for items.";

  return (
    <div className="p-4">
      {!token && <p className="text-red-500 text-center mb-4">{loginMessage}</p>}
      <SearchComponent
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        handleSearch={() => handleSearch()}
        loading={loading}
        searchHistory={searchHistory}
        handleHistoryClick={handleHistoryClick}
        handleDeleteHistory={handleDeleteHistory}
        disabled={!token} // Disable search if no token
      />
      <div className="flex justify-end my-4">
        <button
          onClick={() => router.push('/add_drop')}
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          disabled={!token} // Disable add button if no token
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
    </div>
  );
}