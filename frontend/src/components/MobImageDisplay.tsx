import React, { useState } from 'react';
import Image from 'next/image';
import { AiOutlineWarning } from 'react-icons/ai';

interface MobImageDisplayProps {
  dropperid: number;
  dropper_name: string;
}

const MobImageDisplay: React.FC<MobImageDisplayProps> = ({ dropperid, dropper_name }) => {
  const [hasError, setHasError] = useState(false);

  if (dropperid === 0) {
    return (
      <div className="w-16 h-16 flex items-center justify-center text-xs text-gray-500 text-center leading-tight">
        No Mob ID
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
      src={`/api/images/mob/${dropperid}`}
      alt={`Mob: ${dropper_name}`}
      width={64}
      height={64}
      unoptimized
      onError={() => setHasError(true)}
      style={{ objectFit: 'contain' }}
    />
  );
};

export default MobImageDisplay;
