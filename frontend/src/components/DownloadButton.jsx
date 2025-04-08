// import React from 'react';
// import { pdf } from '@react-pdf/renderer';
// import { Download } from 'lucide-react';
// import BattlecardPDF from './BattlecardPDF';

// const DownloadButton = ({ battlecards }) => {
//   const handleDownload = async () => {
//     try {
//       const blob = await pdf(
//         <BattlecardPDF battlecards={battlecards} />
//       ).toBlob();
//       const url = URL.createObjectURL(blob);
//       const link = document.createElement('a');
//       link.href = url;
//       link.download = `battlecards-${new Date().toISOString().split('T')[0]}.pdf`;
//       document.body.appendChild(link);
//       link.click();
//       document.body.removeChild(link);
//       URL.revokeObjectURL(url);
//     } catch (error) {
//       console.error('Error generating PDF:', error);
//     }
//   };

//   return (
//     <button
//       onClick={handleDownload}
//       className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg
//         hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300
//         transition-colors text-sm md:text-base font-medium shadow-sm"
//     >
//       <Download className="h-5 w-5 mr-2" />
//       Download PDF
//     </button>
//   );
// };

// export default DownloadButton;


// import React from 'react';
// import { pdf } from '@react-pdf/renderer';
// import { Download } from 'lucide-react';
// import BattlecardPDF from './BattlecardPDF';

// const DownloadButton = ({ battlecards, onDownload }) => {
//   const handleDownload = async () => {
//     try {
//       const blob = await pdf(
//         <BattlecardPDF battlecards={battlecards} />
//       ).toBlob();
//       const url = URL.createObjectURL(blob);
//       const link = document.createElement('a');
//       link.href = url;
//       link.download = `battlecards-${new Date().toISOString().split('T')[0]}.pdf`;
//       document.body.appendChild(link);
//       link.click();
//       document.body.removeChild(link);
//       URL.revokeObjectURL(url);
      
//       // Call the onDownload callback if provided
//       if (onDownload) {
//         onDownload();
//       }
//     } catch (error) {
//       console.error('Error generating PDF:', error);
//     }
//   };

//   return (
//     <button
//       onClick={handleDownload}
//       className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg
//         hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300
//         transition-colors text-sm md:text-base font-medium shadow-sm"
//     >
//       <Download className="h-5 w-5 mr-2" />
//       Download PDF
//     </button>
//   );
// };

// export default DownloadButton;



import React, { useState } from 'react';
import { pdf } from '@react-pdf/renderer';
import { Download } from 'lucide-react';
import BattlecardPDF from './BattlecardPDF';

const DownloadButton = ({ battlecards, companyName = "" }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  
  const handleDownload = async () => {
    try {
      setIsGenerating(true);
      
      // Create the PDF document
      const blob = await pdf(
        <BattlecardPDF 
          battlecards={battlecards} 
          companyName={companyName || "Battlecard Generator"} 
        />
      ).toBlob();
      
      // Create a URL for the blob
      const url = URL.createObjectURL(blob);
      
      // Create a link and trigger the download
      const link = document.createElement('a');
      link.href = url;
      link.download = `battlecards-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <button
      onClick={handleDownload}
      disabled={isGenerating || !battlecards || battlecards.length === 0}
      className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg
        hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300
        transition-colors text-sm md:text-base font-medium shadow-sm
        disabled:bg-gray-400 disabled:cursor-not-allowed"
    >
      {isGenerating ? (
        <>
          <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
          Generating PDF...
        </>
      ) : (
        <>
          <Download className="h-5 w-5 mr-2" />
          Download PDF
        </>
      )}
    </button>
  );
};

export default DownloadButton;