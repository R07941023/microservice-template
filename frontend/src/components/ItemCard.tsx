import Image from 'next/image'
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
      {/* Placeholder for image - you might want to fetch MapleStory item images based on itemid */}
      <Image
        src="/next.svg"
        alt={`Item ID: ${item.itemid}`}
        width={64}
        height={64}
        style={{ height: 64 }} 
        className="mx-auto mb-2"
      />
      <h3 className="text-lg font-semibold text-center">Mob Name: {item.dropper_name}</h3>
      <p className="text-sm text-gray-600 text-center">Item Name: {item.item_name}</p>
      <p className="text-sm text-gray-600 text-center">Chance: {item.chance}</p>
      <p className="text-sm text-gray-600 text-center">Quantity: {item.minimum_quantity} - {item.maximum_quantity}</p>
    </div>
  );
}