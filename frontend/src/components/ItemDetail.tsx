import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DropData } from '@/hooks/useSearchData';
import DropForm from './DropForm';

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

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevent default form submission
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
      
      <DropForm
        formData={editableItem}
        onFormChange={handleChange}
        onSubmit={handleSave}
        isSubmitting={isSaving}
        submitButtonText="Save Changes"
        message={message}
        rightSideContent={(
          <button
            onClick={onDelete}
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            Delete Item
          </button>
        )}
      />
    </div>
  );
};

export default ItemDetail;
