'use client';

import React from 'react';
import { useDevMode } from '@/context/DevContext';

const DevToggle: React.FC = () => {
  const { devMode, toggleDevMode } = useDevMode();

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <label className="inline-flex items-center cursor-pointer">
        <span className="relative">
          <input
            type="checkbox"
            className="sr-only"
            checked={devMode}
            onChange={toggleDevMode}
          />
          <div className={`block w-10 h-6 rounded-full ${devMode ? 'bg-blue-600' : 'bg-gray-600'}`}></div>
          <div className={`dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform ${devMode ? 'translate-x-full' : ''}`}></div>
        </span>
        <span className="ml-3 text-sm font-medium text-gray-900 dark:text-gray-300">Dev</span>
      </label>
    </div>
  );
};

export default DevToggle;
