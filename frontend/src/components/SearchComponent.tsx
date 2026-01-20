"use client";

import React, { useState, useRef } from 'react';
import { useClickOutside } from '@/hooks/useClickOutside';
import { useAutocompleteNames } from '@/hooks/useAutocompleteNames';

const DeleteIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

interface SearchComponentProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  handleSearch: (term?: string) => void;
  loading: boolean;
  searchHistory: string[];
  handleHistoryClick: (term: string) => void;
  handleDeleteHistory: (e: React.MouseEvent, term: string) => void;
  disabled?: boolean;
}

const SearchComponent: React.FC<SearchComponentProps> = ({
  searchTerm,
  setSearchTerm,
  handleSearch,
  loading,
  searchHistory,
  handleHistoryClick,
  handleDeleteHistory,
  disabled = false,
}) => {
  const allNames = useAutocompleteNames();
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isInputFocused, setIsInputFocused] = useState(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  useClickOutside(searchContainerRef, () => setIsInputFocused(false));

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    if (value) {
      const filteredSuggestions = allNames
        .filter(name => name.toLowerCase().includes(value.toLowerCase()))
        .slice(0, 10);
      setSuggestions(filteredSuggestions);
    } else {
      setSuggestions([]);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setSearchTerm(suggestion);
    handleSearch(suggestion); // Trigger search immediately
    setSuggestions([]);
    setIsInputFocused(false);
  };

  return (
    <div ref={searchContainerRef}>
      <div className="flex mb-1 relative">
        <input
          type="text"
          placeholder="Search by Dropper ID or Item ID..."
          className="flex-grow p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black disabled:bg-gray-100 disabled:cursor-not-allowed"
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={() => setIsInputFocused(true)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSearch();
              setIsInputFocused(false);
            }
          }}
          disabled={disabled}
        />
        {isInputFocused && suggestions.length > 0 && (
          <ul className="absolute top-full left-0 right-0 z-10 bg-white border border-gray-300 rounded-b-md shadow-lg max-h-60 overflow-y-auto">
            {suggestions.map((suggestion, index) => (
              <li
                key={index}
                className="p-2 cursor-pointer hover:bg-gray-100 text-black"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </li>
            ))}
          </ul>
        )}
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          onClick={() => handleSearch()}
          disabled={loading || disabled}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {searchHistory.length > 0 && (
        <div className="mb-4 flex items-center flex-wrap">
          <span className="text-sm text-gray-500 mr-2">Recent:</span>
          {searchHistory.map((term, index) => (
            <div
              key={index}
              className="flex items-center bg-gray-200 rounded-full mr-2 mb-1 cursor-pointer hover:bg-gray-300 group"
              onClick={() => handleHistoryClick(term)}
            >
              <span className="text-sm text-gray-700 pl-3 pr-2 py-1">
                {term}
              </span>
              <button
                className="text-gray-500 hover:text-red-500 opacity-50 group-hover:opacity-100 p-1 rounded-full"
                onClick={(e) => handleDeleteHistory(e, term)}
                aria-label={`Remove ${term} from history`}
              >
                <DeleteIcon />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchComponent;

