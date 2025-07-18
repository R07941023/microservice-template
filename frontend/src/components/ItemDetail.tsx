import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DropData } from '@/hooks/useSearchData';

interface ItemDetailProps {
  item: DropData;
  onDelete: () => void;
}

const ItemDetail: React.FC<ItemDetailProps> = ({ item, onDelete }) => {
  const router = useRouter();
  const [editableItem, setEditableItem] = useState<DropData>(item);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setEditableItem(item);
  }, [item]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEditableItem(prev => ({ ...prev, [name]: Number(value) }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);
    try {
      const response = await fetch(`/api/update_drop/${item.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editableItem),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save data');
      }

      setMessage("Successfully updated!");
      setTimeout(() => {
        setMessage(null);
        router.push('/'); // Navigate back to the home page
        router.refresh(); // Force a refresh to re-fetch data and re-run effects
      }, 1500); // Hide message and navigate after 1.5 seconds

    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setMessage(`Error: ${errorMessage}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md max-w-lg mx-auto">
      
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Editing Drop Record ID: {item.id}</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Dropper ID</label>
          <input type="number" name="dropperid" value={editableItem.dropperid} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Item ID</label>
          <input type="number" name="itemid" value={editableItem.itemid} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Chance</label>
          <input type="number" name="chance" value={editableItem.chance} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Minimum Quantity</label>
          <input type="number" name="minimum_quantity" value={editableItem.minimum_quantity} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Maximum Quantity</label>
          <input type="number" name="maximum_quantity" value={editableItem.maximum_quantity} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Quest ID</label>
          <input type="number" name="questid" value={editableItem.questid} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" />
        </div>
      </div>

      <div className="mt-6 flex items-center justify-between">
        <button 
          onClick={handleSave}
          disabled={isSaving}
          className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
        <button
          onClick={onDelete}
          className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        >
          Delete Item
        </button>
        {message && <p className={`ml-4 text-sm ${message.startsWith('Error') ? 'text-red-500' : 'text-green-500'}`}>{message}</p>}
      </div>
    </div>
  );
};

export default ItemDetail;
