interface DropData {
  id: string;
  dropperid: number;
  itemid: number;
  minimum_quantity: number;
  maximum_quantity: number;
  questid: number;
  chance: number;
}

interface ItemDetailProps {
  item: DropData;
  onBack: () => void;
}

export default function ItemDetail({ item, onBack }: ItemDetailProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg text-black">
      <button
        className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md mb-4 hover:bg-gray-300"
        onClick={onBack}
      >
        &larr; Back to Search
      </button>
      <div className="flex items-center mb-4">
        {/* Placeholder for image - you might want to fetch MapleStory item images based on itemid */}
        <img src="/next.svg" alt={`Item ID: ${item.itemid}`} className="w-24 h-24 mr-4" />
        <div>
          <h2 className="text-3xl font-bold mb-1">Item ID: {item.itemid}</h2>
          <p className="text-gray-600 text-lg">Dropper ID: {item.dropperid}</p>
        </div>
      </div>
      <p className="text-gray-700 mb-2">Dropper ID: {item.dropperid}</p>
      <p className="text-gray-700 mb-2">Item ID: {item.itemid}</p>
      <p className="text-gray-700 mb-2">Chance: {item.chance}</p>
      <p className="text-gray-700 mb-2">Minimum Quantity: {item.minimum_quantity}</p>
      <p className="text-gray-700 mb-2">Maximum Quantity: {item.maximum_quantity}</p>
      <p className="text-gray-700 mb-2">Questid: {item.questid}</p>
      <p className="text-gray-700">ID: {item.id}</p>
    </div>
  );
}