import { useState, useEffect } from 'react';

export function useAutocompleteNames() {
  const [allNames, setAllNames] = useState<string[]>([]);

  useEffect(() => {
    const fetchAllNames = async () => {
      try {
        const response = await fetch('/api/names/all');
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
  }, []);

  return allNames;
}
