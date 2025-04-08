import React, { useState } from 'react';
import { Search, Upload, AlertCircle } from 'lucide-react';

const ScraperForm = ({ onScrapedData, setLoading, setError }) => {
  const [url, setUrl] = useState('');
  const [isValidUrl, setIsValidUrl] = useState(true);
  const [files, setFiles] = useState([]);
  const [activeTab, setActiveTab] = useState('url'); // 'url' or 'file'

  const validateUrl = (input) => {
    try {
      new URL(input);
      return true;
    } catch {
      return false;
    }
  };

  const handleUrlChange = (e) => {
    const input = e.target.value;
    setUrl(input);
    setIsValidUrl(input === '' || validateUrl(input));
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (activeTab === 'url') {
      if (!validateUrl(url)) {
        setError('Please enter a valid URL');
        return;
      }
    } else {
      if (files.length === 0) {
        setError('Please select at least one file');
        return;
      }
    }
    
    setLoading(true);
    setError('');

    try {
      let response;
      
      if (activeTab === 'url') {
        // Website scraping
        response = await fetch('/api/scrape', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        });
      } else {
        // File upload
        const formData = new FormData();
        files.forEach(file => {
          formData.append('files', file);
        });
        
        response = await fetch('/api/process-documents', {
          method: 'POST',
          body: formData
        });
      }
      
      if (!response.ok) {
        throw new Error(activeTab === 'url' ? 'Failed to scrape website' : 'Failed to process documents');
      }
      
      const data = await response.json();
      onScrapedData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="mb-6 flex border-b border-gray-200">
        <button
          type="button"
          className={`px-4 py-2 font-medium text-sm ${
            activeTab === 'url' 
              ? 'text-blue-600 border-b-2 border-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('url')}
        >
          Website URL
        </button>
        <button
          type="button"
          className={`px-4 py-2 font-medium text-sm ${
            activeTab === 'file' 
              ? 'text-blue-600 border-b-2 border-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('file')}
        >
          Upload Documents
        </button>
      </div>

      <div className="space-y-4">
        {activeTab === 'url' ? (
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="url"
              value={url}
              onChange={handleUrlChange}
              placeholder="Enter website URL (e.g., https://example.com)"
              className={`w-full pl-10 pr-4 py-3 rounded-lg border ${
                isValidUrl ? 'border-gray-300 focus:border-blue-500' : 'border-red-500'
              } focus:outline-none focus:ring-2 ${
                isValidUrl ? 'focus:ring-blue-200' : 'focus:ring-red-200'
              } transition-colors text-sm md:text-base`}
            />
            {!isValidUrl && (
              <div className="flex items-center text-red-500 text-sm mt-1">
                <AlertCircle className="h-4 w-4 mr-2" />
                <span>Please enter a valid URL</span>
              </div>
            )}
          </div>
        ) : (
          <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-6">
            <div className="flex flex-col items-center justify-center space-y-4">
              <Upload className="h-10 w-10 text-gray-400" />
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  Drag & drop files or click to upload
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Supports PDF, DOCX, TXT, and other text-based documents
                </p>
              </div>
              <input
                type="file"
                multiple
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                style={{ height: 'calc(100% - 2rem)' }} // Prevent overlap with button
              />
            </div>
            {files.length > 0 && (
              <div className="mt-4">
                <p className="font-medium text-sm text-gray-700 mb-2">Selected files:</p>
                <ul className="text-sm text-gray-600 space-y-1">
                  {files.map((file, i) => (
                    <li key={i} className="flex items-center">
                      <span className="truncate">{file.name}</span>
                      <span className="ml-2 text-gray-400">({(file.size / 1024).toFixed(1)} KB)</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="mt-6"> {/* Added container for button */}
          <button
            type="submit"
            disabled={(activeTab === 'url' && (!isValidUrl || !url)) || (activeTab === 'file' && files.length === 0)}
            className="w-full md:w-auto px-6 py-3 bg-blue-600 text-white rounded-lg
              hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300
              disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors
              text-sm md:text-base font-medium"
          >
            Generate Battlecards
          </button>
        </div>
      </div>
    </form>
  );
};

export default ScraperForm;
