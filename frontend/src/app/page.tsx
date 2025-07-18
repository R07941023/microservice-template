"use client";

import { useState, useEffect } from 'react';
import SearchComponent from '@/components/SearchComponent';
import ResultsComponent from '@/components/ResultsComponent';

interface DropData {
  id: string;
  dropperid: number;
  itemid: number;
  minimum_quantity: number;
  maximum_quantity: number;
  questid: number;
  chance: number;
}

export default function Home() {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<DropData[]>([]);
  const [selectedItem, setSelectedItem] = useState<DropData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);

  // Load search history from localStorage on initial render
  useEffect(() => {
    try {
      const storedHistory = localStorage.getItem('searchHistory');
      if (storedHistory) {
        setSearchHistory(JSON.parse(storedHistory));
      }
    } catch (error) {
      console.error("Failed to parse search history from localStorage", error);
      setSearchHistory([]);
    }
  }, []);

  // Save search history to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    } catch (error) {
      console.error("Failed to save search history to localStorage", error);
    }
  }, [searchHistory]);

  const handleSearch = async (query?: string) => {
    const termToSearch = query || searchTerm;
    if (!termToSearch) return;

    setLoading(true);
    setError(null);
    setSearchResults([]);
    setSelectedItem(null);

    // Add to history if it's a new term
    if (!searchHistory.includes(termToSearch)) {
      setSearchHistory([termToSearch, ...searchHistory].slice(0, 10)); // Keep last 10 searches
    }

    try {
      const response = await fetch(`/api/search_drops?query=${termToSearch}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch data');
      }
      const data: DropData[] = await response.json();
      setSearchResults(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (term: string) => {
    setSearchTerm(term);
    handleSearch(term);
  };

  const handleDeleteHistory = (e: React.MouseEvent, termToDelete: string) => {
    e.stopPropagation(); // Prevent the history click from firing
    setSearchHistory(searchHistory.filter(term => term !== termToDelete));
  };

  const handleItemClick = (item: DropData) => {
    setSelectedItem(item);
  };

  const handleBack = () => {
    setSelectedItem(null);
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
        selectedItem={selectedItem}
        searchTerm={searchTerm}
        handleItemClick={handleItemClick}
        handleBack={handleBack}
      />
    </div>
  );
}
