import MobImageDisplay from './MobImageDisplay';
import ItemImageDisplay from './ItemImageDisplay';
interface DropData {
  id: string;
  dropperid: number;
  dropper_name: string,
  itemid: number;
  item_name: string,
  minimum_quantity: number;
  maximum_quantity: number;
  questid: number;
  chance: number;
}

interface ItemCardProps {
  item: DropData;
  onClick: (item: DropData) => void;
}

export default function ItemCard({ item, onClick }: ItemCardProps) {
  

  return (
    <div
      className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-lg transition-shadow bg-white text-black"
      onClick={() => onClick(item)}
    >
      <div className="flex justify-center items-start space-x-4 mb-2">
        <div className="flex flex-col items-center w-24 flex-shrink-0 flex-grow"> {/* Mob container with fixed width, prevent shrinking, allow growing */}
          <div className="w-16 h-16 flex items-center justify-center border border-gray-200 rounded-md mb-1 flex-shrink-0"> {/* Fixed size image wrapper, prevent shrinking */}
            <MobImageDisplay dropperid={item.dropperid} dropper_name={item.dropper_name} />
          </div>
          <div className="text-sm font-semibold text-center flex-grow min-h-[2rem]"> {/* Min-height for name, allow growing */}
            {item.dropper_name}
          </div>
        </div>

        <div className="flex flex-col items-center w-24 flex-shrink-0 flex-grow"> {/* Item container with fixed width, prevent shrinking, allow growing */}
          <div className="w-16 h-16 flex items-center justify-center border border-gray-200 rounded-md mb-1 flex-shrink-0"> {/* Fixed size image wrapper, prevent shrinking */}
            <ItemImageDisplay itemid={item.itemid} item_name={item.item_name} />
          </div>
          <div className="text-sm font-semibold text-center flex-grow min-h-[2rem]"> {/* Min-height for name, allow growing */}
            {item.item_name}
          </div>
        </div>
      </div>
      <p className="text-sm text-gray-600 text-center mt-4">Chance: {item.chance}</p>
      <p className="text-sm text-gray-600 text-center">Quantity: {item.minimum_quantity} - {item.maximum_quantity}</p>
    </div>
  );
}
