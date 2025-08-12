"use client";

import { useRouter } from 'next/navigation';
import React from 'react';

const GoBackButton: React.FC = () => {
  const router = useRouter();

  return (
    <button
      onClick={() => router.back()}
      className="mb-4 px-4 py-2 bg-transparent text-blue-600 rounded-md hover:bg-blue-50 hover:text-blue-800"
    >
      &larr; Go Back
    </button>
  );
};

export default GoBackButton;
