import React, { useState } from 'react';
import Image from 'next/image';
import { AiOutlineWarning } from 'react-icons/ai';

interface ItemImageDisplayProps {
  itemid: number;
  item_name: string;
}

const ItemImageDisplay: React.FC<ItemImageDisplayProps> = ({ itemid, item_name }) => {
  const [hasError, setHasError] = useState(false);

  if (itemid === 0) {
    return (
      <div className="w-16 h-16 flex items-center justify-center text-xs text-gray-500 text-center leading-tight">
        No Item ID
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="w-16 h-16 flex items-center justify-center border border-gray-200 rounded-md">
        <AiOutlineWarning size={32} color="gray" />
      </div>
    );
  }

  return (
    <Image
      src={`/api/images/item/${itemid}`}
      alt={`Item: ${item_name}`}
      width={64}
      height={64}
      unoptimized
      onError={() => setHasError(true)}
      style={{ objectFit: 'contain' }}
    />
  );
};

export default ItemImageDisplay;
