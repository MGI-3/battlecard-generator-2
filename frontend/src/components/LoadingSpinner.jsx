import React from 'react';

const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center py-12">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    <p className="mt-4 text-gray-600 text-sm md:text-base">
      Analyzing website content...
    </p>
  </div>
);

export default LoadingSpinner;