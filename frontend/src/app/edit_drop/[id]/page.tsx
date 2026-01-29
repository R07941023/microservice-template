"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ItemDetail from '@/components/ItemDetail';
import { DropData } from '@/hooks/useSearchData';
import GoBackButton from '@/components/GoBackButton';
import { useAuth } from '@/context/AuthContext';

export default function EditDropPage() {
  const params = useParams();
  const router = useRouter();
  const { id } = params;
  const [item, setItem] = useState<DropData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    if (id && token) {
      const fetchItem = async () => {
        try {
          const response = await fetch(`/api/get_drop/${Array.isArray(id) ? id[0] : id}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          if (!response.ok) {
            throw new Error('Failed to fetch item data');
          }
          const data: DropData = await response.json();
          setItem(data);
        } catch (err: unknown) {
          setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
          setLoading(false);
        }
      };
      fetchItem();
    }
  }, [id, token]);

  if (loading) {
    return <div className="p-4 text-center">Loading item details...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">Error: {error}</div>;
  }

  if (!item) {
    return <div className="p-4 text-center">Item not found.</div>;
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      const response = await fetch(`/api/delete_drop/${item.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete item');
      }

      alert('Item deleted successfully!');
      router.push('/'); // Redirect to home page after successful deletion
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
      alert(`Error deleting item: ${errorMessage}`);
    }
  };

  return (
    <div className="p-4">
      <GoBackButton />
      <ItemDetail item={item} onDelete={handleDelete} />
    </div>
  );
}
