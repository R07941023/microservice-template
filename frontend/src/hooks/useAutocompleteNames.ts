import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';

export function useAutocompleteNames() {
  const [allNames, setAllNames] = useState<string[]>([]);
  const { authFetch, authenticated } = useAuth();

  useEffect(() => {
    if (!authenticated) return;

    const fetchAllNames = async () => {
      try {
        const response = await authFetch('/api/names/all');
        if (response.ok) {
          const data = await response.json();
          setAllNames(data.names || []);
        } else {
          console.error("Failed to fetch all names");
        }
      } catch (error) {
        console.error("Error fetching all names:", error);
      }
    };
    fetchAllNames();
  }, [authFetch, authenticated]);

  return allNames;
}
