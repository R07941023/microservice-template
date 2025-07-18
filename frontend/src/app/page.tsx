"use client";

import { useState } from 'react';
import ItemCard from '../components/ItemCard';
import ItemDetail from '../components/ItemDetail';

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

  const handleSearch = async () => {
    if (!searchTerm) return;

    setLoading(true);
    setError(null);
    setSearchResults([]);
    setSelectedItem(null);

    try {
      const response = await fetch(`/api/search_drops?query=${searchTerm}`);
      console.log(response)
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

  const handleItemClick = (item: DropData) => {
    setSelectedItem(item);
  };

  return (
    <div className="p-4">
      <div className="flex mb-4">
        <input
          type="text"
          placeholder="Search by Dropper ID or Item ID..."
          className="flex-grow p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          onClick={handleSearch}
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {error && <p className="text-red-500 text-center mb-4">Error: {error}</p>}
      {loading && <p className="text-center text-gray-500">Loading...</p>}

      {selectedItem ? (
        <ItemDetail item={selectedItem} onBack={() => setSelectedItem(null)} />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {searchResults.map((item) => (
            <ItemCard key={item.id} item={item} onClick={handleItemClick} />
          ))}
        </div>
      )}

      {!loading && !error && searchResults.length === 0 && searchTerm && (
        <p className="text-center text-gray-500">No results found for &quot;{searchTerm}&quot;.</p>
      )}
      {!loading && !error && searchResults.length === 0 && !searchTerm && (
        <p className="text-center text-gray-500">Enter a Dropper ID or Item ID to search for MapleStory drops.</p>
      )}
    </div>
  );
}
