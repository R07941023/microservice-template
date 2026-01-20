import React from 'react';
import ItemCard from './ItemCard';
import { DropData, AggregatedExistenceInfo } from '@/hooks/useSearchData';
import { FaCheck, FaTimes } from 'react-icons/fa'; // Import icons

interface ResultsComponentProps {
  loading: boolean;
  error: string | null;
  searchResults: DropData[];
  searchTerm: string;
  handleItemClick: (item: DropData) => void;
  alternativeIds?: AggregatedExistenceInfo[];
}

const ResultsComponent: React.FC<ResultsComponentProps> = ({
  loading,
  error,
  searchResults,
  searchTerm,
  handleItemClick,
  alternativeIds,
}) => {
  if (error) {
    return <p className="text-red-500 text-center mb-4">Error: {error}</p>;
  }

  if (loading) {
    return <p className="text-center text-gray-500">Loading...</p>;
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
    if (alternativeIds && alternativeIds.length > 0) {
      return (
        <div className="text-center text-gray-500">
          <p>No results found for &quot;{searchTerm}&quot;.</p>
          <p className="mt-2 mb-4">However, the following entries are associated with this name:</p>
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto bg-white border border-gray-300 rounded-lg shadow-sm mx-auto">
              <thead>
                <tr className="bg-gray-100 text-gray-700">
                  <th className="py-2 px-4 border-b text-left">Type</th>
                  <th className="py-2 px-4 border-b text-center">ID</th>
                  <th className="py-2 px-4 border-b text-center">Image Exists</th>
                  <th className="py-2 px-4 border-b text-center">Drop Exists</th>
                </tr>
              </thead>
              <tbody>
                {alternativeIds.map((entry, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="py-2 px-4 border-b text-left">{entry.type}</td>
                    <td className="py-2 px-4 border-b text-center">{entry.id}</td>
                    <td className="py-2 px-4 border-b text-center">
                      {entry.image_exist ? (
                        <FaCheck className="text-green-500 mx-auto text-lg" />
                      ) : (
                        <FaTimes className="text-red-500 mx-auto text-lg" />
                      )}
                    </td>
                    <td className="py-2 px-4 border-b text-center">
                      {entry.drop_exist ? (
                        <FaCheck className="text-green-500 mx-auto text-lg" />
                      ) : (
                        <FaTimes className="text-red-500 mx-auto text-lg" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }
    return <p className="text-center text-gray-500">No results found for &quot;{searchTerm}&quot;.</p>;
  }

  return <p className="text-center text-gray-500">Enter a Dropper ID or Item ID to search for MapleStory drops.</p>;
};

export default ResultsComponent;

