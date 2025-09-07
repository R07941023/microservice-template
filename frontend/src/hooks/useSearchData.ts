import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';

export interface DropData {
  id: string;
  dropperid: number;
  itemid: number;
  minimum_quantity: number;
  maximum_quantity: number;
  questid: number;
  chance: number;
  dropper_name: string;
  item_name: string;
}

export function useSearchData() {
  const { authFetch } = useAuth(); // Get the global authFetch function

  const [searchTerm, setSearchTerm] = useState(() => {
    if (typeof window !== 'undefined') {
      const storedTerm = localStorage.getItem('searchTerm');
      return storedTerm || '';
    }
    return '';
  });

  const [searchResults, setSearchResults] = useState<DropData[]>(() => {
    if (typeof window !== 'undefined') {
      const storedResults = localStorage.getItem('searchResults');
      return storedResults ? JSON.parse(storedResults) : [];
    }
    return [];
  });

  const [selectedItem, setSelectedItem] = useState<DropData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [searchHistory, setSearchHistory] = useState<string[]>(() => {
    if (typeof window !== 'undefined') {
      const storedHistory = localStorage.getItem('searchHistory');
      return storedHistory ? JSON.parse(storedHistory) : [];
    }
    return [];
  });

  // Save search history to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    } catch (error) {
      console.error("Failed to save search history to localStorage", error);
    }
  }, [searchHistory]);

  // Save search results to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('searchResults', JSON.stringify(searchResults));
    } catch (error) {
      console.error("Failed to save search results to localStorage", error);
    }
  }, [searchResults]);

  // Save search term to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('searchTerm', searchTerm);
    } catch (error) {
      console.error("Failed to save search term to localStorage", error);
    }
  }, [searchTerm]);

  const handleSearch = useCallback(async (query?: string) => {
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
      // Use the global authFetch
      const response = await authFetch(`/api/search_drops?query=${termToSearch}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch data');
      }
      const responseData = await response.json();
      const data: DropData[] = responseData.data; // Extract the array
      setSearchResults(data);
    } catch (err: unknown) {
      // The authFetch will throw an error on 401, which will be caught here.
      if (err instanceof Error && err.message.includes("Session expired")) {
        setError("Your session has expired. You are being redirected to login.");
      } else {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      }
    } finally {
      setLoading(false);
    }
  }, [searchTerm, authFetch, searchHistory, setSearchResults, setSelectedItem, setLoading, setError]);

  const initialSearchPerformed = useRef(false); // Use a ref to track if initial search happened

  useEffect(() => {
    if (!initialSearchPerformed.current && !searchTerm && searchResults.length === 0) {
      initialSearchPerformed.current = true; // Set flag to true
      handleSearch('朱礦石母礦'); // Automatically query
    }
  }, [searchTerm, searchResults, handleSearch]); // Dependencies

  const handleDeleteHistory = (e: React.MouseEvent, termToDelete: string) => {
    e.stopPropagation(); // Prevent the history click from firing
    setSearchHistory(searchHistory.filter(term => term !== termToDelete));
  };

  return {
    searchTerm,
    setSearchTerm,
    searchResults,
    setSearchResults,
    selectedItem,
    setSelectedItem,
    loading,
    error,
    searchHistory,
    handleSearch,
    handleDeleteHistory,
  };
}
