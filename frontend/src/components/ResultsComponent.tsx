"use client";

import React from 'react';
import ItemCard from './ItemCard';
import ItemDetail from './ItemDetail';

interface DropData {
  id: string;
  dropperid: number;
  itemid: number;
  minimum_quantity: number;
  maximum_quantity: number;
  questid: number;
  chance: number;
}

interface ResultsComponentProps {
  loading: boolean;
  error: string | null;
  searchResults: DropData[];
  selectedItem: DropData | null;
  searchTerm: string;
  handleItemClick: (item: DropData) => void;
  handleBack: () => void;
}

const ResultsComponent: React.FC<ResultsComponentProps> = ({
  loading,
  error,
  searchResults,
  selectedItem,
  searchTerm,
  handleItemClick,
  handleBack,
}) => {
  if (error) {
    return <p className="text-red-500 text-center mb-4">Error: {error}</p>;
  }

  if (loading) {
    return <p className="text-center text-gray-500">Loading...</p>;
  }

  if (selectedItem) {
    return <ItemDetail item={selectedItem} onBack={handleBack} />;
  }

  if (searchResults.length > 0) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {searchResults.map((item) => (
          <ItemCard key={item.id} item={item} onClick={handleItemClick} />
        ))}
      </div>
    );
  }

  if (searchTerm) {
    return <p className="text-center text-gray-500">No results found for &quot;{searchTerm}&quot;.</p>;
  }

  return <p className="text-center text-gray-500">Enter a Dropper ID or Item ID to search for MapleStory drops.</p>;
};

export default ResultsComponent;
