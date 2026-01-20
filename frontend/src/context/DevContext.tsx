'use client';

import { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface DevContextType {
  devMode: boolean;
  toggleDevMode: () => void;
}

const DevContext = createContext<DevContextType | undefined>(undefined);

export const DevProvider = ({ children }: { children: ReactNode }) => {
  const [devMode, setDevMode] = useState<boolean>(() => {
    // Initialize from localStorage or default to false
    if (typeof window !== 'undefined') {
      const storedDevMode = localStorage.getItem('devMode');
      return storedDevMode ? JSON.parse(storedDevMode) : false;
    }
    return false;
  });

  useEffect(() => {
    // Persist devMode to localStorage whenever it changes
    if (typeof window !== 'undefined') {
      localStorage.setItem('devMode', JSON.stringify(devMode));
    }
  }, [devMode]);

  const toggleDevMode = () => {
    setDevMode(prevMode => !prevMode);
  };

  return (
    <DevContext.Provider value={{ devMode, toggleDevMode }}>
      {children}
    </DevContext.Provider>
  );
};

export const useDevMode = () => {
  const context = useContext(DevContext);
  if (context === undefined) {
    throw new Error('useDevMode must be used within a DevProvider');
  }
  return context;
};
