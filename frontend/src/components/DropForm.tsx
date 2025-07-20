import React from 'react';
import { DropData } from '@/hooks/useSearchData';

interface DropFormProps {
  formData: Omit<DropData, 'id'> & { id?: string };
  onFormChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
  isSubmitting: boolean;
  submitButtonText: string;
  message: string | null;
  rightSideContent?: React.ReactNode;
}

const DropForm: React.FC<DropFormProps> = ({
  formData,
  onFormChange,
  onSubmit,
  isSubmitting,
  submitButtonText,
  message,
  rightSideContent,
}) => {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Dropper ID</label>
        <input type="number" name="dropperid" value={formData.dropperid} onChange={onFormChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Item ID</label>
        <input type="number" name="itemid" value={formData.itemid} onChange={onFormChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Chance</label>
        <input type="number" name="chance" value={formData.chance} onChange={onFormChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Minimum Quantity</label>
        <input type="number" name="minimum_quantity" value={formData.minimum_quantity} onChange={onFormChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Maximum Quantity</label>
        <input type="number" name="maximum_quantity" value={formData.maximum_quantity} onChange={onFormChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Quest ID</label>
        <input type="number" name="questid" value={formData.questid} onChange={onFormChange} className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black" required />
      </div>
      
      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center">
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
          >
            {submitButtonText}
          </button>
          {message && <p className={`ml-4 text-sm ${message.startsWith('Error') ? 'text-red-500' : 'text-green-500'}`}>{message}</p>}
        </div>
        {rightSideContent}
      </div>
    </form>
  );
};

export default DropForm;
