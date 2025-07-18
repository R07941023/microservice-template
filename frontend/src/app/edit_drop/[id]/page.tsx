"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ItemDetail from '@/components/ItemDetail';

interface DropData {
  id: string;
  dropperid: number;
  itemid: number;
  minimum_quantity: number;
  maximum_quantity: number;
  questid: number;
  chance: number;
}

export default function EditDropPage() {
  const params = useParams();
  const router = useRouter();
  const { id } = params;
  const [item, setItem] = useState<DropData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      const fetchItem = async () => {
        try {
          const response = await fetch(`/api/get_drop/${Array.isArray(id) ? id[0] : id}`);
          if (!response.ok) {
            throw new Error('Failed to fetch item data');
          }
          const data: DropData = await response.json();
          setItem(data);
        } catch (err: any) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      };
      fetchItem();
    }
  }, [id]);

  if (loading) {
    return <div className="p-4 text-center">Loading item details...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">Error: {error}</div>;
  }

  if (!item) {
    return <div className="p-4 text-center">Item not found.</div>;
  }

  return (
    <div className="p-4">
      <ItemDetail item={item} />
    </div>
  );
}
