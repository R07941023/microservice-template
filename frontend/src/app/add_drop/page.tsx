"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DropData } from '@/hooks/useSearchData';

export default function AddDropPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<Omit<DropData, 'id'> & { id?: string }>({ // id is optional for new items
    dropperid: 0,
    itemid: 0,
    minimum_quantity: 0,
    maximum_quantity: 0,
    questid: 0,
    chance: 0,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: Number(value) }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage(null);

    try {
      const response = await fetch('/api/add_drop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add new item');
      }

      setMessage("Item added successfully!");
      setFormData({
        dropperid: 0,
        itemid: 0,
        minimum_quantity: 0,
        maximum_quantity: 0,
        questid: 0,
        chance: 0,
      }); // Clear form
      setTimeout(() => {
        setMessage(null);
        router.push('/'); // Navigate back to home page
        router.refresh(); // Force a refresh to re-fetch data
      }, 1500);

    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md max-w-lg mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Add New Drop Record</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Dropper ID</label>
          <input type="number" name="dropperid" value={formData.dropperid} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Item ID</label>
          <input type="number" name="itemid" value={formData.itemid} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Chance</label>
          <input type="number" name="chance" value={formData.chance} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Minimum Quantity</label>
          <input type="number" name="minimum_quantity" value={formData.minimum_quantity} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Maximum Quantity</label>
          <input type="number" name="maximum_quantity" value={formData.maximum_quantity} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Quest ID</label>
          <input type="number" name="questid" value={formData.questid} onChange={handleChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
        </div>
        
        <div className="mt-6 flex items-center justify-between">
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
          >
            {isSubmitting ? 'Adding...' : 'Add Item'}
          </button>
          {message && <p className={`ml-4 text-sm ${message.startsWith('Error') ? 'text-red-500' : 'text-green-500'}`}>{message}</p>}
        </div>
      </form>
    </div>
  );
}
