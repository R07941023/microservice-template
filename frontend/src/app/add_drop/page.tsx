"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DropData } from '@/hooks/useSearchData';
import DropForm from '@/components/DropForm';
import GoBackButton from '@/components/GoBackButton';
import { useAuth } from '@/context/AuthContext';

export default function AddDropPage() {
  const router = useRouter();
  const { token} = useAuth(); // Get the token from AuthContext
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

    if (!token) {
      setMessage("Error: You must be logged in to add an item.");
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await fetch('/api/add_drop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // Add Authorization header
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
        router.push(`/?query=${formData.dropperid}`);
      }, 1500);

    } catch (err: unknown) {
      setMessage(err instanceof Error ? `Error: ${err.message}`: "Unknown error occurred");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-4">
      <GoBackButton />
      <div className="bg-white rounded-lg shadow-md max-w-lg mx-auto mt-8">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Add New Drop Record</h2>
        <DropForm
          formData={formData}
          onFormChange={handleChange}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          submitButtonText="Add Item"
          message={message}
        />
      </div>
    </div>
  );
}
