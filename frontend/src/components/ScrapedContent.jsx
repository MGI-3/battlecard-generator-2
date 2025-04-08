import React from 'react';

const ScrapedContent = ({ content }) => {
  if (!content) {
    return null;
  }

  return (
    <div className="mt-4">
      <h2 className="text-xl font-bold mb-2">Scraped Content:</h2>
      <div className="p-4 border rounded bg-gray-50 max-h-[600px] overflow-y-auto">
        <pre className="whitespace-pre-wrap">{content}</pre>
      </div>
    </div>
  );
};

export default ScrapedContent;