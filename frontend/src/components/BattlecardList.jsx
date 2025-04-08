import React from 'react';
import Battlecard from './Battlecard';
import DownloadButton from './DownloadButton';

const BattlecardList = ({ battlecards }) => {
  if (!battlecards || battlecards.length === 0) {
    return null;
  }

  return (
    <div className="mt-8 space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl md:text-2xl font-bold text-gray-800">
          Generated Battlecards ({battlecards.length})
        </h2>
        <DownloadButton battlecards={battlecards} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {battlecards.map((battlecard, index) => (
          <Battlecard key={index} battlecard={battlecard} />
        ))}
      </div>
    </div>
  );
};

export default BattlecardList;
